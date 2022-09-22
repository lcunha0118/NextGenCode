#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  6 14:43:26 2021

@author: west
"""

import os
import geopandas as gpd
import subprocess
import pandas as pd

# for example
CAMELS_list_516="/home/west/Projects/CAMELS/camels_basin_list_516.txt"
CAMELS_pol="/home/west/Projects/CAMELS/HCDN_nhru_final_671WithGageIIHUC06.shp"
CAMELS_points="/home/west/Projects/CAMELS/CAMELS_WHUC06.shp"
DEM_folder="/home/west/Projects/CAMELS/DEM/"
Output_folder="/home/west/Projects/CAMELS/PerBasin2/"
if not os.path.exists(Output_folder): os.mkdir(Output_folder)

# Read file with list of 516 CAMELS - remaining CAMELS are uncertain in terms of area
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id': str})
CAMELS_516=CAMELS_516.set_index(['hru_id'])   

# Shapefiles for CAMELS
# pt_data = gpd.read_file(CAMELS_points) 
pol_data = gpd.read_file(CAMELS_pol) 
pol_data.index=pol_data['hru_id']

#  Contain area
# CAMELS_Attribute_file="/home/west/Projects/CAMELS/Attributes/camels_attributes_v2.0/camels_topo.txt"
# CAMELS_Attributes=pd.read_csv(CAMELS_Attribute_file, sep = ';',dtype={'gauge_id': str})
# CAMELS_Attributes=CAMELS_Attributes.set_index(['gauge_id']) 

#  File contains ID, name, and huc for the CAMELS 
CAMELS_names_file="/home/west/Projects/CAMELS/Attributes/camels_attributes_v2.0/camels_name.txt"
CAMELS_names=pd.read_csv(CAMELS_names_file, sep = ';',dtype={'gauge_id': str,'huc_02': str})
CAMELS_names=CAMELS_names.set_index(['gauge_id']) 

#  File contains CAMELS polygons  

pol_data_buf = pol_data.buffer(0.06)
pol_data_buf.to_file(Output_folder+"Buffered1.shp")
#data['HUC6'][0:2].unique()
len(pol_data)
NoHUC=[]
DatFile=Output_folder+"ALl_CAMELS.txt"
f= open(DatFile, "w")
                    
                    
for i in range (0,len(pol_data)):    
    f.write("%s" %(str(pol_data.iloc[i]['hru_id'])+"\n"))
f.close()    
    
for i in range (0,len(CAMELS_516)):
    hru_id=CAMELS_516.index[i]
    
    if(int(hru_id) in pol_data_buf.index):
        selection=pol_data_buf[pol_data_buf.index==int(hru_id)]
    else:
        print ("DID NOT FIND BASIN "+hru_id)
        
    outfolder=Output_folder+"/"+hru_id+"/"
    if not os.path.exists(outfolder): os.mkdir(outfolder)   
    Output_DEM=outfolder+hru_id+".tif"
    if not os.path.exists(Output_DEM):
        print (hru_id) 

        outfp=outfolder+hru_id+".shp"
        selection.to_file(outfp)         

        outfp=outfolder+hru_id+"_buffer.shp"
        selection.to_file(outfp)
        HUC2=CAMELS_names.loc[hru_id]['huc_02']
        # if(pt_data[pt_data['hru_id']==int(hru_id)]['HUC6'].iloc[0] is None):
        #     print (pt_data[pt_data['hru_id']==int(hru_id)]['HUC6'].iloc[0])
        #     if(int(hru_id)=='1121000'): HUC2="01"
        #     elif(int(hru_id)=='1123000'): HUC2="01"
        #     elif(int(hru_id)=='1195100'): HUC2="01"
        #     else:
        #         NoHUC.append(hru_id)
        # else:
        #     HUC2=pt_data[pt_data['hru_id']==int(hru_id)]['HUC6'].iloc[0][0:2]
        DEM_file=DEM_folder+"huc"+HUC2+"-res-1.tif"
        str_sub="gdalwarp -cutline  --config GDALWARP_IGNORE_BAD_CUTLINE YES "+outfp+" -dstalpha "+ DEM_file+" -crop_to_cutline  -dstnodata -999.0 "+Output_DEM
        
        subprocess.call(str_sub,shell=True)
