#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 08:32:28 2021

@author: west
"""

import pandas as pd

# Read file with list of 516 CAMELS - remaining CAMELS are uncertain in terms of area
CAMELS_list_516="/home/west/Projects/CAMELS/camels_basin_list_516.txt"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id': str})
CAMELS_516=CAMELS_516.set_index(['hru_id'])   
CAMELS_516.index.name="gage_id"

DataOut="/home/west/Projects/CAMELS/PerBasin3/data_CAMELS/"

area_issues_file='/home/west/Projects/CAMELS/PerBasin3/Area_issue.csv'
no_reanalysis_file=DataOut+"NoReanalysis.csv"
no_calib_file=DataOut+"NoCalibration.csv"

area_issues=pd.read_csv(area_issues_file,dtype={'gage_id': str})
area_issues=area_issues.set_index('gage_id')   
no_reanalysis=pd.read_csv(no_reanalysis_file,dtype=str,header=None)
no_reanalysis=no_reanalysis.set_index([no_reanalysis.columns[0]])   
no_reanalysis.index.name="gage_id"
no_calib=pd.read_csv(no_calib_file,dtype=str,header=None)
no_calib=no_calib.set_index([no_calib.columns[0]])   
no_calib.index.name="gage_id"

all_issues=pd.concat([area_issues,no_reanalysis,no_calib])
Drop1=CAMELS_516.drop(all_issues.index)
len(Drop1)



