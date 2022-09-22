#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 10:58:42 2022

@author: west
"""

import os
import geopandas as gpd
import subprocess
import pandas as pd

# By 
HUC_File = "/home/west/Downloads/HUC2.shp"
HUC_data = gpd.read_file(HUC_File) 

for i in range(0,len(HUC_data.HUC2)):
    HUC=HUC_data.HUC2.iloc[i]
    HUC_temp=HUC_data[HUC_data.HUC2==HUC]
    pol_data_buf = HUC_temp.buffer(0.1)
    HUC_File = "/media/west/Expansion/DEM/HUC_"+HUC+".shp"
    pol_data_buf.to_file(HUC_File)


Hydrof_directory="