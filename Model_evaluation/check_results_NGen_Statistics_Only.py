#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 09:20:43 2021

@author: west
"""
import pandas as pd
import geopandas as gp
from datetime import datetime,timedelta
import os
import matplotlib.pyplot as plt
import glob
import geopandas as gpd
import seaborn as sns
import numpy as np
import sys
sys.path.append("/home/west/git_repositories/ngen-cal-master/ngen-cal/python/ngen_cal/")
import objectives as OB  
from hydrotools.metrics import metrics
from hydrotools.nwis_client.iv import IVDataService
from shapely.geometry import Point
from scipy import interpolate

import geoplot as gplt
import geoplot.crs as gcrs

def Generate_plotstats_multiple_model_results(Stats,Title_str,output_figure, Label):     
    import seaborn as sns    
    import matplotlib.pyplot as plt      
    #num_subplots = 1 #If plotting cumulative precipitation/soil moisture, use 3 subplots (flow, cumulative rain, soil moisture)
    Stats_M=pd.melt(Stats.dropna())
    sns.set_style("whitegrid")
    fig, ax = plt.subplots() #Create the plot for this zone
    fig.set_size_inches(6,4)
    

    #plt.rcParams["figure.figsize"] = (5,10)
    sns.boxplot(x='variable',y="value",data=Stats_M,ax=ax,color='silver',width=0.5)
    ax.set_xlabel ('Model',fontsize=12)
    ax.set_ylabel(Label)
    ax.set_xticklabels(Stats_M['variable'].unique(),rotation=90)
    ax.yaxis.grid(True)
    #ax.set_yscale("log")
    ax.set_title(Title_str)
    fig.savefig(output_figure, bbox_inches='tight',dpi=300)        
    plt.close(fig)

def plot_dist(CAMELS_516,Verification_values,Verification_title,Opt_type,output_figure):
    import seaborn as sns    
    import matplotlib.pyplot as plt 
    colors = {'Noah_CFE':'tab:blue', 'Noah_CFE_X':'tab:green', 'Noah_Topmodel':'tab:red', 'H':'tab:purple', 'NWM_2.1':'tab:brown', 'J':'tab:pink'}

    columns=Verification_values[0].columns
    f, axes = plt.subplots(figsize=(12, 7), ncols=2, nrows=2)
    
    for i in range(0,4):
        if(i==0): ax1=0;ax2=0;xtext=0.05;ytext=0.5
        if(i==1): ax1=0;ax2=1;xtext=0.5;ytext=0.5
        if(i==2): ax1=1;ax2=0;xtext=0.05;ytext=0.1
        if(i==3): ax1=1;ax2=1;xtext=0.5;ytext=0.1  
    
        
        #Hyd_Sig.plot(ax=axes[0][0],column='Min_col',cmap='RdYlBu',categorical=True,legend="True" )
        
        Hyd_Sig = Verification_values[i].replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        if(Opt_type[i]=="Min"): 
            Hyd_Sig = Hyd_Sig.assign(Min_val = Hyd_Sig.min(axis=1), Min_col=Hyd_Sig.idxmin(axis=1))
            Hyd_Sig['Inv_Min_val']=Hyd_Sig['Min_val'].max()-Hyd_Sig['Min_val']
            scale='Min_val'
            hue='Min_col'
        if(Opt_type[i]=="Max"): 
            Hyd_Sig = Hyd_Sig.assign(Max_val = Hyd_Sig.max(axis=1), Max_col=Hyd_Sig.idxmax(axis=1))
            scale='Max_val'
            hue='Max_col'
        Hyd_Sig = pd.concat([CAMELS_516,Hyd_Sig],axis=1).dropna()
        
        for j in range (0,len(columns)):
            col=columns[j]
            
            maxS=Hyd_Sig[col].max()
            minS=Hyd_Sig[col].min()
            if(Verification_title[i]=='Hydrological Signature'):
                maxS=4
                minS=-1      
                bins=np.arange(-1,6,1)
            if(Verification_title[i]=='KGE'):
               maxS=1
               minS=-1
               bins=np.arange(-1,1,0.25)
            if(Verification_title[i]=='Normalized Nash'):
               maxS=1
               minS=0
               bins=np.arange(0,1,0.1)

            if(Verification_title[i]=='Threat Score (Q> Q95 percentile)'):
              maxS=1
              minS=0
              bins=np.arange(0,1,0.1)            
            #plt.figtext(xtext,ytext,Verification_title[i],fontsize=14)
            Hyd_Sig[col][Hyd_Sig[col]<minS]=minS
            Hyd_Sig[col][Hyd_Sig[col]>maxS]=maxS
            sns.distplot(Hyd_Sig[col],ax=axes[ax1][ax2],bins=bins,label=col)
            
            
        sns.distplot(Hyd_Sig[scale],ax=axes[ax1][ax2],bins=bins,label="Best Model")    
        axes[ax1][ax2].set_xlim([minS, maxS])
        #plt.figtext(xtext,ytext,Verification_title[i],fontsize=14)
        axes[ax1][ax2].legend(loc='best')
        axes[ax1][ax2].set_xlabel(Verification_title[i])
 
        

    f.savefig(output_figure, bbox_inches='tight',dpi=300)
    

def plot_map(CAMELS_516,Verification_values,Verification_title,Opt_type,output_figure):
    import seaborn as sns    
    import matplotlib.pyplot as plt 
    colors = {'Noah_CFE':'tab:blue', 'Noah_CFE_X':'tab:green', 'Noah_Topmodel':'tab:red', 'H':'tab:purple', 'NWM_2.1':'tab:brown', 'J':'tab:pink'}

    columns=Verification_values[0].columns
    f, axes = plt.subplots(figsize=(12, 7), ncols=2, nrows=2)
    
    for i in range(0,4):
        if(i==0): ax1=0;ax2=0;xtext=0.05;ytext=0.5
        if(i==1): ax1=0;ax2=1;xtext=0.5;ytext=0.5
        if(i==2): ax1=1;ax2=0;xtext=0.05;ytext=0.1
        if(i==3): ax1=1;ax2=1;xtext=0.5;ytext=0.1  
    
        us_states.plot(ax=axes[ax1][ax2],color='lightgray')
        #Hyd_Sig.plot(ax=axes[0][0],column='Min_col',cmap='RdYlBu',categorical=True,legend="True" )
        
        Hyd_Sig = Verification_values[i].replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        if(Opt_type[i]=="Min"): 
            Hyd_Sig = Hyd_Sig.assign(Min_val = Hyd_Sig.min(axis=1), Min_col=Hyd_Sig.idxmin(axis=1))
            Hyd_Sig['Inv_Min_val']=Hyd_Sig['Min_val'].max()-Hyd_Sig['Min_val']
            scale='Inv_Min_val'
            hue='Min_col'
        if(Opt_type[i]=="Max"): 
            Hyd_Sig = Hyd_Sig.assign(Max_val = Hyd_Sig.max(axis=1), Max_col=Hyd_Sig.idxmax(axis=1))
            scale='Max_val'
            hue='Max_col'
        Hyd_Sig = pd.concat([CAMELS_516,Hyd_Sig],axis=1).dropna()
        
        gplt.pointplot(Hyd_Sig,hue=hue,
                       cmap='viridis',
                       edgecolor="gray",linewidth=0.2,
                       scale=scale,limits=(3, 5),
                       legend=True,
                       ax=axes[ax1][ax2]);                
        axes[ax1][ax2].set_xlim(([-125,-65]))
        axes[ax1][ax2].set_ylim(([20,50]))
        #plt.title(Verification_title[i])
        plt.figtext(xtext,ytext,Verification_title[i],fontsize=14)

    f.savefig(output_figure, bbox_inches='tight',dpi=300)
    
    
    for j in range(0,len(columns)):
        f, axes = plt.subplots(figsize=(12, 7), ncols=2, nrows=2)
        for i in range(0,4):
            if(i==0): ax1=0;ax2=0;xtext=0.05;ytext=0.5
            if(i==1): ax1=0;ax2=1;xtext=0.5;ytext=0.5
            if(i==2): ax1=1;ax2=0;xtext=0.05;ytext=0.1
            if(i==3): ax1=1;ax2=1;xtext=0.5;ytext=0.1  
        
            us_states.plot(ax=axes[ax1][ax2],color='lightgray')
            #Hyd_Sig.plot(ax=axes[0][0],column='Min_col',cmap='RdYlBu',categorical=True,legend="True" )
            
            Hyd_Sig = Verification_values[i].replace([np.inf, -np.inf], np.nan).dropna(axis=0)
            Hyd_Sig = pd.concat([CAMELS_516,Hyd_Sig],axis=1).dropna()

            gplt.pointplot(Hyd_Sig,hue=columns[j],
                           cmap='viridis', 
                           edgecolor="gray",linewidth=0.2,
                           legend=True,
                           ax=axes[ax1][ax2]);                
            axes[ax1][ax2].set_xlim(([-125,-65]))
            axes[ax1][ax2].set_ylim(([20,50]))
            #plt.title(Verification_title[i])
            plt.figtext(xtext,ytext,Verification_title[i],fontsize=14)
        
        f.savefig(output_figure.replace(".png",columns[j]+"_values.png"), bbox_inches='tight',dpi=300) 
    #plt.close()  
    f, axes = plt.subplots(figsize=(12, 7), ncols=2, nrows=2)
    
    for i in range(0,4):
        if(i==0): ax1=0;ax2=0;xtext=0.05;ytext=0.5
        if(i==1): ax1=0;ax2=1;xtext=0.5;ytext=0.5
        if(i==2): ax1=1;ax2=0;xtext=0.05;ytext=0.1
        if(i==3): ax1=1;ax2=1;xtext=0.5;ytext=0.1  
        
        if(Opt_type[i]=="Min"): 
            Verification_values[i]['Best']=Verification_values[i].min(axis=1)  
        if(Opt_type[i]=="Max"): 
            Verification_values[i]['Best']=Verification_values[i].max(axis=1)  
        Stats_M=pd.melt(Verification_values[i].dropna())
        sns.boxplot(x='variable',y="value",data=Stats_M,ax=axes[ax1][ax2],color='silver',width=0.5)
        axes[ax1][ax2].set_xlabel ('Model',fontsize=12)
        axes[ax1][ax2].set_ylabel(Verification_title[i])
        axes[ax1][ax2].set_xticklabels(Stats_M['variable'].unique(),rotation=90)
        axes[ax1][ax2].yaxis.grid(True)               
        if(Verification_title[i]=="Hydrological Signature"):
                axes[ax1][ax2].set_ylim(([0,5]))
        if(Verification_title[i]=="KGE"):
                axes[ax1][ax2].set_ylim(([-2,1]))
        if(ax1==0): 
            axes[ax1][ax2].set_xticks([])
            axes[ax1][ax2].set(xlabel=None)
        #axes[ax1][ax2].set_ylim(([20,50]))
        #plt.title(Verification_title[i])
        #plt.figtext(xtext,ytext,Verification_title[i],fontsize=14)

        
    f.savefig(output_figure.replace(".png","_boxplot.png"), bbox_inches='tight',dpi=300)   


def plot_map_variable(CAMELS_516,NNashDf,Columns,output_figure):
    import math as m
    nrow=m.ceil(len(Columns)/2)
    f, axes = plt.subplots(figsize=(12, 7), ncols=2, nrows=nrow)
    for i in range(0,len(Columns)):
        if(i==0): ax1=0;ax2=0;xtext=0.05;ytext=0.5
        if(i==1): ax1=0;ax2=1;xtext=0.5;ytext=0.5
        if(i==2): ax1=1;ax2=0;xtext=0.05;ytext=0.1
        if(i==3): ax1=1;ax2=1;xtext=0.5;ytext=0.1  
        if(i==4): ax1=2;ax2=0;xtext=0.5;ytext=0.1  
        if(i==5): ax1=2;ax2=1;xtext=0.5;ytext=0.1 
    
        us_states.plot(ax=axes[ax1][ax2],color='lightgray')
        #Hyd_Sig.plot(ax=axes[0][0],column='Min_col',cmap='RdYlBu',categorical=True,legend="True" )
        
        Hyd_Sig = NNashDf.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        Hyd_Sig = pd.concat([CAMELS_516,Hyd_Sig],axis=1).dropna()
        NNashDf
        gplt.pointplot(Hyd_Sig,hue=Columns[i],
                       cmap='viridis', vmin=0,vmax=1,
                       edgecolor="gray",linewidth=0.2,
                       legend=True,
                       ax=axes[ax1][ax2]);                
        axes[ax1][ax2].set_xlim(([-125,-65]))
        axes[ax1][ax2].set_ylim(([20,50]))
        #plt.title(Verification_title[i])
        plt.figtext(xtext,ytext,Columns[i],fontsize=14)
    f.savefig(output_figure, bbox_inches='tight',dpi=300)         
# for example
Hyd_folder="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"
Output_folder="/media/west/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Results/"

Output_ngen=["Output_ngen_03292022"]
#Output_ngen=["Output_ngen_03092022"]
Output_Wanru="/media/west/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Results/Model_output_daily/"
if not os.path.exists(Output_Wanru): os.mkdir(Output_Wanru)  
Output_Rachel="/media/west/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Results/Output4Rachel/"
if not os.path.exists(Output_Rachel): os.mkdir(Output_Rachel)  


CAMELS_list_516="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/CAMELS_v3_complete.csv"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id_CAMELS': str})
CAMELS_516=CAMELS_516.set_index(['hru_id_CAMELS'])
#CAMELS_516=CAMELS_516[CAMELS_516['SA_analysis']==1]

CAMELS_516['Lat']=-9.0
CAMELS_516['Long']=-9.0
for i in range (0,len(CAMELS_516)):  
    hru_id=CAMELS_516.index[i]
    Folder=CAMELS_516.iloc[i]['Folder_CAMELS']
    Hydrofabrics=Hyd_folder+"/"+Folder+"/spatial/catchment_data.geojson"
    basin = gpd.read_file(Hydrofabrics) 
    basin_id=basin.sort_values(by="area_sqkm",ascending=True).iloc[0].id
    nexus_id=basin.sort_values(by="area_sqkm",ascending=True).iloc[0].toid
    CAMELS_516.at[hru_id,'Lat']=basin.sort_values(by="area_sqkm",ascending=True).iloc[0].geometry.centroid.y
    CAMELS_516.at[hru_id,'Long']=basin.sort_values(by="area_sqkm",ascending=True).iloc[0].geometry.centroid.x      

CAMELS_516.to_csv(Output_Wanru+"Evaluation_Camels_list.csv")
Generate_plots_flag=0

#CAMELS_516=CAMELS_516.drop(['11176400'])

General_Dir="/data_CAMELS/"
ID_format="id"
Models=["NOAH_CFE","NOAH_CFE_KNash","NOAH_CFE_klNash","NOAH_CFE_GWIC8","PET_1_CFE","PET_2_CFE","PET_3_CFE","PET_4_CFE","PET_5_CFE","NOAH_CFE_X","PET_1_CFE_X","PET_2_CFE_X","PET_3_CFE_X","PET_4_CFE_X","PET_5_CFE_X","NOAH_Topmodel","PET_1_Topmodel","PET_2_Topmodel","PET_3_Topmodel","PET_4_Topmodel","PET_5_Topmodel"]
#Models=["NOAH_CFE"]
Models=["NOAH_CFE","NOAH_CFE_X","NOAH_Topmodel"]

#Models=["NOAH_CFE","PET_1_CFE","PET_2_CFE","PET_3_CFE","PET_4_CFE","PET_5_CFE"]
#Models=["NOAH_Topmodel"]
#Models=["NOAH_CFE"]
#Models=["NOAH_Topmodel"]
Config_file=[Hyd_folder+"CFE_output_var_config.csv",Hyd_folder+"Topmodel_output_var_config.csv"]
Models_run=pd.DataFrame()

# Models=["NOAH_CFE"]
# Config_file=[Hyd_folder+"CFE_output_var_config.csv"]
Spinnup=365 # in Days
#min_date_plot=min_date
min_date_plot=datetime(2007,10,1,0,0)
#min_date_plot=datetime(2012,10,1,0,0)
max_date_plot=datetime(2013,10,1,0,0)

#CAMELS_516=pd.read_csv("/home/west/Projects/CAMELS/HUC01_camels_calib.txt",header=None,dtype=str)
sns.set_style("whitegrid")
Problem_simulations=[]

Models_w_NWM=Models.copy()
Models_w_NWM.append("NWM_2.1")

NashDf=pd.DataFrame(index=CAMELS_516.index,columns=Models_w_NWM)
NNashDf=pd.DataFrame(index=CAMELS_516.index,columns=Models_w_NWM)
mean_biasDf=pd.DataFrame(index=CAMELS_516.index,columns=Models_w_NWM)
mean_absolute_errorDf=pd.DataFrame(index=CAMELS_516.index,columns=Models_w_NWM)
RMSEDf=pd.DataFrame(index=CAMELS_516.index,columns=Models_w_NWM)
NRMSEDf=pd.DataFrame(index=CAMELS_516.index,columns=Models_w_NWM)
KGEDf=pd.DataFrame(index=CAMELS_516.index,columns=Models_w_NWM)
TSDf=pd.DataFrame(index=CAMELS_516.index,columns=Models_w_NWM)
ratio_slope_FDCDf=pd.DataFrame(index=CAMELS_516.index,columns=Models_w_NWM)
ratio_mean_annual_RDf=pd.DataFrame(index=CAMELS_516.index,columns=Models_w_NWM)
ratio_average_annual_RCDf=pd.DataFrame(index=CAMELS_516.index,columns=Models_w_NWM)
ratio_differenceDf=pd.DataFrame(index=CAMELS_516.index,columns=Models_w_NWM)

for i in range (0,len(CAMELS_516)):   
    hru_id=CAMELS_516.index[i]
    Folder=CAMELS_516.iloc[i]['Folder_CAMELS']
    
  
    Daily_Q_all_Model=pd.DataFrame()  
    
    for j in range (0,len(Models)):  
        print("Basin " + str(i) + " / " + str(len(CAMELS_516))+ " hru_id " + hru_id + " Model " + Models[j] )
        for z in range(0,len(Output_ngen)):
            
            Total_file=Output_Rachel+hru_id+"_"+Models[j]+".csv"
            if (os.path.isfile(Total_file)):     
                print (Models[j] + " " + hru_id + " " + str(i))
                # Read output config file
                if("CFE" in Models[j]):  file=Config_file[0]
                else:  file=Config_file[1]
                Output_config=pd.read_csv(file,index_col=0)
                outfolder=Hyd_folder+"/"+Folder+"/"
                catchment_file=Hyd_folder+"/"+Folder+'/spatial/catchment_data.geojson'    
                zones = gp.GeoDataFrame.from_file(catchment_file) 
                
                Results=Output_folder+"/"+Folder+"/"+Output_ngen[z]+"/"+Models[j]+"/"
                # all_results=glob.glob(Results+"cat*.csv")
                # flag_empty=0
                # for f in all_results:
                #     if(os.path.getsize(f)==0):
                #         flag_empty=1
                # flag_wrong=0 
                
                # if(len(all_results)>len(zones)):
                #     Cat_out_file=f
                #     Cat_out=pd.read_csv(Cat_out_file,parse_dates=True,index_col=1)
                #     nvar=0
                #     if(len(all_results)>1):
                #         for ff in range(0,len(Output_config)):
                #             if(not Output_config.output_var_names[ff] in Cat_out.columns):
                #                 print ("did not find variable " + Output_config.output_var_names[ff])
                #                 nvar=nvar+1
                #         if(nvar>3):  
                #             flag_wrong=1 
                            
                #     if(Cat_out.index.max()<max_date_plot):
                #         flag_wrong=1 
                #         print ("Short period of record")
                # if(flag_empty==1) | (flag_wrong==1):
                #     for f in os.listdir(Results):
                #        os.remove(os.path.join(Results,f))                        
                

                Total_file=Output_Rachel+hru_id+"_"+Models[j]+".csv"
                Total=pd.read_csv(Total_file,parse_dates=True,index_col=0)
                #Total[['Rainfall_from_forcing',Output_config.loc['Surface water flux'].output_var_names,Output_config.loc['Q_OUT'].output_var_names,'Q_NWM_2.1','Obs_Q']].to_csv()
                
                Var_name_out=Output_config.loc['Q_OUT'].output_var_names
                Total_daily=Total.resample('D').apply(lambda x: np.sum(x.values))
                Total_dailyNoNAN=Total_daily.dropna()
                Total_year=Total_dailyNoNAN.resample("AS-OCT").sum()
                
                
                len(Total_daily)
                len_sim=len(Total_daily[Var_name_out].dropna())
                len_obs=len(Total_daily['Obs_Q'].dropna())
                
                if(len(Total_dailyNoNAN)>0.6*len(Total_daily)):
                    Nash=OB.nash_sutcliffe(Total_dailyNoNAN[Var_name_out],Total_dailyNoNAN['Obs_Q'])
                    NNash=OB.normalized_nash_sutcliffe(Total_dailyNoNAN[Var_name_out],Total_dailyNoNAN['Obs_Q'])
                    mean_bias=OB.mean_bias(Total_dailyNoNAN[Var_name_out],Total_dailyNoNAN['Obs_Q'])
                    mean_absolute_error=OB.mean_absolute_error(Total_dailyNoNAN[Var_name_out],Total_dailyNoNAN['Obs_Q'])
                    RMSE=OB.RMSE(Total_dailyNoNAN[Var_name_out],Total_dailyNoNAN['Obs_Q'])
                    NRMSE=OB.NRMSE(Total_dailyNoNAN[Var_name_out],Total_dailyNoNAN['Obs_Q'])
                    KGE=metrics.kling_gupta_efficiency(Total_dailyNoNAN['Obs_Q'].values,Total_dailyNoNAN[Var_name_out].values)
                    Q95=Total_dailyNoNAN['Obs_Q'].quantile(0.95)
                    Total_dailyNoNAN.at[:,'simulated_flood'] = Total_dailyNoNAN[Var_name_out] >= Q95
                    Total_dailyNoNAN.at[:,'observed_flood'] = Total_dailyNoNAN['Obs_Q'] >= Q95
                    contingency_table=metrics.compute_contingency_table(Total_dailyNoNAN['observed_flood'],Total_dailyNoNAN['simulated_flood'])
                    TS=metrics.threat_score(contingency_table)                     
                    RC_Obs=  Total_year['Obs_Q']/Total_year['Rainfall_from_forcing']   
                    RC_Sim=  Total_year[Var_name_out]/Total_year['Rainfall_from_forcing']  
                    ratio_average_annual_RC=RC_Sim.mean()/RC_Obs.mean()
                    ratio_mean_annual_R=Total_year[Var_name_out].mean()/Total_year['Obs_Q'].mean()
                    
                    Total_dailyNoNAN['excedanceP'] = np.arange(1,len(Total_dailyNoNAN)+1)/(len(Total_dailyNoNAN)+1)
                    Q50_sim=Total_dailyNoNAN['Q_NWM_2.1'].quantile(0.5)
                    SlopeInterval = [20,80]
                    f = interpolate.interp1d(Total_dailyNoNAN['excedanceP'].values, Total_dailyNoNAN[Var_name_out].sort_values(ascending=False))
                    Q_atGivenSlope=Q_atGivenSlope = [f(SlopeInterval[0]/100.0), f(SlopeInterval[1]/100.0)]
                    slope_FDC_sim = -1.0*(Q_atGivenSlope[1] - Q_atGivenSlope[0]) / Q50_sim*(SlopeInterval[1]-SlopeInterval[0])
                    
                    Q50_obs=Total_dailyNoNAN['Q_NWM_2.1'].quantile(0.5)
                    f = interpolate.interp1d(Total_dailyNoNAN['excedanceP'].values, Total_dailyNoNAN['Obs_Q'].sort_values(ascending=False))
                    Q_atGivenSlope=Q_atGivenSlope = [f(SlopeInterval[0]/100.0), f(SlopeInterval[1]/100.0)]
                    slope_FDC_obs = -1.0*(Q_atGivenSlope[1] - Q_atGivenSlope[0]) / Q50_obs*(SlopeInterval[1]-SlopeInterval[0])                    
                    ratio_slope_FDC=slope_FDC_sim/slope_FDC_obs
                    
                    NashDf.at[hru_id,Models[j]]=Nash
                    NNashDf.at[hru_id,Models[j]]=NNash
                    mean_biasDf.at[hru_id,Models[j]]=mean_bias
                    mean_absolute_errorDf.at[hru_id,Models[j]]=mean_absolute_error
                    RMSEDf.at[hru_id,Models[j]]=RMSE
                    NRMSEDf.at[hru_id,Models[j]]=NRMSE
                    KGEDf.at[hru_id,Models[j]]=KGE
                    TSDf.at[hru_id,Models[j]]=TS
                    
                    ratio_slope_FDCDf.at[hru_id,Models[j]]=ratio_slope_FDC
                    ratio_mean_annual_RDf.at[hru_id,Models[j]]=ratio_mean_annual_R
                    ratio_average_annual_RCDf.at[hru_id,Models[j]]=ratio_average_annual_RC
                    ratio_differenceDf.at[hru_id,Models[j]]=abs(1-ratio_average_annual_RC)+abs(1-ratio_slope_FDC)+abs(1-ratio_mean_annual_R)
                    
                    Temp=pd.DataFrame([[hru_id,Models[j],CAMELS_516.iloc[i]['frac_snow'],1]],columns=['hru_id','Models','frac_snow','Done'])
                    Models_run=Models_run.append(Temp)
                    
                    if(j==0):
                        Nash_NWM=OB.nash_sutcliffe(Total_dailyNoNAN['Q_NWM_2.1'],Total_dailyNoNAN['Obs_Q'])
                        NNash=OB.normalized_nash_sutcliffe(Total_dailyNoNAN['Q_NWM_2.1'],Total_dailyNoNAN['Obs_Q'])
                        mean_bias=OB.mean_bias(Total_dailyNoNAN['Q_NWM_2.1'],Total_dailyNoNAN['Obs_Q'])
                        mean_absolute_error=OB.mean_absolute_error(Total_dailyNoNAN['Q_NWM_2.1'],Total_dailyNoNAN['Obs_Q'])
                        RMSE=OB.RMSE(Total_dailyNoNAN['Q_NWM_2.1'],Total_dailyNoNAN['Obs_Q'])
                        NRMSE=OB.NRMSE(Total_dailyNoNAN['Q_NWM_2.1'],Total_dailyNoNAN['Obs_Q']) 
                        KGE=metrics.kling_gupta_efficiency(Total_dailyNoNAN['Q_NWM_2.1'],Total_dailyNoNAN[Var_name_out].values)
                        Q95=Total_dailyNoNAN['Obs_Q'].quantile(0.95)
                        Total_dailyNoNAN.at[:,'simulated_flood'] = Total_dailyNoNAN['Q_NWM_2.1'] >= Q95
                        Total_dailyNoNAN.at[:,'observed_flood'] = Total_dailyNoNAN['Obs_Q'] >= Q95
                        contingency_table=metrics.compute_contingency_table(Total_dailyNoNAN['observed_flood'],Total_dailyNoNAN['simulated_flood'])
                        TS=metrics.threat_score(contingency_table)                      
                         
                        RC_Sim=  Total_year['Q_NWM_2.1']/Total_year['Rainfall_from_forcing']  
                        ratio_average_annual_RC=RC_Sim.mean()/RC_Obs.mean()
                        ratio_mean_annual_R=Total_year['Q_NWM_2.1'].mean()/Total_year['Obs_Q'].mean()
                         
                         
                        Q50_sim=Total_dailyNoNAN['Q_NWM_2.1'].quantile(0.5)
                        SlopeInterval = [20,80]
                        f = interpolate.interp1d(Total_dailyNoNAN['excedanceP'].values, Total_dailyNoNAN['Q_NWM_2.1'].sort_values(ascending=False))
                        Q_atGivenSlope=Q_atGivenSlope = [f(SlopeInterval[0]/100.0), f(SlopeInterval[1]/100.0)]
                        slope_FDC_sim = -1.0*(Q_atGivenSlope[1] - Q_atGivenSlope[0]) / Q50_sim*(SlopeInterval[1]-SlopeInterval[0])
                         
                        ratio_slope_FDC=slope_FDC_sim/slope_FDC_obs                       
                        
                        NashDf.at[hru_id,"NWM_2.1"]=Nash
                        NNashDf.at[hru_id,"NWM_2.1"]=NNash
                        mean_biasDf.at[hru_id,"NWM_2.1"]=mean_bias
                        mean_absolute_errorDf.at[hru_id,"NWM_2.1"]=mean_absolute_error
                        RMSEDf.at[hru_id,"NWM_2.1"]=RMSE
                        NRMSEDf.at[hru_id,"NWM_2.1"]=NRMSE
                        KGEDf.at[hru_id,"NWM_2.1"]=KGE
                        TSDf.at[hru_id,"NWM_2.1"]=TS

                        ratio_slope_FDCDf.at[hru_id,"NWM_2.1"]=ratio_slope_FDC
                        ratio_mean_annual_RDf.at[hru_id,"NWM_2.1"]=ratio_mean_annual_R
                        ratio_average_annual_RCDf.at[hru_id,"NWM_2.1"]=ratio_average_annual_RC
                        ratio_differenceDf.at[hru_id,"NWM_2.1"]=abs(1-ratio_average_annual_RC)+abs(1-ratio_slope_FDC)+abs(1-ratio_mean_annual_R)
                else:
                    print ("All NAN : " + Results)
                     
Models_run.to_csv(Output_Wanru+"Summary_run_March_report.csv")   
NextGen=['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel']
All=['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','NWM_2.1']


NNashDf['Best_Nextgen']=NNashDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel']].max(axis=1)                   
NNashDf['Best_all']=NNashDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','NWM_2.1']].max(axis=1)    

NRMSEDf['Best_Nextgen']=NRMSEDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel']].min(axis=1)                   
NRMSEDf['Best_all']=NRMSEDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','NWM_2.1']].min(axis=1)  

mean_biasDf['Best_Nextgen']=mean_biasDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel']].min(axis=1)                   
mean_biasDf['Best_all']=mean_biasDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','NWM_2.1']].min(axis=1)    

mean_absolute_errorDf['Best_Nextgen']=mean_absolute_errorDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel']].min(axis=1)                   
mean_absolute_errorDf['Best_all']=mean_absolute_errorDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','NWM_2.1']].min(axis=1)    

TSDf['Best_Nextgen']=TSDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel']].max(axis=1)                   
TSDf['Best_all']=TSDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','NWM_2.1']].max(axis=1)    

KGEDf['Best_Nextgen']=KGEDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel']].max(axis=1)                   
KGEDf['Best_all']=KGEDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','NWM_2.1']].max(axis=1)  

ratio_differenceDf['Best_Nextgen']=ratio_differenceDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel']].min(axis=1)                   
ratio_differenceDf['Best_all']=ratio_differenceDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','NWM_2.1']].min(axis=1)  

KGEDf['Best_Nextgen']=KGEDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel']].max(axis=1)                   
KGEDf['Best_all']=KGEDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','NWM_2.1']].max(axis=1)  

NashDf.to_csv(Output_Wanru+"Nash_all_models.csv")  
NNashDf.to_csv(Output_Wanru+"NNash_all_models.csv")  
mean_biasDf.to_csv(Output_Wanru+"mean_bias_all_models.csv") 
mean_absolute_errorDf.to_csv(Output_Wanru+"mean_absolute_error_all_models.csv") 
RMSEDf.to_csv(Output_Wanru+"RMSE_all_models.csv")  
NRMSEDf.to_csv(Output_Wanru+"NRMSE_all_models.csv")  
KGEDf.to_csv(Output_Wanru+"KGE_all_models.csv") 
TSDf.to_csv(Output_Wanru+"TS_all_models.csv") 
#Nash=pd.concat([Nash,CAMELS_516],axis=1)            
    #Obs_Q_cms=pd.read_csv("/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/01350140/cat-1.csv",parse_dates=True,index_col=0)        


Title_str="Number of basins " + str(len(NNashDf.dropna()))
Label="Normalized NSE"
output_figure=Output_folder+Label.replace(" ","_")+"WithNWM.png"
Generate_plotstats_multiple_model_results(NNashDf,Title_str,output_figure,Label)
output_figure=Output_folder+Label.replace(" ","_")+".png"
Generate_plotstats_multiple_model_results(NNashDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','Best_Nextgen']],Title_str,output_figure,Label)  


Label="Normalized RMSE"
#NRMSEDf[NRMSEDf>10]=10
output_figure=Output_folder+Label.replace(" ","_")+"WithNWM.png"
Generate_plotstats_multiple_model_results(NRMSEDf,Title_str,output_figure,Label)
output_figure=Output_folder+Label.replace(" ","_")+".png"
Generate_plotstats_multiple_model_results(NRMSEDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','Best_Nextgen']],Title_str,output_figure,Label)  


Label="Mean bias"
output_figure=Output_folder+Label.replace(" ","_")+"WithNWM.png"
Generate_plotstats_multiple_model_results(mean_biasDf,Title_str,output_figure,Label)
output_figure=Output_folder+Label.replace(" ","_")+".png"
Generate_plotstats_multiple_model_results(mean_biasDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','Best_Nextgen']],Title_str,output_figure,Label)  


Label="Mean absolute error"
#mean_absolute_errorDf[mean_absolute_errorDf>0.02]=0.02
#mean_absolute_errorDf[mean_absolute_errorDf<-0.02]=-0.02
output_figure=Output_folder+Label.replace(" ","_")+"WithNWM.png"
Generate_plotstats_multiple_model_results(mean_absolute_errorDf,Title_str,output_figure,Label)
output_figure=Output_folder+Label.replace(" ","_")+".png"
Generate_plotstats_multiple_model_results(mean_absolute_errorDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','Best_Nextgen']],Title_str,output_figure,Label)  


Label="Threat Score"
output_figure=Output_folder+Label.replace(" ","_")+"WithNWM.png"
Generate_plotstats_multiple_model_results(TSDf,Title_str,output_figure,Label)
output_figure=Output_folder+Label.replace(" ","_")+".png"
Generate_plotstats_multiple_model_results(TSDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','Best_Nextgen']],Title_str,output_figure,Label)  

Label="KGE"
#KGEDf[KGEDf<-5]=-5
output_figure=Output_folder+Label.replace(" ","_")+"WithNWM.png"
Generate_plotstats_multiple_model_results(KGEDf,Title_str,output_figure,Label)
output_figure=Output_folder+Label.replace(" ","_")+".png"
Generate_plotstats_multiple_model_results(KGEDf[['NOAH_CFE','NOAH_CFE_X','NOAH_Topmodel','Best_Nextgen']],Title_str,output_figure,Label)  


points = []
for lon, lat in zip(CAMELS_516["Long"], CAMELS_516["Lat"]):
    points.append(Point(lon, lat))



us_states_file="/home/west/us_states.json"
us_states = gpd.read_file(us_states_file)
us_states=us_states[us_states.name != "Alaska"]
us_states_bounds = us_states.geometry.total_bounds
contiguous_usa = gpd.read_file(gplt.datasets.get_path('contiguous_usa'))
CAMELS_516["geometry"] = points
CAMELS_516 = gpd.GeoDataFrame(CAMELS_516)

Verification_values=[ratio_differenceDf[NextGen],TSDf[NextGen],NNashDf[NextGen],KGEDf[NextGen]]
Verification_title=["Hydrological Signature","Threat Score (Q> Q95 percentile)","Normalized Nash","KGE"]
Opt_type=["Min","Max","Max","Max"]
output_figure=Output_folder+"Type1_best_model_Nextgen"+".png"
plot_map(CAMELS_516,Verification_values,Verification_title,Opt_type,output_figure)

Verification_values=[ratio_differenceDf[NextGen],TSDf[NextGen],NNashDf[NextGen],KGEDf[NextGen]]
output_figure=Output_folder+"Dist_best_model_Nextgen"+".png"
plot_dist(CAMELS_516,Verification_values,Verification_title,Opt_type,output_figure)

Verification_values=[ratio_differenceDf[All],TSDf[All],NNashDf[All],KGEDf[All]]
output_figure=Output_folder+"Type1_best_model_WithNWM"+".png"
plot_map(CAMELS_516,Verification_values,Verification_title,Opt_type,output_figure)

Verification_values=[ratio_differenceDf[All],TSDf[All],NNashDf[All],KGEDf[All]]
output_figure=Output_folder+"Dist_best_model_WithNWM"+".png"
plot_dist(CAMELS_516,Verification_values,Verification_title,Opt_type,output_figure)



# output_figure=Output_folder+"Nash_Nextgen"+".png"
# plot_map_variable(CAMELS_516,NNashDf,NextGen,output_figure)
# plot_map_variable(CAMELS_516,NNashDf[NextGen],"Normalized Nash",output_figure)

# edgecolor="black",
# legend=True,
# cmap='RdYlBu',
# legend_var="scale",
# legend_kwargs={"loc":"best",
#                 "fontsize": "large",
#                 "title_fontsize":"large"},
# alpha=0.8,ax=axes[0][0]
# us_map_axes = geoplot.polyplot(us_states, facecolor="white", figsize=(10, 10));

# geoplot.pointplot(matrix,
#                   hue="Min_col",
#                   scale="p_seasonality",
#                   scheme="Quantiles", ## mapclassify.Quantiles(us_states_pop["2018 Population"], k=5) will give same results.
#                   ax=us_map_axes,
#                   cmap='RdYlBu',
#                   edgecolor="black",
#                   legend=True,
#                   legend_var="scale",
#                   legend_kwargs={"loc":"best",
#                                   "fontsize": "large",
#                                   "title":"Seasonality",
#                                   "title_fontsize":"large"},
#                   limits=(5, 20),
#                   alpha=0.8

#                   );

# plt.title("US State's 2018 Population", fontdict={"fontsize": 15}, pad=15);
# interval_value = {'KGE': [-np.inf, 0, 0.3, 0.6, 0.75, 1],'NNSEWt': [0, 0.2, 0.5, 0.6, 0.75, 1], 'PBIAS': [-np.inf, -50, -20, -10, -5, 0],
#                   'RMSE': [-np.inf, -0.8, -0.6, -0.4, -0.2, 0],'HSEG_FDC': [-np.inf, -50, -20, -10, -5, 0],
#                   'pk_error_perc_median': [-np.inf, -60, -40, -20, -10, 0],'pk_timing_error_mean_h': [-np.inf, -36, -24, -12, -6, 0]}
# rank_category=[1, 2, 3, 4, 5]



# # calculate rank
# df_rank = pd.DataFrame()
# for catid in catids:
#     for row in df.itertuples():
#         dict1 = {'catid': catid, 'model': row.model}
#         for x in all_metrics:
#             if x in part_metrics:
#                 value = -abs(df.loc[row.Index, x])
#             else:
#                 value = df.loc[row.Index, x]
#             z = pd.cut(np.array([value]), bins=interval_value[x], include_lowest=False if x=='KGE' else True)
#             bl = z.categories.map(lambda xx: value in xx)
#             rank_value = [r for r, b in zip(rank_category, bl) if b][0]
#             dict1.update({x: rank_value}) 
#         df_rank = df_rank.append([dict1], ignore_index=True)

# print(df_rank)