#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 11:32:28 2021

@author: west
"""


"""

author: lcunha

Function to generate namelist file for NOAH-modular surface bmi
https://github.com/NOAA-OWP/noah-mp-modular

Reads hydrofabrics
Alter specific parameters
 
"""

import pandas as pd
import os
import geopandas as gp
import glob
import matplotlib.pyplot as plt

# for example
Hyd_folder="/home/west/Projects/CAMELS/PerBasin4/"
CAMELS_list_516="/home/west/Projects/CAMELS/camels_basin_list_516.txt"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id': str})
CAMELS_516=CAMELS_516.set_index(['hru_id'])   


outputfolder='/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/'


for i in range (516,len(CAMELS_516)):    
    hru_id=CAMELS_516.index[i]
    hru_id='HUC01'
    catchments=outputfolder+"/"+hru_id+'/catchment_data.geojson'
    CFE_Config=outputfolder+"/"+hru_id+'/CFE/'
    Param_all=pd.DataFrame()
     
    zones = gp.GeoDataFrame.from_file(catchments)
    for index,row in zones.iterrows():
        catstr=row[0]

        DatFile=os.path.join(CFE_Config,catstr+"_bmi_config_cfe_pass.txt")
        print (DatFile)
        
        Param_temp=pd.read_csv(DatFile,delimiter="=",header=0,index_col=0)
        Param_temp=Param_temp.rename(columns={'BMI':catstr})
        Param_all=pd.concat([Param_all,Param_temp],axis=1)

    #From original Config file
    soil_params_depth=2.0
    soil_params_b=4.05
    soil_params_mult=1000.0
    soil_params_satdk=0.00000338
    soil_params_satpsi=0.355
    soil_params_slope=1.0
    soil_params_smcmax=0.439
    soil_params_wltsmc=0.066
    max_gw_storage=16.0
    Cgw=0.01
    expon=6.0
    gw_storage=50
    alpha_fc=0.33
    soil_storage=66.7
    K_nash=0.03
    K_lf=0.01
    nash_storage=0.0,0.0
    giuh_ordinates=[0.06,0.51,0.28,0.12,0.03]
    
    plt.rcParams["figure.figsize"] = (15,20)
    fig, ax_compare = plt.subplots(4, 3) #Create the plot for this zone
    
    
    #hist=np.histogram(pd.to_numeric(Param_all.loc['soil_params.b']).values, bins=range(0,10))
    #CDF=pd.DataFrame({'Nelem':hist[0].T, 'soil_params.b':hist[1][1:].T})
    #CDF['Freq']=CDF['Nelem']/sum(CDF['Nelem'])
    #ax_compare[0,0].bar(CDF['soil_params.b'],CDF['Freq'])

    ax_compare[0,0].hist(pd.to_numeric(Param_all.loc['soil_params.b']).values,bins=10) #Plot obs data on comparison figure
    ax_compare[0,0].vlines(soil_params_b,[0],[10000],'r')
    ax_compare[0,0].set_xlabel ('soil_params_b'); 
    ax_compare[0,0].set_ylabel('Number cat')
    Num_zero="#zero="+str(sum(pd.to_numeric(Param_all.loc['soil_params.b']).values<0))
    ax_compare[0,0].text(soil_params_b,9000,Num_zero,fontsize=12)
    
      

    ax_compare[0,1].hist(pd.to_numeric(Param_all.loc['soil_params.satdk']).values,bins=10)
    ax_compare[0,1].vlines(soil_params_satdk,[0],[10000],'r')
    ax_compare[0,1].set_xlabel ('soil_params_satdk'); 
    ax_compare[0,1].set_ylabel('Number cat')
    Num_zero="#zero="+str(sum(pd.to_numeric(Param_all.loc['soil_params.satdk']).values<0))
    ax_compare[0,1].text(soil_params_satdk,9000,Num_zero,fontsize=12)
     

    ax_compare[0,2].hist(pd.to_numeric(Param_all.loc['soil_params.satpsi']).values,bins=10)
    ax_compare[0,2].vlines(soil_params_satpsi,[0],[10000],'r')
    ax_compare[0,2].set_xlabel ('soil_params_satpsi'); 
    ax_compare[0,2].set_ylabel('Number cat')
    Num_zero="#zero="+str(sum(pd.to_numeric(Param_all.loc['soil_params.satpsi']).values<0))
    ax_compare[0,2].text(soil_params_satpsi,9000,Num_zero,fontsize=12)
    

    ax_compare[1,0].hist(pd.to_numeric(Param_all.loc['soil_params.slop']).values,bins=10)
    ax_compare[1,0].vlines(soil_params_slope,[0],[10000],'r')
    ax_compare[1,0].set_xlabel ('soil_params_slope'); 
    ax_compare[1,0].set_ylabel('Number cat')
    Num_zero="#zero="+str(sum(pd.to_numeric(Param_all.loc['soil_params.slop']).values<0))
    ax_compare[1,0].text(soil_params_slope,9000,Num_zero,fontsize=12)
     
    
    ax_compare[1,1].hist(pd.to_numeric(Param_all.loc['soil_params.smcmax']).values,bins=10)
    ax_compare[1,1].vlines(soil_params_smcmax,[0],[10000],'r')
    ax_compare[1,1].set_xlabel ('soil_params_smcmax'); 
    ax_compare[1,1].set_ylabel('Number cat')
    Num_zero="#zero="+str(sum(pd.to_numeric(Param_all.loc['soil_params.smcmax']).values<0))
    ax_compare[1,1].text(soil_params_smcmax,9000,Num_zero,fontsize=12)
    
    refkdt=3 # As described in CFE document
    ax_compare[1,2].hist(pd.to_numeric(Param_all.loc['refkdt']).values,bins=10)
    ax_compare[1,2].vlines(soil_params_smcmax,[0],[10000],'r')
    ax_compare[1,2].set_xlabel ('refkdt'); 
    ax_compare[1,2].set_ylabel('Number cat')
    Num_zero="#zero="+str(sum(pd.to_numeric(Param_all.loc['refkdt']).values<0))
    ax_compare[1,2].text(refkdt,9000,Num_zero,fontsize=12)
    
    ax_compare[2,0].hist(pd.to_numeric(Param_all.loc['soil_params.mult']).values,bins=10)
    ax_compare[2,0].vlines(soil_params_mult,[0],[10000],'r')
    ax_compare[2,0].set_xlabel ('soil_params_mult '); 
    ax_compare[2,0].set_ylabel('Number cat')
    Num_zero="#zero="+str(sum(pd.to_numeric(Param_all.loc['soil_params.mult']).values<0))
    ax_compare[2,0].text(soil_params_mult,9000,Num_zero,fontsize=12)
    

    ax_compare[2,1].hist(pd.to_numeric(Param_all.loc['soil_params.wltsmc']).values,bins=10)
    ax_compare[2,1].vlines(soil_params_wltsmc,[0],[10000],'r')
    ax_compare[2,1].set_xlabel ('soil_params_wltsmc'); 
    ax_compare[2,1].set_ylabel('Number cat')
    Num_zero="#zero="+str(sum(pd.to_numeric(Param_all.loc['soil_params.wltsmc']).values<0))
    ax_compare[2,1].text(soil_params_wltsmc,9000,Num_zero,fontsize=12)
    

    ax_compare[2,2].hist(pd.to_numeric(Param_all.loc['max_gw_storage']).values,bins=10)
    ax_compare[2,2].vlines(max_gw_storage,[0],[10000],'r')
    ax_compare[2,2].set_xlabel ('max_gw_storage'); 
    ax_compare[2,2].set_ylabel('Number cat')
    Num_zero="#zero="+str(sum(pd.to_numeric(Param_all.loc['max_gw_storage']).values<0))
    ax_compare[2,2].text(max_gw_storage,9000,Num_zero,fontsize=12)
    

    ax_compare[3,0].hist(pd.to_numeric(Param_all.loc['Cgw']).values,bins=10)
    ax_compare[3,0].vlines(Cgw,[0],[10000],'r')
    ax_compare[3,0].set_xlabel ('Cgw'); 
    ax_compare[3,0].set_ylabel('Number cat')
    Num_zero="#zero="+str(sum(pd.to_numeric(Param_all.loc['Cgw']).values<0))
    ax_compare[3,0].text(Cgw,9000,Num_zero,fontsize=12)
    

    ax_compare[3,1].hist(pd.to_numeric(Param_all.loc['expon']).values,bins=10)
    ax_compare[3,1].vlines(expon,[0],[10000],'r')
    ax_compare[3,1].set_xlabel ('expon'); 
    ax_compare[3,1].set_ylabel('Number cat')
    Num_zero="#zero="+str(sum(pd.to_numeric(Param_all.loc['expon']).values<0))
    ax_compare[2,1].text(expon,9000,Num_zero,fontsize=12)
    
    

    for i in range(0,len(Param_all.columns)):
        List_str=Param_all.loc['giuh_ordinates'].iloc[i].split(",")
        List_float=[float(i) for i in List_str]
        a=0
        List_float_accum=[]
        List_float_accum.append(a)
        for j in List_float:
            a=a+j
            List_float_accum.append(a)
        #print (List_float_accum)
        ax_compare[3,2].plot(range(0,len(List_float_accum)),List_float_accum,'y')
    
    
    a=0
    List_float_accum=[]
    List_float_accum.append(a)    
    giuh_ordinates
    for j in giuh_ordinates:
        a=a+j
        List_float_accum.append(a)        
    ax_compare[3,2].plot(range(0,len(List_float_accum)),List_float_accum,'b')  
    ax_compare[3,2].set_xlabel ('hours'); 
    ax_compare[3,1].set_ylabel('GIUH-Accum dist')
    
    output_figure=outputfolder+"/"+hru_id+"CFE_params.png"
    fig.savefig(output_figure, bbox_inches='tight')   
