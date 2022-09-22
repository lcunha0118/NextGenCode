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
Hydrofabrics_folder="/home/west/s3-bucket/hydrofabric/CAMELS/"
DEM_folder="/media/west/Expansion/DEM/"
 
# Read file with list of 516 CAMELS - remaining CAMELS are uncertain in terms of area
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id': str})
CAMELS_516=CAMELS_516.set_index(['hru_id'])   

CAMELS_names_file="/home/west/Projects/CAMELS/Attributes/camels_attributes_v2.0/camels_name.txt"
CAMELS_names=pd.read_csv(CAMELS_names_file, sep = ';',dtype={'gauge_id': str,'huc_02': str})
CAMELS_names=CAMELS_names.set_index(['gauge_id']) 

#  File contains ID, p_mean, pet_mean,aridity,p_seasonality,frac_snow_daily,high_prec_freq,high_prec_dur
#high_prec_timing,low_prec_freq,low_prec_dur,low_prec_timing
CAMELS_clim_file="/home/west/Projects/CAMELS/Attributes/camels_attributes_v2.0/camels_clim.txt"
CAMELS_clim=pd.read_csv(CAMELS_clim_file, sep = ';',dtype={'gauge_id': str,'huc_02': str})
CAMELS_clim=CAMELS_clim.set_index(['gauge_id']) 

CAMELS_516=CAMELS_516.append(pd.DataFrame(index=['HUC01'])) 
CAMELS_names=CAMELS_names.append(pd.DataFrame([['01','HUC01']], columns=['huc_02','gauge_name'],index=['HUC01']))

Hydrofabrics_list=[]

hru_id=CAMELS_516.index[0]
Hydrofabrics=Hydrofabrics_folder+"/gage_"+hru_id+"/spatial/catchment_data.geojson"
gdf = gpd.read_file(Hydrofabrics) 
gdf["gauge_id"]=hru_id
gdf = gdf.dissolve()
for i in range (1,len(CAMELS_516)):  
    hru_id=CAMELS_516.index[i]

    Hydrofabrics=Hydrofabrics_folder+"/gage_"+hru_id+"/spatial/catchment_data.geojson"
    # Data might not exist yet, so just run if data was successfully downloaded
    if not os.path.exists(Hydrofabrics):
        print ("Error - Hydrofabrics does not exist " + hru_id)
    else:
        #Hydrofabrics_list.append(Hydrofabrics)
        pol_data = gpd.read_file(Hydrofabrics) 
        pol_data["gauge_id"]=hru_id
        pol_data = pol_data.dissolve()
        gdf = pd.concat([gdf,pol_data]).pipe(gpd.GeoDataFrame)
        
gdf=gdf.set_index(['gauge_id'])     
gdf = pd.concat([gdf,CAMELS_clim],axis=1,join="inner")          
gdf.to_file(Hydrofabrics_folder +'Merged_516CAMELS.shp')


gdf[(gdf['aridity']<0.5) & (gdf['frac_snow']<0.02)].to_file(Hydrofabrics_folder +'Very_Wet_nosnow_CAMELS.shp')

gdf[(gdf['aridity']<1) & (gdf['frac_snow']<0.02)].to_file(Hydrofabrics_folder +'Wet_nosnow_CAMELS.shp')

        
        