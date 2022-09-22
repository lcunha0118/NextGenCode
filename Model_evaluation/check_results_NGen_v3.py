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
import netCDF4 as nc

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
  
# def generate_hydrograph(Total,Spinnup,str_title,output_figure):       
#     import seaborn as sns
#     import matplotlib.pyplot as plt
#     from datetime import timedelta
    
#     fig,(ax)= plt.subplots(len(Total),1, figsize = (10,2*len(Total)))
#     cmap = sns.color_palette("seismic", as_cmap=True)
#     cmap=cmap.reversed()
#     cmap.set_bad(color='yellow')
#     Spinup_time=Total.index.min()+timedelta(days=Spinnup)
#     for i in range(0,len(Total.columns)):  
#         ax[i].plot(Total[Total.columns[i]])
#         #ax[i].plot([Spinup_time,Spinup_time],[Min_Y,Max_Y],'-')
#         #ax1.plot(param_range_mod['for_cat'],'o',color='gray'
#         y_label=Total.columns[i]      
#         ax[i].set(ylabel=y_label,xlabel="time")  
#         #ax[i].set_ylim([Min_Y,Max_Y])
#         if(i==0): 
#             ax[i].set_title(str_title)
#         if(i<len(Total.columns)-1): 
#             ax[i].axes.xaxis.set_visible(False)
#     fig.savefig(output_figure, bbox_inches='tight')
#     plt.close()     
def plot_Results(Model,Output_config,Total,CAMEL_Daymet_Acum,Title_str,output_figure):        
    
   
    Total_Acum=Total.cumsum(axis= 0)
    CAMEL_Daymet_Acum=CAMEL_Daymet.cumsum(axis= 0)

    
    if("CFE" in Model) |  ("Topmodel" in Model):        
        num_subplots = 3 #If plotting cumulative precipitation/soil moisture, use 3 subplots (flow, cumulative rain, soil moisture)
        plt.rcParams["figure.figsize"] = (8,8)
        fig, ax_compare = plt.subplots(num_subplots, 1) #Create the plot for this zone
        #ax_compare[0].set_title('Cumulative Precipitation')
        ax_compare[0].plot (Total.index,Total_Acum['Obs_Q'], label = 'Accum Obs runoff', color= 'blue') #Plot obs data on comparison figure
        ax_compare[0].plot (Total.index,Total_Acum[Output_config.loc['Q_OUT'].output_var_names], label = 'Accum Sim runoff', color= 'orange') #Plot obs data on comparison figure
        ax_compare[0].plot (Total.index,Total_Acum[Output_config.loc['Rainfall'].output_var_names], label = 'Accum precipitation', color= 'black') #Plot obs data on comparison figure
        ax_compare[0].plot (Total.index,Total_Acum['Rainfall_from_forcing'],label = 'Accum surface water flux', color= 'silver') #Plot obs data on comparison figure
        ax_compare[0].legend(loc='upper left')
        #ax_compare[0].set_xlabel ('Date'); 
        ax_compare[0].set_ylabel('Cumulative rain/runoff (m)')
        ax_compare[1].plot (Total.index,Total[Output_config.loc['Q_OUT'].output_var_names], label = 'Sim runoff', color= 'orange',linewidth=1) #Plot obs data on comparison figure
        ax_compare[1].plot(Total.index,Total['Obs_Q'], label = 'Obs runoff',linewidth=0.5, color= 'blue',alpha=0.8) #plot the rainfall from the mixed AORC/other precip array used to generate the equations
        
        ax_compare[1].legend(loc='upper left')
        #ax_compare[1].set_xlabel ('Date'); 
        ax_compare[1].set_ylabel('Runoff (m/h)')
        
        To_plot=Output_config[Output_config['Plot'] == 1]
        
        for i in range(0,len(To_plot)):
            if(To_plot.iloc[i].output_var_names in Total_Acum.columns):
                #print (To_plot.iloc[i].output_var_names)
                if(To_plot.iloc[i].output_var_units == "m/h"):
                    ax_compare[2].plot (Total.index,Total_Acum[To_plot.iloc[i].output_var_names], label = To_plot.index[i]) #Plot obs data on comparison figure
                    #print(To_plot.index[i] + "Total_acum")
                else:
                    ax_compare[2].plot (Total.index,Total[To_plot.iloc[i].output_var_names], label = To_plot.index[i]) #Plot obs data on comparison figure
                    #print(To_plot.index[i] + "Total")
        #ax_compare[2].plot (CAMEL_Daymet_Acum.index,CAMEL_Daymet_Acum['PET'], label = 'Sim PET-from CAMELS') 
        #ax_compare[2].plot (CAMEL_Daymet_Acum.index,CAMEL_Daymet_Acum['ET'], label = 'Sim ET-from CAMELS') 
        
        ax_compare[2].legend(loc='upper left')
        #ax_compare[2].set_xlabel ('Date'); 
        ax_compare[2].set_ylabel('All Components (m)' )
        #ax_compare[0].set_title(Title_str)
        fig.savefig(output_figure, bbox_inches='tight',dpi=300)               
        plt.close(fig)
