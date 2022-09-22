#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  6 14:43:26 2021

@author: lcunha
"""

import os
import geopandas as gpd
import subprocess
import pandas as pd

# for example
Hydrofabrics_folder="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"

 
# Read file with list of 516 CAMELS - remaining CAMELS are uncertain in terms of area
CAMELS_list_516="/home/west/Projects/CAMELS/CAMELS_Files_Ngen//CAMELS_v2_list.csv"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id_CAMELS': str})
CAMELS_516=CAMELS_516.set_index(['hru_id_CAMELS'])  


CAMELS_names_file="/home/west/Projects/CAMELS/Attributes/camels_attributes_v2.0/camels_name.txt"
CAMELS_names=pd.read_csv(CAMELS_names_file, sep = ';',dtype={'gauge_id': str,'huc_02': str})
CAMELS_names=CAMELS_names.set_index(['gauge_id']) 

#  File contains ID, p_mean, pet_mean,aridity,p_seasonality,frac_snow_daily,high_prec_freq,high_prec_dur
#high_prec_timing,low_prec_freq,low_prec_dur,low_prec_timing
CAMELS_clim_file="/home/west/Projects/CAMELS/Attributes/camels_attributes_v2.0/camels_clim.txt"
CAMELS_clim=pd.read_csv(CAMELS_clim_file, sep = ';',dtype={'gauge_id': str,'huc_02': str})
CAMELS_clim=CAMELS_clim.set_index(['gauge_id']) 

for i in range (0,len(CAMELS_516)):  
    

    hru_id=CAMELS_516.index[i]
    Folder=CAMELS_516.iloc[i]['Folder_CAMELS']
    #Origin="/home/west/Projects/CAMELS/nwm_v2.1_chrt_camels513_csv/csv/nwm_v2.1_chrt."+hru_id+".csv"
    Origin=Hydrofabrics_folder+"/"+Folder+"/nwm_v2.1_chrt."+hru_id+".csv"
    Destination=Hydrofabrics_folder+"/"+Folder+"/Validation/"
    #str_sub="cp " +Origin + " " + Destination    
    #out=subprocess.call(str_sub,shell=True)     
    str_sub="rm " +Origin   
    out=subprocess.call(str_sub,shell=True)         
        