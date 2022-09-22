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

# CAMELS_516=CAMELS_516.append(pd.DataFrame(index=['HUC01'])) 
# CAMELS_names=CAMELS_names.append(pd.DataFrame([['01','HUC01']], columns=['huc_02','gauge_name'],index=['HUC01']))



hru_id=CAMELS_516.index[0]
Folder=CAMELS_516.iloc[0]['Folder_CAMELS']
Hydrofabrics=Hydrofabrics_folder+"/"+Folder+"/spatial/catchment_data.geojson"
gdf = gpd.read_file(Hydrofabrics) 
gdf["gauge_id"]=hru_id
gdf_dissolved = gdf.dissolve()
for i in range (1,len(CAMELS_516)):  
    hru_id=CAMELS_516.index[i]
    Folder=CAMELS_516.iloc[i]['Folder_CAMELS']
    Hydrofabrics=Hydrofabrics_folder+"/"+Folder+"/spatial/catchment_data.geojson"
    # Data might not exist yet, so just run if data was successfully downloaded
    if not os.path.exists(Hydrofabrics):
        print ("Error - Hydrofabrics does not exist " + hru_id)
    else:
        #Hydrofabrics_list.append(Hydrofabrics)
        pol_data = gpd.read_file(Hydrofabrics) 
        pol_data["gauge_id"]=hru_id
        pol_data_dissolve = pol_data.dissolve()
        gdf_dissolved = pd.concat([gdf_dissolved,pol_data_dissolve]).pipe(gpd.GeoDataFrame)
        gdf = pd.concat([gdf,pol_data]).pipe(gpd.GeoDataFrame)
gdf_dissolved=gdf_dissolved.set_index(['gauge_id'])     
gdf_dissolved = pd.concat([gdf_dissolved,CAMELS_clim],axis=1,join="inner")          
gdf_dissolved.to_file(Hydrofabrics_folder +'Merged_516CAMELS.shp')

#gdf=gdf.set_index(['gauge_id'])     
#gdf = pd.concat([gdf,CAMELS_clim],axis=1,join="inner")          
gdf.to_file(Hydrofabrics_folder +'Merged_516CAMELS_cat.shp')

#####################################################################
# For Join start here
gdf = gpd.read_file(Hydrofabrics_folder +'Merged_516CAMELS_cat.shp') 

SNOTEL=pd.read_csv("/media/west/Expansion/Projects/SNOTEL/snotel_site_data.orig.csv")
SNOTEL_gf = gpd.GeoDataFrame(
    SNOTEL, geometry=gpd.points_from_xy(SNOTEL.XLONG_M, SNOTEL.XLAT_M))
SNOTEL_gf = SNOTEL_gf.set_crs("EPSG:4326")
SNOTEL_gf.to_file(Hydrofabrics_folder +'SNOTEL.shp')
SNOTEL_join = gpd.sjoin(gdf, SNOTEL_gf, how="inner")
SNOTEL_join.to_file(Hydrofabrics_folder +'SNOTEL_JOIN.shp')
SNOTEL_join.to_csv(Hydrofabrics_folder +'SNOTEL_JOIN.csv')

SCAN=pd.read_csv("/media/west/Expansion/Projects/SM/nsmn_SCAN_nwm_collocations.txt", delimiter=r"\s+")
SCAN_gf = gpd.GeoDataFrame(
    SCAN, geometry=gpd.points_from_xy(SCAN.obs_lon, SCAN.obs_lat))
SCAN_join = gpd.sjoin(gdf, SCAN_gf, how="inner")
SCAN_join.to_file(Hydrofabrics_folder +'SCAN_JOIN.shp')
SCAN_join.to_csv(Hydrofabrics_folder +'SCAN_JOIN.csv')

USCRN=pd.read_csv("/media/west/Expansion/Projects/SM/nsmn_USCRN_nwm_collocations.txt", delimiter=r"\s+")
USCRN_gf = gpd.GeoDataFrame(
    USCRN, geometry=gpd.points_from_xy(USCRN.obs_lon, USCRN.obs_lat))
USCRN_join = gpd.sjoin(gdf, USCRN_gf, how="inner")
USCRN_join.to_file(Hydrofabrics_folder +'USCRN_JOIN.shp')
USCRN_join.to_csv(Hydrofabrics_folder +'USCRN_JOIN.csv')

TxDot=pd.read_csv("/media/west/Expansion/Projects/SM/TxSON_v1_5 (1)/ESSD/metadataTxSON.csv")
TxDot_gf = gpd.GeoDataFrame(
    TxDot, geometry=gpd.points_from_xy(TxDot.LON, TxDot.LAT))
TxDot_gf = TxDot_gf.set_crs("EPSG:4326")
TxDot_gf.to_file(Hydrofabrics_folder +'TxDot.shp')
TxDot_join = gpd.sjoin(gdf, TxDot_gf, how="inner")
TxDot_join.to_file(Hydrofabrics_folder +'TxDot_JOIN.shp')
TxDot_join.to_csv(Hydrofabrics_folder +'TxDot_JOIN.csv')
# CAMELS_516Selected_file="/home/west/Projects/CAMELS/Sensitivity_analysis_basin_selection/Sens_analysis_basins.csv"
# CAMELS_516Selected=pd.read_csv(CAMELS_516Selected_file,dtype={'hru_id_CAMELS': str})
# CAMELS_516Selected=CAMELS_516Selected.set_index(['hru_id_CAMELS'])  

# hru_id=CAMELS_516Selected.index[0]
# Folder=CAMELS_516Selected.iloc[0]['Folder_CAMELS']
# Hydrofabrics=Hydrofabrics_folder+"/"+Folder+"/spatial/catchment_data.geojson"
# gdf = gpd.read_file(Hydrofabrics) 
# gdf["gauge_id"]=hru_id
# gdf = gdf.dissolve()
# for i in range (1,len(CAMELS_516Selected)):  
#     hru_id=CAMELS_516Selected.index[i]
#     Folder=CAMELS_516Selected.iloc[i]['Folder_CAMELS']
#     Hydrofabrics=Hydrofabrics_folder+"/"+Folder+"/spatial/catchment_data.geojson"
#     # Data might not exist yet, so just run if data was successfully downloaded
#     if not os.path.exists(Hydrofabrics):
#         print ("Error - Hydrofabrics does not exist " + hru_id)
#     else:
#         #Hydrofabrics_list.append(Hydrofabrics)
#         pol_data = gpd.read_file(Hydrofabrics) 
#         pol_data["gauge_id"]=hru_id
#         pol_data = pol_data.dissolve()
#         gdf = pd.concat([gdf,pol_data]).pipe(gpd.GeoDataFrame)
        
# gdf=gdf.set_index(['gauge_id'])     
# gdf = pd.concat([gdf,CAMELS_clim],axis=1,join="inner")          
# gdf.to_file(Hydrofabrics_folder +'Merged_516CAMELSSelected2.shp')



# gdf[(gdf['aridity']<0.5) & (gdf['frac_snow']<0.02)].to_file(Hydrofabrics_folder +'Very_Wet_nosnow_CAMELS.shp')

# gdf[(gdf['aridity']<1) & (gdf['frac_snow']<0.02)].to_file(Hydrofabrics_folder +'Wet_nosnow_CAMELS.shp')

        
        