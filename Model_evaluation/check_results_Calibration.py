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
import pyreadr
import rpy2.robjects as robjects


def NSEs_noZeros(mod, obs, w=0.5, p=1):

    import math as m
    # Calculate NSE and logNSE in here, so we are positive we are using the exact same estimates for zeros
    S = mod.copy()   # Specify similuations
    O = obs.copy()   # Specify observations
    # Get sample size of station data (how many observed and PRMS simulated streamflow data)
    n = len(O)
    
    ############## NSE ##############
    # Nash-Sutcliffe Efficiency (NSE)                              # Xia: n-1 instead of n in denomitor as in standard NSE on 20200616
    NSE  = 1.-((1./n)*sum(m.pow(S-O,2)))/((1/(n-1))*sum((m.math(O-m.mean(O),2))))   # Barber et al. 2019 eqn. 8b
    # LogNSE  = 1.-((1./n)*sum(m.pow(m.log(S)-log(O),2)))/((1/(n-1))*sum((m.math(log(O)-m.mean(m.log(O)),2))))   # Barber et al. 2019 eqn. 8b
    # wtNSE = m.pow((m.pow(w,p) * m.pow(NSE,p) + m.pow(w,p) * m.pow(LogNSE,p)),(1/p))
    # alpha = S.std()/O.std()
    # beta = m.mean(S)/m.mean(O)
    #r <- cor(S,O)   # Calculate correlation coefficient (rho) between simulations and observations
    #KGE = 1-sqrt((beta-1)^2+(alpha-1)^2+(r-1)^2)   # Barber et al. 2019 eqn 14
    
    #NSEs = [NSE, LogNSE, wtNSE, KGE]

    return NSE
  

