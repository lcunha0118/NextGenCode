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
from shapely.geometry import Point
from datetime import datetime,timedelta
# for example
Hydrofabrics_folder="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"

 
# Read file with list of 516 CAMELS - remaining CAMELS are uncertain in terms of area
#CAMELS_list_516="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/CAMELS_v3_complete.csv"

CAMELS_list_516="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/CAMELS_runs8.csv"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id_CAMELS': str})
CAMELS_516=CAMELS_516.set_index(['hru_id_CAMELS'])
#CAMELS_516=CAMELS_516[CAMELS_516['SA_analysis']==1]

CAMELS_516["N_Nexus"]=-9

CAMELS_names_file="/home/west/Projects/CAMELS/Attributes/camels_attributes_v2.0/camels_name.txt"
CAMELS_names=pd.read_csv(CAMELS_names_file, sep = ';',dtype={'gauge_id': str,'huc_02': str})
CAMELS_names=CAMELS_names.set_index(['gauge_id']) 

CAMELS_516=pd.concat([CAMELS_516,CAMELS_names[['huc_02','gauge_name']]],axis=1,join="inner")

#  File contains ID, p_mean, pet_mean,aridity,p_seasonality,frac_snow_daily,high_prec_freq,high_prec_dur
#high_prec_timing,low_prec_freq,low_prec_dur,low_prec_timing
CAMELS_clim_file="/home/west/Projects/CAMELS/Attributes/camels_attributes_v2.0/camels_clim.txt"
CAMELS_clim=pd.read_csv(CAMELS_clim_file, sep = ';',dtype={'gauge_id': str,'huc_02': str})
CAMELS_clim=CAMELS_clim.set_index(['gauge_id']) 
 
CAMELS_516=pd.concat([CAMELS_516,CAMELS_clim],axis=1,join="inner")
points = []
for lon, lat in zip(CAMELS_516["Long"], CAMELS_516["Lat"]):
    points.append(Point(lon, lat))

CAMELS_516["geometry"] = points
CAMELS_516 = gpd.GeoDataFrame(CAMELS_516)


#points_hydrofabric=CAMELS_516.copy()
#points_hydrofabric['geometry']=points_hydrofabric['geometry'].centroid 

RFC_file="/home/west/Projects/GIS/rf12ja05/rf12ja05.shp"
RFC = gpd.GeoDataFrame.from_file(RFC_file)
Hydrofabric_RFC=gpd.sjoin(CAMELS_516,RFC.to_crs('EPSG:4326'), how="inner", op="intersects")

#Hydrofabric_RFC = Hydrofabric_RFC.drop(['index_right'], axis=1)

Hydrofabric_RFC = Hydrofabric_RFC[['Folder_CAMELS','NCat', 'SA_analysis','NOAH_CFE', 'area_sqkm', 'p_mean', 'pet_mean',
       'p_seasonality', 'frac_snow', 'aridity', 'high_prec_freq', 'high_prec_dur',
       'high_prec_timing', 'low_prec_freq', 'low_prec_dur', 'low_prec_timing', 'geometry',
        'BASIN_ID']]
Hydrofabric_RFC=Hydrofabric_RFC.rename(columns={'BASIN_ID':"RFC"})

physio_file="/home/west/Projects/GIS/physio_shp/physio.shp"
physio = gpd.GeoDataFrame.from_file(physio_file)
Hydrofabric_RFC_physio=gpd.sjoin(Hydrofabric_RFC,physio.to_crs('EPSG:4326'))
Hydrofabric_RFC_physio=Hydrofabric_RFC_physio[['Folder_CAMELS','NCat', 'SA_analysis','NOAH_CFE', 'area_sqkm', 'p_mean', 'pet_mean',
       'p_seasonality', 'frac_snow', 'aridity', 'high_prec_freq', 'high_prec_dur',
       'high_prec_timing', 'low_prec_freq', 'low_prec_dur', 'low_prec_timing', 'geometry',
        'RFC','PROVCODE','DIVISION']]
Hydrofabric_RFC_physio=Hydrofabric_RFC_physio.rename(columns={'PROVCODE':"physio_PROVCODE"})
Hydrofabric_RFC_physio=Hydrofabric_RFC_physio.rename(columns={'DIVISION':"physio_DIVISION"})


eco_file="//home/west/Projects/GIS/us_eco_l3/us_eco_l3.shx"
eco = gpd.GeoDataFrame.from_file(eco_file)
Hydrofabric_RFC_physio_eco=gpd.sjoin(Hydrofabric_RFC_physio,eco.to_crs('EPSG:4326'))

Hydrofabric_RFC_physio_eco=Hydrofabric_RFC_physio_eco[['Folder_CAMELS','NCat', 'SA_analysis','NOAH_CFE', 'area_sqkm', 'p_mean', 'pet_mean',
       'p_seasonality', 'frac_snow', 'aridity', 'high_prec_freq', 'high_prec_dur',
       'high_prec_timing', 'low_prec_freq', 'low_prec_dur', 'low_prec_timing', 'geometry',
        'RFC','physio_PROVCODE','physio_DIVISION','US_L3CODE','US_L3NAME']]
Hydrofabric_RFC_physio_eco=Hydrofabric_RFC_physio_eco.rename(columns={'US_L3CODE':"ECO_L3CODE"})
Hydrofabric_RFC_physio_eco=Hydrofabric_RFC_physio_eco.rename(columns={'US_L3NAME':"ECO_L3NAME"})

