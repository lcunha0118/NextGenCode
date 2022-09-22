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
  

def plot_Results(Model,Output_config,Total,Title_str,output_figure):        
    
   
    Total_Acum=Total.cumsum(axis= 0)
 

    
    if("CFE" in Model) |  ("Topmodel" in Model):
        num_subplots = 3 #If plotting cumulative precipitation/soil moisture, use 3 subplots (flow, cumulative rain, soil moisture)
        plt.rcParams["figure.figsize"] = (13,15)
        fig, ax_compare = plt.subplots(num_subplots, 1) #Create the plot for this zone
        #ax_compare[0].set_title('Cumulative Precipitation')
        ax_compare[0].plot (Total.index,Total_Acum['Obs_Q'], label = 'Accum Obs runoff (m)', color= 'b') #Plot obs data on comparison figure
        ax_compare[0].plot (Total.index,Total_Acum[Output_config.loc['Q_OUT'].output_var_names], label = 'Accum Sim runoff (m)', color= 'r') #Plot obs data on comparison figure
        ax_compare[0].plot (Total.index,Total_Acum[Output_config.loc['Rainfall'].output_var_names], label = 'Accum rainfall in model (m)', color= 'k') #Plot obs data on comparison figure
        ax_compare[0].plot (Total.index,Total_Acum['Rainfall_from_forcing'],label = 'Accum rainfall in forcing (m)', color= 'g') #Plot obs data on comparison figure
        ax_compare[0].legend(loc='upper left')
        ax_compare[0].set_xlabel ('Date'); 
        ax_compare[0].set_ylabel('Cumulative rain/runoff (m)')
        
        ax_compare[1].plot(Total.index,Total['Obs_Q'], label = 'Obs runoff (m/h)', color= 'b') #plot the rainfall from the mixed AORC/other precip array used to generate the equations
        ax_compare[1].plot (Total.index,Total[Output_config.loc['Q_OUT'].output_var_names], label = 'Sim runoff (m/h)', color= 'r') #Plot obs data on comparison figure
        ax_compare[1].legend(loc='upper left')
        ax_compare[1].set_xlabel ('Date'); ax_compare[1].set_ylabel('Runoff (m/h)')
        
        To_plot=Output_config[Output_config['Plot'] == 1]
        
        for i in range(0,len(To_plot)):
            ax_compare[2].plot (Total.index,Total_Acum[To_plot.iloc[i].output_var_names], label = To_plot.iloc[i].output_var_names) #Plot obs data on comparison figure
        ax_compare[2].legend(loc='upper left')
        ax_compare[2].set_xlabel ('Date'); ax_compare[2].set_ylabel('All Components (m)' )
        ax_compare[0].set_title(Model+' - ' + min_date.strftime ('%Y-%m-%d %H:%M:%S')+' through '+ max_date.strftime ('%Y-%m-%d %H:%M:%S'))
        fig.savefig(output_figure, bbox_inches='tight')               
    

# for example
Hyd_folder="/home/west/Projects/CAMELS/PerBasin4/"
CAMELS_list_516="/home/west/Projects/CAMELS/camels_basin_list_516.txt"
Output_ngen="Output_ngen2"
CAMELS_list_516="/home/west/Projects/CAMELS/Working_CAMELS.txt"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id': str})
CAMELS_516=CAMELS_516.set_index(['hru_id'])   

General_Dir="/data_CAMELS/"
ID_format="id"
Models=["NOAH_CFE","NOAH_Topmodel"]
Config_file=[Hyd_folder+"CFE_output_var_config.csv",Hyd_folder+"Topmodel_output_var_config.csv"]

Models=["NOAH_CFE"]
Config_file=[Hyd_folder+"CFE_output_var_config.csv"]
Spinnup=365 # in Days

len(CAMELS_516)