def plot_Results(Model,Total_out_plot,Obs_q_mh_plot,Obs_RR_mh_ave_plot,Title_str,output_figure):        
    Total_out_acum=Total_out_plot.cumsum(axis= 0)
    Obs_q_m=Obs_q_mh_plot.cumsum(axis= 0)
    Obs_RR_m_ave=Obs_RR_mh_ave_plot.cumsum(axis= 0)

    
    if("CFE" in Model) |  ("Topmodel" in Model):
        num_subplots = 3 #If plotting cumulative precipitation/soil moisture, use 3 subplots (flow, cumulative rain, soil moisture)
        plt.rcParams["figure.figsize"] = (13,15)
        fig, ax_compare = plt.subplots(num_subplots, 1) #Create the plot for this zone
        #ax_compare[0].set_title('Cumulative Precipitation')
        ax_compare[0].plot (Obs_q_m.index,Obs_q_m, label = 'Accum Obs runoff (m)', color= 'b') #Plot obs data on comparison figure
        ax_compare[0].plot (Total_out_acum.index,Total_out_acum[q_var[j]], label = 'Accum Sim runoff (m)', color= 'r') #Plot obs data on comparison figure
        ax_compare[0].plot (Total_out_acum.index,Total_out_acum[rain_var[j]], label = 'Accum rainfall in model (m)', color= 'k') #Plot obs data on comparison figure
        ax_compare[0].plot (Obs_RR_m_ave, label = 'Accum rainfall in forcing (m)', color= 'g') #Plot obs data on comparison figure
        ax_compare[0].legend(loc='upper left')
        ax_compare[0].set_xlabel ('Date'); ax_compare[1].set_ylabel('Cumulative rain/runoff (m)')
        
        ax_compare[1].plot(Obs_q_mh_plot.index,Obs_q_mh_plot, label = 'Obs runoff (m/h)', color= 'b') #plot the rainfall from the mixed AORC/other precip array used to generate the equations
        ax_compare[1].plot (Total_out_plot.index,Total_out_plot[q_var[j]], label = 'Sim runoff (m/h)', color= 'r') #Plot obs data on comparison figure
        ax_compare[1].legend(loc='upper left')
        ax_compare[1].set_xlabel ('Date'); ax_compare[1].set_ylabel('Runoff (m/s)')
        if("NOAH" in Model):    
             
            # obs_soilDeficit= max_historical_SM040.loc[zone_id]['MaxSM']-SoilMoistureAll['0-40_'+str(zone_id)].loc[event_start:event_end].dropna() #subtract the NLDAS/NWM soil moisture (in) from the maximum historical soil moisture
            ax_compare[2].plot (Total_out_acum.index,Total_out_acum[q_var[j]], label = 'Total runoff (m)', color= 'r') #Plot obs data on comparison figure
            ax_compare[2].plot (Total_out_acum.index,Total_out_acum['NASH_LATERAL_RUNOFF'], label = 'NASH_LATERAL_RUNOFF', color= 'g') #Plot obs data on comparison figure
            ax_compare[2].plot (Total_out_acum.index,Total_out_acum['DEEP_GW_TO_CHANNEL_FLUX'], label = 'DEEP_GW_TO_CHANNEL_FLUX', color= 'm') #Plot obs data on comparison figure
            ax_compare[2].legend(loc='upper left')
            ax_compare[2].set_xlabel ('Date'); ax_compare[2].set_ylabel('Runoff Components (m)' )
        else:
            # obs_soilDeficit= max_historical_SM040.loc[zone_id]['MaxSM']-SoilMoistureAll['0-40_'+str(zone_id)].loc[event_start:event_end].dropna() #subtract the NLDAS/NWM soil moisture (in) from the maximum historical soil moisture
            ax_compare[2].plot (Total_out_acum.index,Total_out_acum[q_var[j]], label = 'Total runoff (m)', color= 'r') #Plot obs data on comparison figure
            ax_compare[2].plot (Total_out_acum.index,Total_out_acum['land_surface_water__domain_time_integral_of_evaporation_volume_flux'], label = 'land_surface_water__domain_time_integral_of_evaporation_volume_flux', color= 'g') #Plot obs data on comparison figure
            ax_compare[2].plot (Total_out_acum.index,Total_out_acum['land_surface_water__baseflow_volume_flux'], label = 'land_surface_water__baseflow_volume_flux', color= 'm') #Plot obs data on comparison figure
            ax_compare[2].legend(loc='upper left')
            ax_compare[2].set_xlabel ('Date'); ax_compare[2].set_ylabel('Runoff Components (m)' )
        ax_compare[0].set_title('CFE - ' + min_date.strftime ('%Y-%m-%d %H:%M:%S')+' through '+ max_date.strftime ('%Y-%m-%d %H:%M:%S'))
        fig.savefig(output_figure, bbox_inches='tight')               

    if(Models[j]=="NOAH"): 
        num_subplots = 1 #If plotting cumulative precipitation/soil moisture, use 3 subplots (flow, cumulative rain, soil moisture)
        plt.rcParams["figure.figsize"] = (13,4)
        fig, ax_compare = plt.subplots(num_subplots, 1) #Create the plot for this zone
        #ax_compare[0].set_title('Cumulative Precipitation')
        ax_compare.plot (Obs_q_m.index,Obs_q_m, label = 'Accum Obs runoff (m)', color= 'b') #Plot obs data on comparison figure
        #ax_compare[0].plot (Total_out_acum.index,Total_out_acum[q_var[j]], label = 'Accum Sim runoff (m)', color= 'r') #Plot obs data on comparison figure
        ax_compare.plot (Total_out_acum.index,Total_out_acum['QINSUR'], label = 'QINSUR (m)', color= 'k') #Plot obs data on comparison figure
        ax_compare.plot (Total_out_acum.index,Total_out_acum['ETRAN'], label = 'Accum ETRAN (m)', color= 'y') #Plot obs data on comparison figure
        ax_compare.plot (Total_out_acum.index,Total_out_acum['QSEVA'], label = 'Accum QSEVA (m)', color= 'c') #Plot obs data on comparison figure
        ax_compare.plot (Total_out_acum.index,Total_out_acum['EVAPOTRANS'], label = 'Accum EVAPOTRANS (m)', color= 'c') #Plot obs data on comparison figure
        #EVPT=Total_out_acum['QSEVA']+Total_out_acum['ETRAN']
        #ax_compare.plot (EVPT, label = 'Accum QSEVA + ETRAN(m)', color= 'm') #Plot obs data on comparison figure
        ax_compare.plot (Obs_RR_m_ave, label = 'Accum raifall in forcing (m)', color= 'g') #Plot obs data on comparison figure
        ax_compare.legend(loc='upper left')
        ax_compare.set_xlabel ('Date'); ax_compare.set_ylabel('Cumulative Obs/Sim runoff (m)')
        
        ax_compare.set_title(Models[j]+' - ' + min_date.strftime ('%Y-%m-%d %H:%M:%S')+' through '+ max_date.strftime ('%Y-%m-%d %H:%M:%S'))
        fig.savefig(output_figure, bbox_inches='tight')     

# for example
Hyd_folder="/home/west/Projects/CAMELS/PerBasin4/"
CAMELS_list_516="/home/west/Projects/CAMELS/camels_basin_list_516.txt"