clima_file="//home/west/Projects/GIS/other_climate_2007_koppen_geiger/other_climate_2007_koppen_geiger.shp"
clima = gpd.GeoDataFrame.from_file(clima_file)
Hydrofabric_RFC_physio_eco_clima=gpd.sjoin(Hydrofabric_RFC_physio_eco,clima.to_crs('EPSG:4326'))

Hydrofabric_RFC_physio_eco_clima=Hydrofabric_RFC_physio_eco_clima[['Folder_CAMELS','NCat', 'SA_analysis','NOAH_CFE', 'area_sqkm', 'p_mean', 'pet_mean',
       'p_seasonality', 'frac_snow', 'aridity', 'high_prec_freq', 'high_prec_dur',
       'high_prec_timing', 'low_prec_freq', 'low_prec_dur', 'low_prec_timing', 'geometry',
        'RFC','physio_PROVCODE','physio_DIVISION','ECO_L3CODE','ECO_L3NAME','climate']]


hlr_file="/home/west/Projects/GIS/hlrshape/hlrus.shp"
hlr = gpd.GeoDataFrame.from_file(hlr_file)
Hydrofabric_RFC_physio_eco_clima_hlr=gpd.sjoin(Hydrofabric_RFC_physio_eco_clima,hlr.to_crs('EPSG:4326'))
Hydrofabric_RFC_physio_eco_clima_hlr=Hydrofabric_RFC_physio_eco_clima_hlr[['Folder_CAMELS','NCat', 'SA_analysis','NOAH_CFE', 'area_sqkm', 'p_mean', 'pet_mean',
       'p_seasonality', 'frac_snow', 'aridity', 'high_prec_freq', 'high_prec_dur',
       'high_prec_timing', 'low_prec_freq', 'low_prec_dur', 'low_prec_timing', 'geometry',
        'RFC','physio_PROVCODE','physio_DIVISION','ECO_L3CODE','ECO_L3NAME','climate','HLR']]
#Hydrofabric_RFC_physio_eco_clima_hlr=Hydrofabric_RFC_physio_eco_clima_hlr.set_index(['gauge_id']) 
    
#Final_list=Hydrofabric_RFC_physio_eco_clima_hlr.loc[CAMELS_516.index]


Hydrofabric_RFC_physio_eco_clima_hlr['Available_data']=-9
for i in range(0,len(Hydrofabric_RFC_physio_eco_clima_hlr)):
    hru_id=Hydrofabric_RFC_physio_eco_clima_hlr.index[i]
    Folder=Hydrofabric_RFC_physio_eco_clima_hlr.iloc[i]['Folder_CAMELS']
    Obs_Q_file=Hydrofabrics_folder+"/"+Folder+"/Validation/usgs_hourly_flow_2007-2019_"+hru_id+".csv"
    Obs_Q_cms=pd.read_csv(Obs_Q_file,parse_dates=True,index_col=1)
    
    min_date=Obs_Q_cms.index.min()
    max_date=Obs_Q_cms.index.max()   
    Obs_Q_cms = Obs_Q_cms.groupby(level=0).first()
    min_date_plot=datetime(2007,10,1,0,0)
    #min_date_plot=datetime(2012,10,1,0,0)
    max_date_plot=datetime(2019,10,1,0,0)
    idx=pd.date_range(min_date_plot,max_date_plot,freq="H")
    Obs_Q_cms=Obs_Q_cms.reindex(idx,fill_value=-9)
    
    Obs_good=Obs_Q_cms.dropna()
    Obs_good=Obs_good[Obs_good['q_cms']>=0]
    Good_Data=100*len(Obs_good)/len(Obs_Q_cms)
    Hydrofabric_RFC_physio_eco_clima_hlr.at[hru_id,'Available_data']=Good_Data
    print (Good_Data)
    Nexus_file=Hydrofabrics_folder+"/"+Folder+"/spatial/nexus_data.geojson"
    pol_data = gpd.read_file(Nexus_file) 
    Hydrofabric_RFC_physio_eco_clima_hlr.at[hru_id,"N_Nexus"]=len(pol_data)

Hydrofabric_RFC_physio_eco_clima_hlr.to_csv(Hydrofabrics_folder+"Info_for_select_calibration.csv")
Hydrofabric_RFC_physio_eco_clima_hlr.to_file(Hydrofabrics_folder +'Info_for_select_calibration.shp')


HLR_unique=Hydrofabric_RFC_physio_eco_clima_hlr['HLR'].unique()
Selected_calibration=pd.DataFrame()
for i in HLR_unique:
    
    selected=Hydrofabric_RFC_physio_eco_clima_hlr[(Hydrofabric_RFC_physio_eco_clima_hlr['HLR']==i) & (Hydrofabric_RFC_physio_eco_clima_hlr['Available_data']>80) & (Hydrofabric_RFC_physio_eco_clima_hlr['NOAH_CFE']>0)]
    selected_sort=selected.sort_values(by='NCat')
    selected_sort['Priority']=-9
    selected_sort.at[selected_sort.index[0],'Priority']=1
    selected_sort.at[selected_sort.index[1],'Priority']=2
    Selected_calibration=pd.concat([Selected_calibration,selected_sort[0:2]])
    
Selected_calibration.to_csv(Hydrofabrics_folder+"Select_calibration_HLR.csv")
Selected_calibration.to_file(Hydrofabrics_folder +'Select_calibration_HLR.shp')
 