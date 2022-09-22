#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 08:57:12 2022

@author: west
"""

import rasterio
from rasterio.merge import merge
from rasterio.plot import show
import generate_giuh_per_basin_params_withUnits_sca as GIUH
import glob
import os

# File and folder paths
DEM_Folder="/media/west/Expansion/DEM/"
out_fp=DEM_Folder+"hucALL-res-190cpdsave1.tif"
file_name_90cpdsave="huc*-res-190cpdsave1.tif"# Make a search criteria to select the  files
re_run=0

q = os.path.join(DEM_Folder, file_name_90cpdsave)
dem_fps = glob.glob(q)
print(dem_fps)
src_files_to_mosaic = []

if (not os.path.exists(out_fp))  | (re_run==1):
        
    for fp in dem_fps:
        src = rasterio.open(fp)
        src_files_to_mosaic.append(src)
       
    mosaic, out_trans = merge(src_files_to_mosaic)
    out_meta = src.meta.copy() 
    out_meta.update({"driver": "GTiff",
                     "height": mosaic.shape[1],
                     "width": mosaic.shape[2],
                     "transform": out_trans,
                     "crs": "+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs "
                     }
                    )
    with rasterio.open(out_fp, "w", **out_meta) as dest:
        dest.write(mosaic)
        
HUC_str="ALL"
cat_file="/media/west/Expansion/hydrofabrics/CONUS/conus/catchment_data.geojson"    
Atrib_file="/media/west/Expansion/hydrofabrics/CONUS/conus/cfe_noahowp_attributes.csv"
Output_folder_hyd="/home/west/conus/"
GIUH.generate_giuh_per_basin_withUnits(HUC_str,cat_file,out_fp,Atrib_file,Output_folder_hyd)