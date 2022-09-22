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
import sys
import glob


# for example
CAMELS_list_516="/home/west/Projects/CAMELS/camels_basin_list_516.txt"
Output_folder="/home/west/Projects/CAMELS/PerBasin5/"
CAMELS_DEM="//media/west/Expansion/Backup/Projects/CAMELS/PerBasin4/"
PreviousVersion="/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/"
DEM_folder="/media/west/Expansion/DEM/"
if not os.path.exists(Output_folder): os.mkdir(Output_folder)

# # Read file using gpd.read_file()
# pt_data = gpd.read_file(CAMELS_points) 

 
# Read file with list of 516 CAMELS - remaining CAMELS are uncertain in terms of area
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id': str})
CAMELS_516=CAMELS_516.set_index(['hru_id'])   

CAMELS_names_file="/home/west/Projects/CAMELS/Attributes/camels_attributes_v2.0/camels_name.txt"
CAMELS_names=pd.read_csv(CAMELS_names_file, sep = ';',dtype={'gauge_id': str,'huc_02': str})
CAMELS_names=CAMELS_names.set_index(['gauge_id']) 

CAMELS_516=CAMELS_516.append(pd.DataFrame(index=['HUC01'])) 
CAMELS_names=CAMELS_names.append(pd.DataFrame([['01','HUC01']], columns=['huc_02','gauge_name'],index=['HUC01']))

# List all folder in AWS
str_sub="aws s3 ls s3://formulations-dev/CAMELS20/"
out=subprocess.check_output(str_sub,shell=True).splitlines()
Folder_CAMELS=[]
hru_id_CAMELS=[]
outlet_id_CAMELS=[]
for i in range(0,len(out)):
    str_CAMELS=out[i].decode('utf-8')
    if("camels" in str_CAMELS):
        str_CAMELS=str_CAMELS.replace("PRE","").replace(" ","").replace("/","")
        Folder_CAMELS.append(str_CAMELS)
        hru_id_CAMELS.append(str_CAMELS.split("_")[1])
        outlet_id_CAMELS.append(str_CAMELS.split("_")[2])

CAMELS_v2_df=pd.DataFrame({'Folder_CAMELS': Folder_CAMELS,
                           'hru_id_CAMELS': hru_id_CAMELS,
                           'outlet_id_CAMELS':outlet_id_CAMELS})
CAMELS_v2_df.to_csv(Output_folder+"CAMELS_v2_list.csv")  

# Download hydrofabrics 
Dif_Number_of_Catchments=[]
Dif_Catchments_ID=[]
Not_found_all=[]    
for i in range (0,len(hru_id_CAMELS)): 
    hru_id=hru_id_CAMELS[i]
    outfolder=Output_folder+"/"+Folder_CAMELS[i]+"/"
    if not os.path.exists(outfolder): os.mkdir(outfolder)   
    # Download hydrofabric     
    Flag_zero=0
    HUC2=CAMELS_names.loc[hru_id]['huc_02']        
    catchment_file=outfolder+"spatial/catchment_data.geojson"
    if(not os.path.exists(catchment_file)):
        str_sub="aws s3 cp --recursive s3://formulations-dev/CAMELS20/"+Folder_CAMELS[i]+" " +outfolder    
        out=subprocess.call(str_sub,shell=True)
    outfolder_forcing=Output_folder+"/"+Folder_CAMELS[i]+"/forcing/"
    if not os.path.exists(outfolder_forcing): os.mkdir(outfolder_forcing)     
    str_sub="aws s3 cp --recursive s3://formulations-dev/forcings/camels/20220202/"+hru_id+"/ " +outfolder_forcing    
    out=subprocess.call(str_sub,shell=True)        
                 

    
    
    