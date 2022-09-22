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
DataDir="/media/west/Expansion/Select_PTBs/Data/"
DataOut="/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/"

# Read file with list of 516 CAMELS - remaining CAMELS are uncertain in terms of area
CAMELS_list_516="/home/west/Projects/CAMELS/camels_basin_list_516.txt"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id': str})
CAMELS_516=CAMELS_516.set_index(['hru_id'])   


#7)  Add NWM 2.1 retrospective since there is a large number of sites (#7000) - 2010-2018
file=DataDir+"/NWM_21_results/191118_NWMV21_FullRouting_FinalRetro_2010_2018_Stats.Rdata"
retrospective = pyreadr.read_r(file) # also works for Rds

stats_str=retrospective['stats_str']
stats_qmean=retrospective['stats_qmean']
stats_str=stats_str.set_index(['site_no']) 
stats_str.index.name='gage_id'
stats_qmean=stats_qmean.set_index(['site_no']) 
stats_qmean.index.name='gage_id'

#retrospective_df=retrospective_df.set_index('site_no', inplace=True)
stats_str21=stats_str[stats_str['tag']=='NWMV21_FinalRetro']
stats_str20=stats_str[stats_str['tag']=='NWMV20_FinalRetro']

  
# Add NWM 2.1 calib/valid 2010-2018
file=DataDir+"/NWM_21_results/v21_calib_valid_statistics_2008_2016.Rdata"
validcalib = pyreadr.read_r(file) # also works for Rds
CalibValidStat=validcalib['CalibValidStat']
CalibValidStat=CalibValidStat.set_index(['gage_id']) 

NoRean=[]
NoCalib=[]
for i in range (0,len(CAMELS_516)):    
    hru_id=CAMELS_516.index[i]
    outfolder=DataOut+"/"+hru_id+"/Validation/"
    if not os.path.exists(outfolder): os.mkdir(outfolder)  
    

    if(hru_id in stats_qmean.index):
        stats_qmean.loc[hru_id].to_csv(DataOut+"/"+hru_id+"/Validation/rean_qmean.csv")
        stats_str21.loc[hru_id].to_csv(DataOut+"/"+hru_id+"/Validation/rean_stats_21.csv")
        stats_str20.loc[hru_id].to_csv(DataOut+"/"+hru_id+"/Validation/rean_stats_20.csv")
    else: 
        NoRean.append(hru_id)
        print ("No reanalysis " + hru_id)
    if(hru_id in CalibValidStat.index):        
        CalibValidStat.loc[hru_id].to_csv(DataOut+"/"+hru_id+"/Validation/calib_valid_stats_21.csv")
    else: 
        NoCalib.append(hru_id)
        print ("No Validation " + hru_id)

np.savetxt(DataOut+"NoReanalysis.csv", NoRean, delimiter=",", fmt='%s')
np.savetxt(DataOut+"NoCalibration.csv", NoCalib, delimiter=",", fmt='%s')

