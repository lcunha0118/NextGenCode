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
import zipfile


Hydrofabrics_folder="/media/west/Expansion/hydrofabrics/"


VPU=pd.read_csv(Hydrofabrics_folder+"VPU_hydrofabrics.txt")

for i in range (0,len(VPU)):  
    vpu_id=VPU.iloc[i]['vpu']
    Output_folder=Hydrofabrics_folder+"/"+vpu_id+"/"
    if not os.path.exists(Output_folder): os.mkdir(Output_folder)
    zip_file=Output_folder+"nextgen_"+vpu_id+".zip"
    gpkg_file=Output_folder+"nextgen_"+vpu_id+".gpkg" 
    if not os.path.exists(zip_file): 
        str_sub="aws s3 cp s3://nextgen-hydrofabric/v1.0/nextgen_"+vpu_id+".zip " +Output_folder   
        out=subprocess.call(str_sub,shell=True)
    if not os.path.exists(gpkg_file): 
        str_sub="aws s3 cp s3://nextgen-hydrofabric/v1.0/nextgen_"+vpu_id+".gpkg " +Output_folder   
        out=subprocess.call(str_sub,shell=True)
    
    with zipfile.ZipFile(Output_folder+"nextgen_"+vpu_id+".zip","r") as zip_ref:
        zip_ref.extractall(Output_folder)
        # Data might not exist yet, so just run if data was successfully downloaded
    str_sub="ogr2ogr -f \"GeoJSON\" "+Output_folder+"/flowpaths.geojson " +Output_folder+"/nextgen_"+vpu_id+".gpkg flowpaths"
    out=subprocess.call(str_sub,shell=True)
    str_sub="ogr2ogr -f \"GeoJSON\" "+Output_folder+"/flowpaths_4269.geojson " +Output_folder+"/flowpaths.geojson -s_srs EPSG:5070 -t_srs EPSG:4269"
    out=subprocess.call(str_sub,shell=True)
    str_sub="ogr2ogr -f \"GeoJSON\" "+Output_folder+"/catchment_data_4269.geojson " +Output_folder+"/catchment_data.geojson -s_srs EPSG:5070 -t_srs EPSG:4269"
    out=subprocess.call(str_sub,shell=True)