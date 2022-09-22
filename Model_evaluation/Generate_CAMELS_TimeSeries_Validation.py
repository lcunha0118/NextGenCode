#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 10:29:20 2021

@author: west
"""
import pyreadr
import pandas as pd
import numpy as np
import os
import subprocess
DataDir="/media/west/Expansion/Select_PTBs/Data/"
DataOut="/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/"

# Read file with list of 516 CAMELS - remaining CAMELS are uncertain in terms of area
CAMELS_list_516="/home/west/Projects/CAMELS/camels_basin_list_516.txt"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id': str})
CAMELS_516=CAMELS_516.set_index(['hru_id'])   

CAMELS_names_file="/home/west/Projects/CAMELS/Attributes/camels_attributes_v2.0/camels_name.txt"
CAMELS_names=pd.read_csv(CAMELS_names_file, sep = ';',dtype={'gauge_id': str,'huc_02': str})
CAMELS_names=CAMELS_names.set_index(['gauge_id']) 

CAMELS_516=CAMELS_516.append(pd.DataFrame(index=['HUC01'])) 
CAMELS_names=CAMELS_names.append(pd.DataFrame([['01','HUC01']], columns=['huc_02','gauge_name'],index=['HUC01']))

Dataset=["model_output_daymet"]
DataIn=["/media/west/Expansion/Backup/Projects/CAMELS_Timeseries/model_output_daymet/model_output/flow_timeseries/daymet/"]


Dataset=["model_output_maurer"]
DataIn=["/media/west/Expansion/Backup/Projects/CAMELS_Timeseries/model_output_maurer/model_output/flow_timeseries/maurer/"]

Dataset=["model_output_nldas"]
DataIn=["/media/west/Expansion/Backup/Projects/CAMELS_Timeseries/model_output_nldas/model_output/flow_timeseries/nldas/"]

for idataset in range (0,len(Dataset)):    
    for i in range (0,len(CAMELS_516)):    
        hru_id=CAMELS_516.index[i]
        HUC2=CAMELS_names.loc[hru_id]['huc_02']
        
        Directory_in=DataIn[idataset]+HUC2+"/"
        Directory_out=DataOut+hru_id+"/Validation/"+Dataset[idataset]
        if not os.path.exists(Directory_out): os.mkdir(Directory_out)  
        str_sub="cp -rf "+Directory_in+hru_id + "* " + Directory_out
        out=subprocess.call(str_sub,shell=True)
        print ("Copy " + DataIn[idataset] + " " + hru_id)


