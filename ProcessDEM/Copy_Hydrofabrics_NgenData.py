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
CAMELS_list_516="/home/west/Projects/CAMELS/camels_basin_list_516.txt"
Input_folder="/home/west/Projects/CAMELS/PerBasin3/"
Output_folder="/home/west/Projects/CAMELS/PerBasin3/data_CAMELS/"

if not os.path.exists(Output_folder): os.mkdir(Output_folder)

# # Read file using gpd.read_file()
# pt_data = gpd.read_file(CAMELS_points) 

 
# Read file with list of 516 CAMELS - remaining CAMELS are uncertain in terms of area
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id': str})
CAMELS_516=CAMELS_516.set_index(['hru_id'])   

CAMELS_names_file="/home/west/Projects/CAMELS/Attributes/camels_attributes_v2.0/camels_name.txt"
CAMELS_names=pd.read_csv(CAMELS_names_file, sep = ';',dtype={'gauge_id': str,'huc_02': str})
CAMELS_names=CAMELS_names.set_index(['gauge_id']) 

for i in range (0,len(CAMELS_516)):    
    hru_id=CAMELS_516.index[i]
    print (hru_id)
    InputFolder=Input_folder+"/"+hru_id+"/"
    Outputfolder=Output_folder+"/"+hru_id+"/"
    str_sub="ogr2ogr -f \"GeoJSON\" "+Outputfolder+"aggregated_catchments.geojson " +InputFolder+"gage_" + hru_id + ".gpkg aggregated_catchments"
    #str_sub="ogr2ogr -f \"ESRI Shapefile\" "+outfolder+"gage_"+hru_id+".gpkg"
    out=subprocess.call(str_sub,shell=True)
    #str_sub="rm "+outfolder+"gage_0"+hru_id+".gpkg"
    #out=subprocess.call(str_sub,shell=True)
    
    str_sub="ogr2ogr -f \"GeoJSON\" "+Outputfolder+"aggregated_flowpaths.geojson " +InputFolder+"gage_" + hru_id + ".gpkg aggregated_flowpaths"
    #str_sub="ogr2ogr -f \"ESRI Shapefile\" "+outfolder+"gage_"+hru_id+".gpkg"
    out=subprocess.call(str_sub,shell=True)
    #str_sub="rm "+outfolder+"gage_0"+hru_id+".gpkg"
#out=subprocess.call(str_sub,shell=True)

    