def plot_Results_v2(Model,Output_config,Total,CAMEL_Daymet_Acum,NWM_21,Title_str,output_figure):        
    
   
    Total_Acum=Total.cumsum(axis= 0)
    CAMEL_Daymet_Acum=CAMEL_Daymet.cumsum(axis= 0)
    NWM_21_Acum=NWM_21.cumsum(axis= 0)
    CB_color_cycle = ['#377eb8', '#ff7f00', '#4daf4a',
                  '#f781bf', '#a65628', '#984ea3',
                  '#999999', '#e41a1c', '#dede00']
    
    if("CFE" in Model) |  ("Topmodel" in Model):        
        num_subplots = 4 #If plotting cumulative precipitation/soil moisture, use 3 subplots (flow, cumulative rain, soil moisture)
        plt.rcParams["figure.figsize"] = (8,9)
        fig, ax_compare = plt.subplots(num_subplots, 1) #Create the plot for this zone
        #ax_compare[0].set_title('Cumulative Precipitation')
        ax_compare[0].plot (Total.index,Total_Acum[Output_config.loc['Q_OUT'].output_var_names], label = Model, color= 'orange',linewidth=2) #Plot obs data on comparison figure
        ax_compare[0].plot (NWM_21_Acum.index,NWM_21_Acum['flow_cms'], label = 'NWM 2.1 runoff', color= 'forestgreen',linewidth=1.5) #Plot obs data on comparison figure
        ax_compare[0].plot (Total.index,Total_Acum['Obs_Q'], label = 'Obs runoff', color= 'blue',linewidth=1) #Plot obs data on comparison figure
        
        
        ax_compare[0].plot (Total.index,Total_Acum[Output_config.loc['Surface water flux'].output_var_names], label = 'Accum surface water flux', color= 'black') #Plot obs data on comparison figure
        ax_compare[0].plot (Total.index,Total_Acum['Rainfall_from_forcing'],label = 'Precipitation', color= 'silver') #Plot obs data on comparison figure
        ax_compare[0].legend(loc='upper left')
        #ax_compare[0].set_xlabel ('Date'); 
        ax_compare[0].set_ylabel('Cumulative flux (m)')
        
        ax_compare[1].plot(NWM_21.index,NWM_21['flow_cms'], label = 'NWM 2.1',linewidth=1.5, color= 'forestgreen',alpha=0.6) #plot the rainfall from the mixed AORC/other precip array used to generate the equations
        ax_compare[1].plot (Total.index,Total[Output_config.loc['Q_OUT'].output_var_names], label = Model, color= 'orange',linewidth=1) #Plot obs data on comparison figure        
        ax_compare[1].plot(Total.index,Total['Obs_Q'], label = 'Observed',linewidth=0.5, color= 'blue',alpha=0.8) #plot the rainfall from the mixed AORC/other precip array used to generate the equations
                
        
        ax_compare[1].legend(loc='upper left')
        #ax_compare[1].set_xlabel ('Date'); 
        ax_compare[1].set_ylabel('Runoff (m/h)')
        
        To_plot=Output_config[Output_config['Plot'] == 1]
        
        for i in range(0,len(To_plot)):
            if(To_plot.iloc[i].output_var_names in Total_Acum.columns):
                #print (To_plot.iloc[i].output_var_names)
                if(To_plot.iloc[i].output_var_units == "m/h"):
                    ax_compare[2].plot (Total.index,Total_Acum[To_plot.iloc[i].output_var_names], label = To_plot.index[i],color=CB_color_cycle[i]) #Plot obs data on comparison figure
                    #print(To_plot.index[i] + "Total_acum")
                else:
                    ax_compare[2].plot (Total.index,Total[To_plot.iloc[i].output_var_names], label = To_plot.index[i],color=CB_color_cycle[i]) #Plot obs data on comparison figure
                    #print(To_plot.index[i] + "Total")
        #ax_compare[2].plot (CAMEL_Daymet_Acum.index,CAMEL_Daymet_Acum['PET'], label = 'Sim PET-from CAMELS') 
        #ax_compare[2].plot (CAMEL_Daymet_Acum.index,CAMEL_Daymet_Acum['ET'], label = 'Sim ET-from CAMELS') 
        
        ax_compare[2].legend(loc='upper left')
        #ax_compare[2].set_xlabel ('Date'); 
        ax_compare[2].set_ylabel('All Components (m)' )

        To_plot=Output_config[Output_config['Storage'] == 1]
        
        for i in range(0,len(To_plot)):
            if(To_plot.iloc[i].output_var_names in Total_Acum.columns):
                #print (To_plot.iloc[i].output_var_names)
                ax_compare[3].plot (Total.index,Total[To_plot.iloc[i].output_var_names], label = To_plot.index[i]) #Plot obs data on comparison figure
                
        ax_compare[3].legend(loc='upper left')
        #ax_compare[2].set_xlabel ('Date'); 
        ax_compare[3].set_ylabel('Storage/Deficit (m)' )
        #ax_compare[0].set_title(Title_str)
        plt.figtext(0.005,0.75,"(a)",fontsize=14)
        plt.figtext(0.005,0.5,"(b)",fontsize=14)
        plt.figtext(0.005,0.3,"(c)",fontsize=14)
        plt.figtext(0.005,0.1,"(d)",fontsize=14)
        fig.savefig(output_figure, bbox_inches='tight',dpi=300)     
        plt.close(fig)
        
        
def plot_Results_v3(Model,Output_config,Total,CAMEL_Daymet_Acum,NWM_21,Title_str,output_figure):        
    
   
    Total_Acum=Total.cumsum(axis= 0)
    CAMEL_Daymet_Acum=CAMEL_Daymet.cumsum(axis= 0)
    NWM_21_Acum=NWM_21.cumsum(axis= 0)
    CB_color_cycle = ['#377eb8', '#ff7f00', '#4daf4a',
                  '#f781bf', '#a65628', '#984ea3',
                  '#999999', '#e41a1c', '#dede00']
    
    if("CFE" in Model) |  ("Topmodel" in Model):        
        num_subplots = 5 #If plotting cumulative precipitation/soil moisture, use 3 subplots (flow, cumulative rain, soil moisture)
        plt.rcParams["figure.figsize"] = (8,12)
        fig, ax_compare = plt.subplots(num_subplots, 1) #Create the plot for this zone
        #ax_compare[0].set_title('Cumulative Precipitation')
        ax_compare[0].plot (Total.index,Total_Acum[Output_config.loc['Q_OUT'].output_var_names], label = Model, color= 'orange',linewidth=3) #Plot obs data on comparison figure
        ax_compare[0].plot (NWM_21_Acum.index,NWM_21_Acum['flow_cms'], label = 'NWM 2.1 runoff', color= 'forestgreen',linewidth=2) #Plot obs data on comparison figure
        ax_compare[0].plot (Total.index,Total_Acum['Obs_Q'], label = 'Obs runoff', color= 'blue',linewidth=1) #Plot obs data on comparison figure
        
        
        ax_compare[0].plot (Total.index,Total_Acum[Output_config.loc['Surface water flux'].output_var_names], label = 'Accum surface water flux', color= 'black') #Plot obs data on comparison figure
        ax_compare[0].plot (Total.index,Total_Acum['Rainfall_from_forcing'],label = 'Precipitation', color= 'silver') #Plot obs data on comparison figure
        ax_compare[0].legend(loc='upper left')
        #ax_compare[0].set_xlabel ('Date'); 
        ax_compare[0].set_ylabel('Cumulative flux (m)')


        
        ax_compare[1].plot(NWM_21.index,NWM_21['flow_cms'], label = 'NWM 2.1',linewidth=1.5, color= 'forestgreen',alpha=0.6) #plot the rainfall from the mixed AORC/other precip array used to generate the equations
        ax_compare[1].plot (Total.index,Total[Output_config.loc['Q_OUT'].output_var_names], label = Model, color= 'orange',linewidth=1) #Plot obs data on comparison figure        
        ax_compare[1].plot(Total.index,Total['Obs_Q'], label = 'Observed',linewidth=0.5, color= 'blue',alpha=0.8) #plot the rainfall from the mixed AORC/other precip array used to generate the equations
        
        
        ax_compare[1].legend(loc='upper left')
        #ax_compare[1].set_xlabel ('Date'); 
        ax_compare[1].set_ylabel('Runoff (m/h)')

        
        To_plot=Output_config[Output_config['To_Channel'] == 1]
        #To_plot[To_plot.index.str.contains("runoff") == False]
        #To_plot[To_plot.index.str.contains("groundwater") == False]
        #To_plot[To_plot.index.str.contains("baseflow") == False]
        for i in range(0,len(To_plot)):
            if(To_plot.iloc[i].output_var_names in Total_Acum.columns):
                #print (To_plot.iloc[i].output_var_names)
                if(To_plot.iloc[i].output_var_units == "m/h"):
                    ax_compare[2].plot (Total.index,Total[To_plot.iloc[i].output_var_names], label = To_plot.index[i],color=CB_color_cycle[i+3]) #Plot obs data on comparison figure
                    #print(To_plot.index[i] + "Total_acum")
                else:
                    ax_compare[2].plot (Total.index,Total[To_plot.iloc[i].output_var_names], label = To_plot.index[i],color=CB_color_cycle[i+3]) #Plot obs data on comparison figure
                    #print(To_plot.index[i] + "Total")
        ax_compare[2].legend(loc='upper left')
        ax_compare[2].set_ylabel('Runoff Components (m)' )
            
        To_plot=Output_config[Output_config['Plot'] == 1]
        cols = [c for c in To_plot.columns if 'runoff' in c ]
        for i in range(0,len(To_plot)):
            if(To_plot.iloc[i].output_var_names in Total_Acum.columns):
                #print (To_plot.iloc[i].output_var_names)
                if(To_plot.iloc[i].output_var_units == "m/h"):
                    ax_compare[3].plot (Total.index,Total_Acum[To_plot.iloc[i].output_var_names], label = To_plot.index[i],color=CB_color_cycle[i]) #Plot obs data on comparison figure
                    #print(To_plot.index[i] + "Total_acum")
                else:
                    ax_compare[3].plot (Total.index,Total[To_plot.iloc[i].output_var_names], label = To_plot.index[i],color=CB_color_cycle[i]) #Plot obs data on comparison figure
                    #print(To_plot.index[i] + "Total")
        #ax_compare[2].plot (CAMEL_Daymet_Acum.index,CAMEL_Daymet_Acum['PET'], label = 'Sim PET-from CAMELS') 
        #ax_compare[2].plot (CAMEL_Daymet_Acum.index,CAMEL_Daymet_Acum['ET'], label = 'Sim ET-from CAMELS') 
        
        ax_compare[3].legend(loc='upper left')
        #ax_compare[2].set_xlabel ('Date'); 
        ax_compare[3].set_ylabel('All Components (m)' )

        To_plot=Output_config[Output_config['Storage'] == 1]
        
        for i in range(0,len(To_plot)):
            if(To_plot.iloc[i].output_var_names in Total_Acum.columns):
                #print (To_plot.iloc[i].output_var_names)
                ax_compare[4].plot (Total.index,Total[To_plot.iloc[i].output_var_names], label = To_plot.index[i]) #Plot obs data on comparison figure
                
        ax_compare[4].legend(loc='upper left')
        #ax_compare[2].set_xlabel ('Date'); 
        ax_compare[4].set_ylabel('Storage/Deficit (m)' )
        #ax_compare[0].set_title(Title_str)
        plt.figtext(0.005,0.74,"(a)",fontsize=13)
        plt.figtext(0.005,0.59,"(b)",fontsize=13)
        plt.figtext(0.005,0.398,"(c)",fontsize=13)
        plt.figtext(0.005,0.27,"(d)",fontsize=13)
        plt.figtext(0.005,0.1,"(e)",fontsize=13)
        fig.savefig(output_figure, bbox_inches='tight',dpi=300)     
        plt.close(fig)

    