CAMELS_list_516="/home/west/Projects/CAMELS/Working_CAMELS.txt"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id': str})
CAMELS_516=CAMELS_516.set_index(['hru_id'])   

General_Dir="/data_CAMELS/"
ID_format="id"
Models=["NOAH_CFE_calib"]
q_var=["Q_OUT","Qout",""]
rain_var=["RAIN_RATE","atmosphere_water__domain_time_integral_of_rainfall_volume_flux",""]
Calib_folder="calib_out_CFE"

len(CAMELS_516)

# Models=["NOAH_Topmodel"]
# q_var=["Qout"]
# Rain_var=["atmosphere_water__domain_time_integral_of_rainfall_volume_flux",""]

# Models=["NOAH_CFE"]
# q_var=["Q_OUT"]
# Rain_var=["RAIN_RATE",""]

# Models=["NOAH"]
# q_var=[""]
# Rain_var=[""]

CAMELS_516=['01350140']
for i in range (0,len(CAMELS_516)):   
    for j in range (0,len(Models)):   
        hru_id='01350140'
        #hru_id=CAMELS_516.index[i]
        print (hru_id)
         
        outfolder=Hyd_folder+"/"+hru_id+"/"
        catchment_file=Hyd_folder+"/"+hru_id+'/spatial/catchment_data.geojson'    
        
       
        Obs_Q_file=Hyd_folder+"data_CAMELS/"+hru_id+"/Validation/usgs_hourly_flow_2007-2019_"+hru_id+".csv"
        Obs_Q_cms=pd.read_csv(Obs_Q_file,parse_dates=True,index_col=1)
        Obs_Q_cms=Obs_Q_cms['q_cms']
        min_date=Obs_Q_cms.index.min()
        max_date=Obs_Q_cms.index.max()
    
        Results_file=Hyd_folder+"data_CAMELS/"+hru_id+"/" +Calib_folder+"/proj_data.Rdata"
        Output_cal=robjects.r['load'](Results_file)
        Sim_300=robjects.r['outDt.300']
        Simout_file=Hyd_folder+"data_CAMELS/"+hru_id+"/" +Calib_folder+"/tnx_output.csv"
        Sim_300.to_csvfile(Simout_file)
        sim_df=pd.read_csv(Simout_file,parse_dates=True,index_col=1)

        kge(evaluation, simulation, return_all=False)
        
        zones = gp.GeoDataFrame.from_file(catchment_file)
        total_area=zones['area_sqkm'].sum()
        Obs_q_mh=(Obs_Q_cms/total_area)*3.6/1000.
        Sim_q_mmh=pd.DataFrame()
        Sim_RR_mmh=pd.DataFrame()
        Obs_RR_mmh=pd.DataFrame()
        Sim_q_mmh_top=pd.DataFrame()
        Sim_RR_mmh_top=pd.DataFrame()   
        for index,row in zones.iterrows():
            catstr=row[0]     
            # READING FORCING
            Focing_file=Hyd_folder+"data_CAMELS/"+hru_id+"/forcing/"+catstr+".csv"
            Obs_RR_mmh_Temp=pd.read_csv(Focing_file,parse_dates=True,index_col=0)
            Obs_RR_mmh_Temp=Obs_RR_mmh_Temp['RAINRATE'].to_frame()*3600.
            Obs_RR_mmh_Temp=Obs_RR_mmh_Temp.rename(columns={Obs_RR_mmh_Temp.columns[0]:catstr})        
            Obs_RR_mmh=pd.concat([Obs_RR_mmh,Obs_RR_mmh_Temp],axis=1)
    
            # READING OUTPUT CFE
            Cat_out_file=Results+catstr+".csv"
            Cat_out=pd.read_csv(Cat_out_file,parse_dates=True,index_col=1)
            if(index==0):
                Total_out=Cat_out.copy()
            else:
                Total_out=Total_out+Cat_out
            
            min_date=max(Obs_Q_cms.index.min(),Cat_out.index.min()+timedelta(days=365))

            if(Models[j]=="NOAH_CFE") | (Models[j]=="NOAH_Topmodel") | (Models[j]=="CFE"):
               
                Sim_q_mmh_Temp=Cat_out[q_var[j]].to_frame()
                Sim_q_mmh_Temp=Sim_q_mmh_Temp.rename(columns={Sim_q_mmh_Temp.columns[0]:catstr})        
                Sim_q_mmh=pd.concat([Sim_q_mmh,Sim_q_mmh_Temp],axis=1)
                Sim_RR_mmh_Temp=Cat_out[rain_var[j]].to_frame()
                Sim_RR_mmh_Temp=Sim_RR_mmh_Temp.rename(columns={Sim_RR_mmh_Temp.columns[0]:catstr})        
                Sim_RR_mmh=pd.concat([Sim_RR_mmh,Sim_RR_mmh_Temp],axis=1)       
            
        # for index,row in zones.iterrows():
        #     nexstr=row[2]   
    
        #     # READING OUTPUT CFE
        #     Nex_out_file=Results+nexstr+".csv"
        #     Nex_out=pd.read_csv(Nex_out_file,parse_dates=True,index_col=1)
        #     if(index==0):
        #         Total_out=Nex_out.copy()
        #     else:
        #         Total_out=Total_out+Nex_out
            
        #     min_date=max(Obs_Q_cms.index.min(),Cat_out.index.min()+timedelta(days=365))

        #     if(Models[j]=="NOAH_CFE") | (Models[j]=="NOAH_Topmodel") | (Models[j]=="CFE"):
               
        #         Sim_qnex_mmh_Temp=Nex_out[q_var[j]].to_frame()
        #         Sim_qnex_mmh_Temp=Sim_qnex_mmh_Temp.rename(columns={Sim_qnex_mmh_Temp.columns[0]:catstr})        
        #         Sim_qnex_mmh=pd.concat([Sim_qnex_mmh,Sim_qnex_mmh_Temp],axis=1)

        Obs_RR_mmh=Obs_RR_mmh[(Obs_RR_mmh.index>=min_date) & (Obs_RR_mmh.index<=max_date)]        
        Sim_q_mmh=Sim_q_mmh[(Sim_q_mmh.index>=min_date) & (Sim_q_mmh.index<=max_date)]
        Sim_RR_mmh=Sim_RR_mmh[(Sim_RR_mmh.index>=min_date) & (Sim_RR_mmh.index<=max_date)]
        Total_out=Total_out/float(len(zones))
        Obs_RR_mh_ave=Obs_RR_mmh.sum(axis=1)/float(len(zones))/1000.
        Obs_RR_mh_ave=Obs_RR_mh_ave[(Obs_RR_mh_ave.index>=min_date) & (Obs_RR_mh_ave.index<=max_date)]
        Total_out=Total_out[(Total_out.index>=min_date) & (Total_out.index<=max_date)]
        if(Models[j]=="NOAH_CFE") | (Models[j]=="NOAH_CFENoEVPT") | (Models[j]=="CFE"):
            Total_out['RAIN_RATE']=Total_out['RAIN_RATE']/1000.

        if(Models[j]=="NOAH") :
            Total_out=Total_out*3600
            Total_out['ETRAN']=Total_out['ETRAN']/1000.      
            Total_out['QSEVA']=Total_out['QSEVA']/1000.    
            Total_out['EVAPOTRANS']=Total_out['EVAPOTRANS']/1000.  
        #Total_out_top_mod=Total_out_top.copy()
        #Total_out_top_mod['RAIN_RATE']=Total_out_mod['RAIN_RATE']/1000.    
        
        #min_date_plot=min_date
        min_date_plot=datetime(2012,5,1,0,0)
        max_date_plot=datetime(2012,10,1,0,0)
        Total_out_plot=Total_out[(Total_out.index>=min_date_plot) & (Total_out.index<=max_date_plot)]
        Obs_q_mh_plot=Obs_q_mh[(Obs_q_mh.index>=min_date_plot) & (Obs_q_mh.index<=max_date_plot)]
        
        Obs_RR_mh_ave_plot=Obs_RR_mh_ave[(Obs_RR_mh_ave.index>=min_date_plot) & (Obs_RR_mh_ave.index<=max_date_plot)]
        Title_str=Models[j]+' - ' + min_date_plot.strftime ('%Y-%m-%d %H:%M:%S')+' through '+ max_date_plot.strftime ('%Y-%m-%d %H:%M:%S')
        output_figure=Results+"Runoff_figure"+min_date_plot.strftime ('%Y-%m')+"_"+min_date_plot.strftime ('%Y-%m')+".png"

        plot_Results(Models[j],Total_out_plot,Obs_q_mh_plot,Obs_RR_mh_ave_plot,Title_str,output_figure)
        
        result = pd.merge(Obs_q_mh_plot.to_frame(), Total_out_plot[q_var[j]].to_frame(),left_index=True,right_index=True)
        plt.plot(result['q_cms'],result[q_var[j]], 'o')
            
#Obs_Q_cms=pd.read_csv("/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/01350140/cat-1.csv",parse_dates=True,index_col=0)        