CAMELS_516=pd.read_csv("/home/west/Projects/CAMELS/HUC01_camels_calib.txt",header=None,dtype=str)
for i in range (0,len(CAMELS_516)):   
    for j in range (0,len(Models)):   

        hru_id=CAMELS_516.iloc[i][0]
        print (hru_id)
         
        # Read output config file
        Output_config=pd.read_csv(Config_file[j],index_col=0)
        outfolder=Hyd_folder+"/"+hru_id+"/"
        catchment_file=Hyd_folder+"/data_CAMELS/"+hru_id+'/hydrofabrics/spatial/catchment_data.geojson'    
        
        Results=Hyd_folder+"data_CAMELS/"+hru_id+"/"+Output_ngen+"/"+Models[j]+"/"
        Obs_Q_file=Hyd_folder+"data_CAMELS/"+hru_id+"/Validation/usgs_hourly_flow_2007-2019_"+hru_id+".csv"
        Obs_Q_cms=pd.read_csv(Obs_Q_file,parse_dates=True,index_col=1)
        Obs_Q_cms=Obs_Q_cms['q_cms']
        
        min_date=Obs_Q_cms.index.min()
        max_date=Obs_Q_cms.index.max()
    
        
        zones = gp.GeoDataFrame.from_file(catchment_file)
        total_area=zones['area_sqkm'].sum()
        Obs_q_mh=(Obs_Q_cms/total_area)*3.6/1000.
        Rainfall_from_forcing_mmh=pd.DataFrame()

        for index,row in zones.iterrows():
            catstr=row[0]     
            # READING FORCING Files- Check it is input correctly
            Focing_file=Hyd_folder+"data_CAMELS/"+hru_id+"/forcing/"+catstr+".csv"
            Obs_RR_mmh_Temp=pd.read_csv(Focing_file,parse_dates=True,index_col=0)
            Obs_RR_mmh_Temp=Obs_RR_mmh_Temp['RAINRATE'].to_frame()*3600.
            Obs_RR_mmh_Temp=Obs_RR_mmh_Temp.rename(columns={Obs_RR_mmh_Temp.columns[0]:catstr})        
            Rainfall_from_forcing_mmh=pd.concat([Rainfall_from_forcing_mmh,Obs_RR_mmh_Temp],axis=1)
    
            # READING OUTPUT CFE
            Cat_out_file=Results+catstr+".csv"
            Cat_out=pd.read_csv(Cat_out_file,parse_dates=True,index_col=1)
            if(index==0):
                Total_out=Cat_out.copy()
            else:
                Total_out=Total_out+Cat_out
            
            min_date=Cat_out.index.min()+timedelta(days=Spinnup)


        
        Total_out=Total_out/float(len(zones))
        Rainfall_from_forcing_mmh_ave=Rainfall_from_forcing_mmh.sum(axis=1)/float(len(zones))/1000.
        Rainfall_from_forcing_mmh_ave=Rainfall_from_forcing_mmh_ave.to_frame()
        Rainfall_from_forcing_mmh_ave=Rainfall_from_forcing_mmh_ave.rename(columns={Rainfall_from_forcing_mmh_ave.columns[0]:"Rainfall_from_forcing"})  
        
        Obs_q_mh=Obs_q_mh.to_frame()
        Obs_q_mh=Obs_q_mh.rename(columns={Obs_q_mh.columns[0]:"Obs_Q"})  
        if("Topmodel" in Models[j]):
            Total_out['land_surface_water__domain_evaporation_volume_flux']=Total_out['land_surface_water__domain_time_integral_of_evaporation_volume_flux'].diff()
            Total_out['land_surface_water__domain_overland_flow_volume_flux']=Total_out['land_surface_water__domain_time_integral_of_overland_flow_volume_flux'].diff()
        
        UnitConversion=Output_config[Output_config['Conversion'] != 1]
        
        for unitc in range(0,len(UnitConversion)):
            Total_out[UnitConversion['output_var_names'].iloc[unitc]]=Total_out[UnitConversion['output_var_names'].iloc[unitc]]*UnitConversion['Conversion'].iloc[unitc]
        
        # This needs to be modified when a config file is created for NOAH
        if(Models[j]=="NOAH") :
            Total_out=Total_out*3600
            Total_out['ETRAN']=Total_out['ETRAN']/1000.      
            Total_out['QSEVA']=Total_out['QSEVA']/1000.    
            Total_out['EVAPOTRANS']=Total_out['EVAPOTRANS']/1000.  
        #Total_out_top_mod=Total_out_top.copy()
        #Total_out_top_mod['RAIN_RATE']=Total_out_mod['RAIN_RATE']/1000.    
        
        Total=pd.concat([Total_out,Rainfall_from_forcing_mmh_ave],axis=1)
        Total=pd.concat([Total,Obs_q_mh],axis=1)
        #min_date_plot=min_date
        min_date_plot=datetime(2007,10,1,0,0)
        #min_date_plot=datetime(2012,10,1,0,0)
        max_date_plot=datetime(2013,10,1,0,0)
        Total=Total[(Total.index>=min_date_plot) & (Total.index<=max_date_plot)]
        output_figure=Results+"Runoff_figure"+min_date_plot.strftime ('%Y-%m')+"_"+max_date_plot.strftime ('%Y-%m')+".png"
        Title_str=Models[j]+' - ' + min_date_plot.strftime ('%Y-%m-%d %H:%M:%S')+' through '+ max_date_plot.strftime ('%Y-%m-%d %H:%M:%S')
        plot_Results(Models[j],Output_config,Total,Title_str,output_figure)
        
        # result = pd.merge(Obs_q_mh_plot.to_frame(), Total_out_plot[q_var[j]].to_frame(),left_index=True,right_index=True)
        # plt.plot(result['q_cms'],result[q_var[j]], 'o')
            
#Obs_Q_cms=pd.read_csv("/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/01350140/cat-1.csv",parse_dates=True,index_col=0)        