def plot_SM(Model,Output_config,Total,Obs,Cat,Title_str,output_figure):        
    
   
    Total_Acum=Total.cumsum(axis= 0)
    CAMEL_Daymet_Acum=CAMEL_Daymet.cumsum(axis= 0)
    NWM_21_Acum=NWM_21.cumsum(axis= 0)
    CB_color_cycle = ['#377eb8', '#ff7f00', '#4daf4a',
                  '#f781bf', '#a65628', '#984ea3',
                  '#999999', '#e41a1c', '#dede00']
    
    if("CFE" in Model) |  ("Topmodel" in Model):        
        num_subplots = 6 #If plotting cumulative precipitation/soil moisture, use 3 subplots (flow, cumulative rain, soil moisture)
        plt.rcParams["figure.figsize"] = (8,16)
        fig, ax_compare = plt.subplots(num_subplots, 1) #Create the plot for this zone
        #ax_compare[0].set_title('Cumulative Precipitation')
        ax_compare[0].plot (Total.index,Total_Acum[Output_config.loc['Q_OUT'].output_var_names], label = Model, color= 'orange',linewidth=3) #Plot obs data on comparison figure
        #ax_compare[0].plot (NWM_21_Acum.index,NWM_21_Acum['flow_cms'], label = 'NWM 2.1 runoff', color= 'forestgreen',linewidth=2) #Plot obs data on comparison figure
        ax_compare[0].plot (Total.index,Total_Acum['Obs_Q'], label = 'Obs runoff', color= 'blue',linewidth=1) #Plot obs data on comparison figure
        
        
        ax_compare[0].plot (Total.index,Total_Acum[Output_config.loc['Surface water flux'].output_var_names], label = 'Accum surface water flux', color= 'black') #Plot obs data on comparison figure
        ax_compare[0].plot (Total.index,Total_Acum['Rainfall_from_forcing'],label = 'Precipitation', color= 'silver') #Plot obs data on comparison figure
        ax_compare[0].legend(loc='upper left')
        #ax_compare[0].set_xlabel ('Date'); 
        ax_compare[0].set_ylabel('Cumulative flux (m)')


        
        
        #ax_compare[1].plot(NWM_21.index,NWM_21['flow_cms'], label = 'NWM 2.1',linewidth=1.5, color= 'forestgreen',alpha=0.6) #plot the rainfall from the mixed AORC/other precip array used to generate the equations
        ax_compare[1].plot (Total.index,Total[Output_config.loc['Q_OUT'].output_var_names], label = Model, color= 'orange',linewidth=1) #Plot obs data on comparison figure        
        ax_compare[1].plot(Total.index,Total['Obs_Q'], label = 'Observed',linewidth=0.8, color= 'blue',alpha=0.8) #plot the rainfall from the mixed AORC/other precip array used to generate the equations
        
        
        ax_compare[1].legend(loc='upper left')
        #ax_compare[1].set_xlabel ('Date'); 
        ax_compare[1].set_ylabel('Runoff (m/h)')

        
        To_plot=Output_config[Output_config['To_Channel'] == 1]
        #To_plot[To_plot.index.str.contains("runoff") == False]
        #To_plot[To_plot.index.str.contains("groundwater") == False]
        #To_plot[To_plot.index.str.contains("baseflow") == False]
        for i in range(0,len(To_plot)):
            if(To_plot.iloc[i].output_var_names in Total_Acum.columns):
                #print (To_plot.iloc[i].output_var_names)
                if(To_plot.iloc[i].output_var_units == "m/h"):
                    ax_compare[2].plot (Total.index,Total[To_plot.iloc[i].output_var_names], label = To_plot.index[i],color=CB_color_cycle[i+3]) #Plot obs data on comparison figure
                    #print(To_plot.index[i] + "Total_acum")
                else:
                    ax_compare[2].plot (Total.index,Total[To_plot.iloc[i].output_var_names], label = To_plot.index[i],color=CB_color_cycle[i+3]) #Plot obs data on comparison figure
                    #print(To_plot.index[i] + "Total")
        ax_compare[2].legend(loc='upper left')
        ax_compare[2].set_ylabel('Runoff Components (m)' )
            
        To_plot=Output_config[Output_config['Plot'] == 1]
        cols = [c for c in To_plot.columns if 'runoff' in c ]
        for i in range(0,len(To_plot)):
            if(To_plot.iloc[i].output_var_names in Total_Acum.columns):
                #print (To_plot.iloc[i].output_var_names)
                if(To_plot.iloc[i].output_var_units == "m/h"):
                    ax_compare[3].plot (Total.index,Total_Acum[To_plot.iloc[i].output_var_names], label = To_plot.index[i],color=CB_color_cycle[i]) #Plot obs data on comparison figure
                    #print(To_plot.index[i] + "Total_acum")
                else:
                    ax_compare[3].plot (Total.index,Total[To_plot.iloc[i].output_var_names], label = To_plot.index[i],color=CB_color_cycle[i]) #Plot obs data on comparison figure
                    #print(To_plot.index[i] + "Total")
        #ax_compare[2].plot (CAMEL_Daymet_Acum.index,CAMEL_Daymet_Acum['PET'], label = 'Sim PET-from CAMELS') 
        #ax_compare[2].plot (CAMEL_Daymet_Acum.index,CAMEL_Daymet_Acum['ET'], label = 'Sim ET-from CAMELS') 
        
        ax_compare[3].legend(loc='upper left')
        #ax_compare[2].set_xlabel ('Date'); 
        ax_compare[3].set_ylabel('All Components (m)' )

        To_plot=Output_config[Output_config['Storage'] == 1]
        
        for i in range(0,len(To_plot)):
            if(To_plot.iloc[i].output_var_names in Total_Acum.columns):
                #print (To_plot.iloc[i].output_var_names)
                ax_compare[4].plot (Total.index,Total[To_plot.iloc[i].output_var_names], label = To_plot.index[i]) #Plot obs data on comparison figure
                
        ax_compare[4].legend(loc='upper left')
        #ax_compare[2].set_xlabel ('Date'); 
        ax_compare[4].set_ylabel('Storage/Deficit (m)' )
        #ax_compare[0].set_title(Title_str)

        Obs_F=Obs_data.filter(like='sm')
        for i in range(0,len(Obs_F.columns)):
            
                #print (To_plot.iloc[i].output_var_names)
            ax_compare[5].plot (Obs_F.index,Obs_F[Obs_F.columns[i]], label = Obs_F.columns[i]) #Plot obs data on comparison figure
                
        ax_compare[5].legend(loc='upper left')
        #ax_compare[2].set_xlabel ('Date'); 
        ax_compare[5].set_ylabel('Observed Storage/Deficit (m)' )
        #ax_compare[0].set_title(Title_str)

        plt.figtext(0.005,0.75,"(a)",fontsize=13)
        plt.figtext(0.005,0.65,"(b)",fontsize=13)
        plt.figtext(0.005,0.5,"(c)",fontsize=13)
        plt.figtext(0.005,0.38,"(d)",fontsize=13)
        plt.figtext(0.005,0.28,"(e)",fontsize=13)
        plt.figtext(0.005,0.1,"(e)",fontsize=13)
        fig.savefig(output_figure, bbox_inches='tight',dpi=300)     
        plt.close(fig)

def ncdump(nc_fid, verb=True):
    '''
    ncdump outputs dimensions, variables and their attribute information.
    The information is similar to that of NCAR's ncdump utility.
    ncdump requires a valid instance of Dataset.

    Parameters
    ----------
    nc_fid : netCDF4.Dataset
        A netCDF4 dateset object
    verb : Boolean
        whether or not nc_attrs, nc_dims, and nc_vars are printed

    Returns
    -------
    nc_attrs : list
        A Python list of the NetCDF file global attributes
    nc_dims : list
        A Python list of the NetCDF file dimensions
    nc_vars : list
        A Python list of the NetCDF file variables
    '''
    def print_ncattr(key):
        """
        Prints the NetCDF file attributes for a given key

        Parameters
        ----------
        key : unicode
            a valid netCDF4.Dataset.variables key
        """
        try:
            print ("\t\ttype:", repr(nc_fid.variables[key].dtype))
            for ncattr in nc_fid.variables[key].ncattrs():
                print ('\t\t%s:' % ncattr,\
                      repr(nc_fid.variables[key].getncattr(ncattr)))
        except KeyError:
            print ("\t\tWARNING: %s does not contain variable attributes" % key)

    # NetCDF global attributes
    nc_attrs = nc_fid.ncattrs()
    if verb:
        #print "NetCDF Global Attributes:"
        for nc_attr in nc_attrs:
            print ('\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr)))
    nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions
    # Dimension shape information.
    if verb:
        #print "NetCDF dimension information:"
        for dim in nc_dims:
            #print "\tName:", dim 
            #print "\t\tsize:", len(nc_fid.dimensions[dim])
            print_ncattr(dim)
    # Variable information.
    nc_vars = [var for var in nc_fid.variables]  # list of nc variables
    if verb:
        #print "NetCDF variable information:"
        for var in nc_vars:
            if var not in nc_dims:
                print ('\tName:', var)
                print ("\t\tdimensions:", nc_fid.variables[var].dimensions)
                print ("\t\tsize:", nc_fid.variables[var].size)
                print_ncattr(var)
    return nc_attrs, nc_dims, nc_vars

def Generate_Scatter_plot2(Model,Output_config,Total,CAMEL_Daymet_Acum,NWM_21,Title_str,output_figure): 
    import sys
    sys.path.append("/home/west/git_repositories/ngen-cal-master/ngen-cal/python/ngen_cal/")
    import objectives as OB  
    import seaborn as sns
    import numpy as np
    sns.set_style("whitegrid")
    
    Total_daily=Total.resample('D').apply(lambda x: np.sum(x.values))
    if(len(NWM_21)>0):
        NWM_21_daily=NWM_21.resample('D').apply(lambda x: np.sum(x.values))
    else:
        NWM_21_daily=pd.DataFrame()
    Total_month=Total.resample('M').apply(lambda x: np.sum(x.values))
    Var_name_out=Output_config.loc['Q_OUT'].output_var_names
    if("CFE" in Model) |  ("Topmodel" in Model):        
        num_subplots = 2 #If plotting cumulative precipitation/soil moisture, use 3 subplots (flow, cumulative rain, soil moisture)
        plt.rcParams["figure.figsize"] = (4,8)
        fig, ax_compare = plt.subplots(num_subplots, 1) #Create the plot for this zone
        #ax_compare[0].set_title('Cumulative Precipitation')
        # Value=OB.nash_sutcliffe(Total['Obs_Q'], Total[Var_name_out])
        # ax_compare[0].scatter(Total['Obs_Q'],Total[Var_name_out], label = 'Hourly Observed versus Simulated Q(m/h)', color= 'b') #Plot obs data on comparison figure        
        # ax_compare[0].set_xlabel ('Obs Q (m/h)'); 
        # ax_compare[0].set_ylabel('Sim Q (m/h)')
        # ax_compare[0].set_aspect('equal',adjustable='box')
        # max_y=1.05*max(Total[Var_name_out].max(),Total['Obs_Q'].max())
        # ax_compare[0].set_xlim([0,max_y])
        # ax_compare[0].set_ylim([0,max_y])
        # ax_compare[0].plot ([0,max_y],[0,max_y],linestyle='dashed',linewidth=0.5,alpha=0.8, color= 'r') #Plot obs data on comparison figure
        # ax_compare[0].set_title("Hourly runoff - Nash = " + str(round(Value,2)))
        Total_dailyNoNAN=Total_daily[[Var_name_out,'Obs_Q']].dropna()
        Nash=OB.nash_sutcliffe(Total_dailyNoNAN[Var_name_out],Total_dailyNoNAN['Obs_Q'])
        NNash=OB.normalized_nash_sutcliffe(Total_dailyNoNAN[Var_name_out],Total_dailyNoNAN['Obs_Q'])
        if(len(NWM_21)>0):  
            Nash_NWM=OB.nash_sutcliffe(NWM_21_daily['flow_cms'],Total_dailyNoNAN['Obs_Q'])
        else: 
            Nash_NWM=""
        mean_bias=OB.mean_bias(Total_dailyNoNAN[Var_name_out],Total_dailyNoNAN['Obs_Q'])
        mean_absolute_error=OB.mean_absolute_error(Total_dailyNoNAN[Var_name_out],Total_dailyNoNAN['Obs_Q'])
        RMSE=OB.RMSE(Total_dailyNoNAN[Var_name_out],Total_dailyNoNAN['Obs_Q'])
        NRMSE=OB.NRMSE(Total_dailyNoNAN[Var_name_out],Total_dailyNoNAN['Obs_Q'])
        ax_compare[0].scatter(Total_daily['Obs_Q'],Total_daily[Var_name_out], label = Model,s=13,edgecolors='black',color='silver',linewidths=0.3)
        if(len(NWM_21)>0): ax_compare[0].scatter(Total_daily['Obs_Q'],NWM_21_daily['flow_cms'], label = 'NWM2.1',s=13,edgecolors='forestgreen',facecolors='none',linewidths=0.5,alpha=0.5)
        ax_compare[0].set_xlabel ('Obs Runoff (m/day)'); 
        ax_compare[0].set_ylabel('Sim Runoff (m/day)')
        ax_compare[0].set_aspect('equal',adjustable='box')
        ax_compare[0].legend(loc='upper left')
        
        max_y=1.05*max(Total_daily[Var_name_out].max(),Total_daily['Obs_Q'].max())
        ax_compare[0].set_xlim([0,max_y])
        ax_compare[0].set_ylim([0,max_y])
        ax_compare[0].plot ([0,max_y],[0,max_y],linestyle='dashed',linewidth=0.5, color= 'r') #Plot obs data on comparison figure    
        if(len(NWM_21)>0): 
            ax_compare[0].set_title("NSE = " + str(round(Nash,2)) +"(NWM 2.1: "+ str(round(Nash_NWM,2))+")")
        else:
            ax_compare[0].set_title("NSE = " + str(round(Nash,2)) +" - No NWM 2.1")
        Total_month['Month']=Total_month.index.month
        #Total_month=Total_month[['Month',Var_name_out,'Obs_Q']]
        ax_compare[1]
        Obs_Month=Total_month[['Month','Obs_Q']]
        Obs_Month['Variable']='Obs'
        Obs_Month=Obs_Month.rename(columns={'Obs_Q':"Runoff"})
        Sim_Month=Total_month[['Month',Var_name_out]]
        Sim_Month['Variable']='Sim'
        Sim_Month=Sim_Month.rename(columns={Var_name_out:"Runoff"})
        Month_Q=pd.concat([Obs_Month,Sim_Month])
        sns.boxplot(x='Month',y="Runoff",hue='Variable',data=Month_Q,ax=ax_compare[1])
        ax_compare[1].set_xlabel ('Month'); 
        ax_compare[1].set_ylabel('Runoff (m/month)')
        ax_compare[1].yaxis.grid(True)
        ax_compare[1].xaxis.grid(True)
        plt.figtext(0.005,0.5,"(e)",fontsize=14)
        plt.figtext(0.005,0.08,"(f)",fontsize=14)
        #ax_compare[1].set_aspect('equal',adjustable='box')
        # ax_compare[1].scatter(Total_daily['Obs_Q'],Total_daily[Var_name_out], label = 'Daily Observed versus Simulated Q(m/d)', color= 'b') #Plot obs data on comparison figure        
        # max_y=1.05*max(Total_daily[Var_name_out].max(),Total_daily['Obs_Q'].max())
        # ax_compare[1].set_xlim([0,max_y])
        # ax_compare[1].set_ylim([0,max_y])
        # ax_compare[1].plot ([0,max_y],[0,max_y],linestyle='dashed',linewidth=0.5,alpha=0.8, color= 'r') #Plot obs data on comparison figure
        
        
        #ax_compare[1].set_title("Q Seasonality ")
        fig.savefig(output_figure, bbox_inches='tight',dpi=300)  
        plt.close(fig)
        return Nash,NNash,mean_bias,mean_absolute_error,RMSE,NRMSE
    

def Generate_multiple_model_results(Daily_Q_all_Model,Title_str,output_figure):     
    import seaborn as sns    
    import matplotlib.pyplot as plt      
    #num_subplots = 1 #If plotting cumulative precipitation/soil moisture, use 3 subplots (flow, cumulative rain, soil moisture)
    sns.set_style("whitegrid")
    fig, ax = plt.subplots() #Create the plot for this zone
    fig.set_size_inches(0.8*len(Daily_Q_all_Model['Source'].unique()),4)
    

    #plt.rcParams["figure.figsize"] = (5,10)
    sns.boxplot(x='Source',y="Runoff[m/day]",data=Daily_Q_all_Model,ax=ax,color='silver',width=0.5)
    ax.set_xlabel ('Source',fontsize=12)
    ax.set_ylabel('Runoff[m/day] - log scale')
    ax.set_xticklabels(Daily_Q_all_Model['Source'].unique(),rotation=90)
    ax.yaxis.grid(True)
    ax.set_yscale("log")
    #ax.set_title(Title_str)
    fig.savefig(output_figure, bbox_inches='tight',dpi=300)        
    plt.close(fig)

def Generate_PET_plot(Model,Output_config,PETts,ETts,output_figure): 
    import sys
 
    import seaborn as sns
    import numpy as np
    sns.set_style("whitegrid")
    
   
       
    num_subplots = 2 #If plotting cumulative precipitation/soil moisture, use 3 subplots (flow, cumulative rain, soil moisture)
    plt.rcParams["figure.figsize"] = (6,8)
    fig, ax_compare = plt.subplots(num_subplots, 1) #Create the plot for this zone
    sns.lineplot(data=PETts,x="hour",y=Output_config.loc['POTENTIAL_ET'].output_var_names,ax=ax_compare[0], label = 'PET')
    sns.lineplot(data=ETts,x="hour",y=Output_config.loc['ACTUAL_ET'].output_var_names,ax=ax_compare[0], label = 'ET')
    ax_compare[0].set_xlabel ('Hour of the day (UTC)'); 
    ax_compare[0].set_ylabel('PET or ET (m/hour)')
    ax_compare[0].legend(loc='upper left')

    sns.lineplot(data=PETts,x="DoY",y=Output_config.loc['POTENTIAL_ET'].output_var_names,ax=ax_compare[1], label = 'PET')
    sns.lineplot(data=ETts,x="DoY",y=Output_config.loc['ACTUAL_ET'].output_var_names,ax=ax_compare[1], label = 'ET')
    ax_compare[1].set_xlabel ('Day of the year (UTC)'); 
    ax_compare[1].set_ylabel('PET or ET (m/hour)')
    ax_compare[1].legend(loc='upper left')
    plt.figtext(0.001,0.48,"(a)",fontsize=14)
    plt.figtext(0.001,0.08,"(b)",fontsize=14)
    fig.savefig(output_figure, bbox_inches='tight',dpi=300)  
    plt.close(fig)
    
    
# for example
Hyd_folder="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"
Output_folder="/media/west/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Results/"


Output_ngen=["Output_ngen_03292022"]
#Output_ngen=["Output_ngen_03092022"]
Output_Wanru="/media/west/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Results/Model_output_daily/"
if not os.path.exists(Output_Wanru): os.mkdir(Output_Wanru)  
Output_Rachel="/media/west/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Results/Output4Rachel/"
if not os.path.exists(Output_Rachel): os.mkdir(Output_Rachel)  
Results_SM=Output_folder+"/SM/"
if not os.path.exists(Results_SM): os.mkdir(Results_SM) 
Results_SNOW=Output_folder+"/SNOW/"
if not os.path.exists(Results_SNOW): os.mkdir(Results_SNOW) 
#TxDot_join=pd.read_csv(Hyd_folder +'TxDot_JOIN.csv')
USCRN_join=pd.read_csv(Hyd_folder +'USCRN_JOIN.csv')
SCAN_join=pd.read_csv(Hyd_folder +'SCAN_JOIN.csv')
SNOTEL_join=pd.read_csv(Hyd_folder +'SNOTEL_JOIN.csv')

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

NashDf=pd.DataFrame(index=CAMELS_516.index,columns=Models)
NNashDf=pd.DataFrame(index=CAMELS_516.index,columns=Models)
mean_biasDf=pd.DataFrame(index=CAMELS_516.index,columns=Models)
mean_absolute_errorDf=pd.DataFrame(index=CAMELS_516.index,columns=Models)
RMSEDf=pd.DataFrame(index=CAMELS_516.index,columns=Models)
NRMSEDf=pd.DataFrame(index=CAMELS_516.index,columns=Models)
PET=pd.DataFrame(index=CAMELS_516.index,columns=Models)
ET=pd.DataFrame(index=CAMELS_516.index,columns=Models)

for i in range (100,len(CAMELS_516)):   
    
    hru_id=CAMELS_516.index[i]
    Folder=CAMELS_516.iloc[i]['Folder_CAMELS']
    Daily_Q_all_Model=pd.DataFrame()  
    
    USCRN_flag=0;SCAN_flag=0;SNOTEL_flag=0;Special_case=0
    cat_Special=[]
    if(hru_id in USCRN_join.gauge_id.values): 
        USCRN_flag=1
        cat_Special.append(['USCRN',USCRN_join[USCRN_join.gauge_id==hru_id].id.values[0],USCRN_join[USCRN_join.gauge_id==hru_id].Filename.values[0]])
        Special_case=Special_case+1
    if(hru_id in SCAN_join.gauge_id.values): 
        SCAN_flag=1
        cat_Special.append(['SCAN',SCAN_join[SCAN_join.gauge_id==hru_id].id.values[0],SCAN_join[SCAN_join.gauge_id==hru_id].Filename.values[0]])
        Special_case=Special_case+1
    if(hru_id in SNOTEL_join.gauge_id.values): 
        SNOTEL_flag=1
        cat_Special.append(['SNOTEL',SNOTEL_join[SNOTEL_join.gauge_id==hru_id].id.values[0],SNOTEL_join[SNOTEL_join.gauge_id==hru_id].nsite.values[0]-1])
        Special_case=Special_case+1

    
    
    for j in range (0,len(Models)):  
        flag_run_plot_all_models=1
        print("Basin " + str(i) + " / " + str(len(CAMELS_516))+ " hru_id" + hru_id + "Model" + Models[j] )
        for z in range(0,len(Output_ngen)):
            
            if ("PET" in Models[j]) and (CAMELS_516.iloc[i]['RunPET']==0):
                print("Snow dominated areas, do not plot PET")
            else:

                
                # Read output config file
                if("CFE" in Models[j]):  file=Config_file[0]
                else:  file=Config_file[1]
                Output_config=pd.read_csv(file,index_col=0)
                outfolder=Hyd_folder+"/"+Folder+"/"
                catchment_file=Hyd_folder+"/"+Folder+'/spatial/catchment_data.geojson'    
                zones = gp.GeoDataFrame.from_file(catchment_file) 
                
                Results=Output_folder+"/"+Folder+"/"+Output_ngen[z]+"/"+Models[j]+"/"
                
                
                all_results=glob.glob(Results+"cat*.csv")
                flag_empty=0
                for f in all_results:
                    if(os.path.getsize(f)==0):
                        flag_empty=1
                flag_wrong=0 
                
                if(len(all_results)>len(zones)):
                    Cat_out_file=f
                    Cat_out=pd.read_csv(Cat_out_file,parse_dates=True,index_col=1)
                    nvar=0
                    if(len(all_results)>1):
                        for ff in range(0,len(Output_config)):
                            if(not Output_config.output_var_names[ff] in Cat_out.columns):
                                print ("did not find variable " + Output_config.output_var_names[ff])
                                nvar=nvar+1
                        if(nvar>3):  
                            flag_wrong=1   
                if(flag_empty==1) | (flag_wrong==1):
                    for f in os.listdir(Results):
                       os.remove(os.path.join(Results,f))                        
                
                
                
                if(len(all_results)<len(zones)) | (flag_empty==1) | (flag_wrong==1):
                    Temp=pd.DataFrame([[hru_id,Models[j],CAMELS_516.iloc[i]['frac_snow'],0]],columns=['hru_id','Models','frac_snow','Done'])
                    Models_run=Models_run.append(Temp)
                    if(os.path.exists(Results)) & (len(all_results)>0): 
                        Problem_simulations.append([hru_id,Models[j],"Not Enough files"])
                        print (hru_id + "  Not Enough files")
                        for f in os.listdir(Results):
                            os.remove(os.path.join(Results,f))
                            
                else:
                    Total_file=Output_Rachel+hru_id+"_"+Models[j]+".csv"
                    if(os.path.isfile(Total_file)) & (Generate_plots_flag==0) & (Special_case==0):
                        print ("Do not run: " + Total_file)
                        flag_run_plot_all_models=0
                    else:
                        Obs_Q_file=Hyd_folder+"/"+Folder+"/Validation/usgs_hourly_flow_2007-2019_"+hru_id+".csv"
                        Obs_Q_cms=pd.read_csv(Obs_Q_file,parse_dates=True,index_col=1)
                        Obs_Q_cms=Obs_Q_cms['q_cms']
                        Obs_Q_cfs=Obs_Q_cms*35.31
                        min_date=Obs_Q_cms.index.min()
                        max_date=Obs_Q_cms.index.max()            
    
                        total_area=zones['area_sqkm'].sum()
                        Obs_q_mh=(Obs_Q_cms/total_area)*3.6/1000.
                        
                       
                        # CAMELS PET AND ET
                        CAMEL_Daymet_file=Hyd_folder+"/"+Folder+"/Validation/model_output_daymet/"+hru_id+"_05_model_output.txt"
                        CAMEL_Daymet=pd.read_csv(CAMEL_Daymet_file,delimiter=r"\s+",parse_dates={"date":["YR","MNTH","DY"]})
                        #CAMEL_Daymet['Date']=pd.date_range(start='10/1/1980',end='12/31/2014')
                        CAMEL_Daymet=CAMEL_Daymet.set_index('date')
                        CAMEL_Daymet  =CAMEL_Daymet/1000.     
                        
                        # NWMStreaflow
                       
                        NWM_21_file=Hyd_folder+"/"+Folder+"/Validation/nwm_v2.1_chrt."+hru_id+".csv"
                        if(os.path.isfile(NWM_21_file)):
                            NWM_21=pd.read_csv(NWM_21_file,parse_dates=True,index_col=0)
                        else: NWM_21=pd.DataFrame()
                        #total_area=zones['area_sqkm'].sum()
                        NWM_21=(NWM_21/total_area)*3.6*100./1000.
                        
                        
                        Rainfall_from_forcing_mmh=pd.DataFrame()
                
                        for index,row in zones.iterrows():
                            catstr=row[0]     
                            # READING FORCING Files- Check it is input correctly
                            Focing_file=Hyd_folder+"/"+Folder+"/forcing/"+catstr+".csv"
                            Obs_RR_mmh_Temp=pd.read_csv(Focing_file,parse_dates=True,index_col=0)
                            Obs_RR_mmh_Temp=Obs_RR_mmh_Temp['RAINRATE'].to_frame()*3600.
                            Obs_RR_mmh_Temp=Obs_RR_mmh_Temp.rename(columns={Obs_RR_mmh_Temp.columns[0]:catstr})        
                            Rainfall_from_forcing_mmh=pd.concat([Rainfall_from_forcing_mmh,Obs_RR_mmh_Temp],axis=1)
                    
                           # READING OUTPUT CFE
                            Cat_out_file=Results+catstr+".csv"
                            Cat_out=pd.read_csv(Cat_out_file,parse_dates=True,index_col=1)
                            #Cat_out=Cat_out.dropna()
                            if(isinstance(Cat_out.index.min(),str)):
                                Cat_out.index=pd.to_datetime(Cat_out.index)
                            if(index==0):
                                Total_out=Cat_out.copy()
                            else:
                                Total_out=Total_out+Cat_out
                            
                            min_date=Cat_out.index.min()+timedelta(days=Spinnup)

                        Total_out=Total_out/float(len(zones))
                        if(Total_out.index.max()<max_date_plot):
                            Problem_simulations.append([hru_id,Models[j],"Short Simulations"])
                            print (hru_id + "  Short Simulations")
                            for f in os.listdir(Results):
                                os.remove(os.path.join(Results,f))
                                
                        else:
                            
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
                            Obs_q_mh=Obs_q_mh.drop_duplicates(keep = 'first')
                            Total=pd.concat([Total,Obs_q_mh],axis=1)
                            output_figure= Results+"All_Outputs_figure"+min_date_plot.strftime ('%Y-%m')+"_"+max_date_plot.strftime ('%Y-%m')+".png"
                            Title_str=hru_id+ " - " +Models[j]+' - ' + min_date_plot.strftime ('%Y-%m-%d')+' through '+ max_date_plot.strftime ('%Y-%m-%d')
                            #generate_hydrograph(Total,Spinnup,Title_str,output_figure)
                            Total=Total[(Total.index>=min_date_plot) & (Total.index<max_date_plot)]   
                            
                            Total_daily=Total.resample('D').apply(lambda x: np.sum(x.values))
                            
                            PETts=Total[Output_config.loc['POTENTIAL_ET'].output_var_names].to_frame()                   
                            PETts['hour']=Total.index.strftime ('%H')
                            PETts['DoY']=Total.index.dayofyear
                            ETts=Total[Output_config.loc['ACTUAL_ET'].output_var_names].to_frame()                 
                            ETts['hour']=Total.index.strftime ('%H')
                            ETts['DoY']=Total.index.dayofyear
                            
    
                            output_figure= Results+"PET"+min_date_plot.strftime ('%Y-%m')+"_"+max_date_plot.strftime ('%Y-%m')+".png"
                            if(Generate_plots_flag==1): Generate_PET_plot(Models[j],Output_config,PETts,ETts,output_figure)
                            #PET.at[hru_id,Models[j]]=Total[Output_config.loc['POTENTIAL_ET'].output_var_names].dropna().sum(min_count=52608)/1000./6.
                            #ET.at[hru_id,Models[j]]=Total[Output_config.loc['ACTUAL_ET'].output_var_names].dropna().sum(min_count=52608)/1000./6.
                            
                            PET.at[hru_id,Models[j]]=Total[Output_config.loc['POTENTIAL_ET'].output_var_names].sum()/float(int((max_date_plot-min_date_plot).days/365.))
                            ET.at[hru_id,Models[j]]=Total[Output_config.loc['ACTUAL_ET'].output_var_names].sum()/float(int((max_date_plot-min_date_plot).days/365.))
                            
                            CAMEL_Daymet=CAMEL_Daymet[(CAMEL_Daymet.index>=min_date_plot) & (CAMEL_Daymet.index<max_date_plot)]
                            if(os.path.isfile(NWM_21_file)): 
                                NWM_21=NWM_21[(NWM_21.index>=min_date_plot) & (NWM_21.index<max_date_plot)]
                                NWM_21_daily=NWM_21.resample('D').apply(lambda x: np.sum(x.values))
                            if(len(Daily_Q_all_Model)==0):
                                Temp=Total_daily['Obs_Q'].to_frame()
                                Temp=Temp.rename(columns={'Obs_Q':"Runoff[m/day]"})
                                Temp['Source']="Obs"
                                Daily_Q_all_Model=pd.concat([Daily_Q_all_Model,Temp])
                                #Temp=CAMEL_Daymet['MOD_RUN'].to_frame()
                                #Temp=Temp.rename(columns={'MOD_RUN':"Runoff[m/day]"})
                                #Temp['Source']="CAMELS_SIM"
                                #Daily_Q_all_Model=pd.concat([Daily_Q_all_Model,Temp])  
                                if(os.path.isfile(NWM_21_file)): 
                                    Temp=NWM_21_daily['flow_cms'].to_frame()
                                    Temp=Temp.rename(columns={'flow_cms':"Runoff[m/day]"})
                                    Temp['Source']="NWM2.1"
                                    Daily_Q_all_Model=pd.concat([Daily_Q_all_Model,Temp])  
                                    
                                                                      
                            Temp=Total_daily[Output_config.loc['Q_OUT'].output_var_names].to_frame()
                            Temp=Temp.rename(columns={Output_config.loc['Q_OUT'].output_var_names:"Runoff[m/day]"})
                            Temp['Source']=Models[j]                    
                            Daily_Q_all_Model=pd.concat([Daily_Q_all_Model,Temp])                    
                            
                            output_figure= Results+"Runoff_figure"+min_date_plot.strftime ('%Y-%m')+"_"+max_date_plot.strftime ('%Y-%m')+".png"
                            if(os.path.exists(output_figure)):os.remove(output_figure)
                            if(Generate_plots_flag==1): plot_Results_v2(Models[j],Output_config,Total,CAMEL_Daymet,NWM_21,Title_str,output_figure)

                            if(Special_case>0):
                                Cat_out_file=Results+cat_Special[0][1]+".csv"
                                Cat_out=pd.read_csv(Cat_out_file,parse_dates=True,index_col=1)                           
                                if(cat_Special[0][0]=='USCRN')| (cat_Special[0][0]=='SCAN'):
                                    Obs_data=pd.read_csv(cat_Special[0][2])  
                                    if(cat_Special[0][0]=='USCRN'): cols=["Year","Month","Day"]
                                    if(cat_Special[0][0]=='SCAN'): cols=["year","month","day"]
                                    Obs_data['date'] = Obs_data[cols].apply(lambda x: '-'.join(x.values.astype(int).astype(str)), axis="columns")
                                    Obs_data['date']=pd.to_datetime(Obs_data['date'])
                                    Obs_data=Obs_data.set_index('date')
                                    Obs_data=Obs_data[(Obs_data.index>=Cat_out.index.min()) & (Obs_data.index<=Cat_out.index.max())]
                                    output_figure= Results_SM+hru_id+Models[j]+cat_Special[0][0]+".png"
                                    Title_str=hru_id+" - " + Models[j] + " - " + cat_Special[0][0]                                    
                                    plot_SM(Models[j],Output_config,Total,Obs_data,Cat_out,Title_str,output_figure)
                                
                                if(cat_Special[0][0]=='SNOTEL'):   
                                    # nc_SNOTEL1=nc.Dataset("/media/west/Expansion/Projects/SNOTEL/SNOTEL_WUS_obs_raw_PNNLbcqc.nc")
                                    # nc_attrs1, nc_dims1, nc_vars1 = ncdump(nc_SNOTEL1)                   
                                    nc_SNOTEL=nc.Dataset("/media/west/Expansion/Projects/SNOTEL/SNOTEL_WUS_obs_raw_PNNLbcqc.timeseries.nc"  )
                                    nc_attrs, nc_dims, nc_vars = ncdump(nc_SNOTEL)
                                    swe=nc_SNOTEL['snotel_swe_pnnl'][:][cat_Special[0][2]]
                                    date_ini=datetime(2008,10,1,0,0)
                                    date=pd.date_range(start=date_ini,periods=len(swe),freq='D')
                                    SWE_df=pd.DataFrame(data=swe,index=date,columns=["SWE"])
                                    print(LU)
                                    # Obs_data=pd.read_csv(cat_Special[0][2])  
                                    # cols=["Year","Month","Day"]
                                    # Obs_data['date'] = Obs_data[cols].apply(lambda x: '-'.join(x.values.astype(int).astype(str)), axis="columns")
                                    # Obs_data['date']=pd.to_datetime(Obs_data['date'])
                                    # Obs_data=Obs_data.set_index('date')
                                    # Obs_data=Obs_data[(Obs_data.index>=Cat_out.index.min()) & (Obs_data.index<=Cat_out.index.max())]
                                    # output_figure= Results_SM+hru_id+Models[j]+cat_Special[0][0]+".png"
                                    # Title_str=hru_id+" - " + Models[j] + " - " + cat_Special[0][0]                                    
                                    # plot_SM(Models[j],Output_config,Total,Obs_data,Cat_out,Title_str,output_figure)
                                                                    
                            for iyear in range(2007,2012):
                                min_date_plot1=datetime(iyear,10,1,0,0)
                                max_date_plot1=datetime(iyear+1,10,1,0,0)
                                Title_str=hru_id+ " - " +Models[j]+' - ' + min_date_plot1.strftime ('%Y-%m-%d')+' through '+ max_date_plot1.strftime ('%Y-%m-%d')
                                Total_temp=Total[(Total.index>=min_date_plot1) & (Total.index<max_date_plot1)] 
                                CAMEL_Daymet_temp=CAMEL_Daymet[(CAMEL_Daymet.index>=min_date_plot1) & (CAMEL_Daymet.index<max_date_plot1)] 
                                if(os.path.isfile(NWM_21_file)): 
                                    NWM_21_temp=NWM_21[(NWM_21.index>=min_date_plot1) & (NWM_21.index<max_date_plot1)] 
                                else: NWM_21_temp=pd.DataFrame()
                                output_figure= Results+"Runoff_figure"+min_date_plot1.strftime ('%Y-%m')+"_"+max_date_plot1.strftime ('%Y-%m')+".png"
                                if(os.path.exists(output_figure)):os.remove(output_figure)
                                if(Generate_plots_flag==1): plot_Results_v3(Models[j],Output_config,Total_temp,CAMEL_Daymet_temp,NWM_21_temp,Title_str,output_figure)
                            
                            Title_str=hru_id+ " - " +Models[j]+' - ' + min_date_plot.strftime ('%Y-%m-%d')+' through '+ max_date_plot.strftime ('%Y-%m-%d')
                            output_figure=Results+"Scatter_plot"+min_date_plot.strftime ('%Y-%m')+"_"+max_date_plot.strftime ('%Y-%m')+".png"
                            if(os.path.exists(output_figure)):os.remove(output_figure)
                            
                            
                            [Nash,NNash,mean_bias,mean_absolute_error,RMSE,NRMSE]=Generate_Scatter_plot2(Models[j],Output_config,Total,CAMEL_Daymet,NWM_21,Title_str,output_figure)
                            # NashDf.at[hru_id,Models[j]]=Nash
                            # NNashDf.at[hru_id,Models[j]]=NNash
                            # mean_biasDf.at[hru_id,Models[j]]=mean_bias
                            # mean_absolute_errorDf.at[hru_id,Models[j]]=mean_absolute_error
                            # RMSEDf.at[hru_id,Models[j]]=RMSE
                            # NRMSEDf.at[hru_id,Models[j]]=NRMSE
                            # Temp=pd.DataFrame([[hru_id,Models[j],CAMELS_516.iloc[i]['frac_snow'],1]],columns=['hru_id','Models','frac_snow','Done'])
                            # Models_run=Models_run.append(Temp)
                              
                            if(len(NWM_21)>0): 
                                NWM_21=NWM_21.rename(columns={"flow_cms": "Q_NWM_2.1"})
                                Total=pd.concat([Total,NWM_21],axis=1)
                                Total[['Rainfall_from_forcing',Output_config.loc['Surface water flux'].output_var_names,Output_config.loc['Q_OUT'].output_var_names,'Q_NWM_2.1','Obs_Q']].to_csv(Total_file)
                            else:
                                Total[['Rainfall_from_forcing',Output_config.loc['Surface water flux'].output_var_names,Output_config.loc['Q_OUT'].output_var_names,'Obs_Q']].to_csv(Total_file)
                                
    Multi_model_comparison_figure=Output_folder+"/"+Folder+"/"+Output_ngen[z]+"/"+"Multiple_Models"+min_date_plot.strftime ('%Y-%m')+"_"+max_date_plot.strftime ('%Y-%m')+".png"                
    Title_str=hru_id+ " - " + min_date_plot.strftime ('%Y-%m')+' to '+ max_date_plot.strftime ('%Y-%m')
    if(len(Daily_Q_all_Model)>0) & (flag_run_plot_all_models==1): 
        Generate_multiple_model_results(Daily_Q_all_Model,Title_str,Multi_model_comparison_figure)              
        Daily_Q_all_Model.pivot(columns="Source",values="Runoff[m/day]").to_csv(Output_Wanru+Folder+"DailyRunoff.csv")
                #output_figure=Results+"Water_Balance"+min_date_plot.strftime ('%Y-%m')+"_"+max_date_plot.strftime ('%Y-%m')+".png"
                #Title_str=Folder+ " - " + Models[j]+' - ' + min_date_plot.strftime ('%Y-%m-%d %H:%M:%S')+' through '+ max_date_plot.strftime ('%Y-%m-%d %H:%M:%S')
                #plot_Water_Balance(Models[j],Output_config,Total,Title_str,output_figure)
                #outfolder_val=outfolder+"/Validation/"
                #CAMELS_Out=['model_output_daymet','model_output_nldas','model_output_maurer']
            # result = pd.merge(Obs_q_mh_plot.to_frame(), Total_out_plot[q_var[j]].to_frame(),left_index=True,right_index=True)
            # plt.plot(result['q_cms'],result[q_var[j]], 'o')
# Models_run.to_csv(Output_Wanru+"Summary_run_March_report.csv")   
# NashDf.to_csv(Output_Wanru+"Nash_all_models.csv")  
# mean_biasDf.to_csv(Output_Wanru+"mean_bias_all_models.csv") 
# mean_absolute_errorDf.to_csv(Output_Wanru+"mean_absolute_error_all_models.csv") 
# RMSEDf.to_csv(Output_Wanru+"RMSE_all_models.csv")  
# NRMSEDf.to_csv(Output_Wanru+"NRMSE_all_models.csv")  
# PET.to_csv(Output_Wanru+"PET_all_models.csv") 
# ET.to_csv(Output_Wanru+"ET_all_models.csv") 
#Nash=pd.concat([Nash,CAMELS_516],axis=1)            
    #Obs_Q_cms=pd.read_csv("/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/01350140/cat-1.csv",parse_dates=True,index_col=0)        