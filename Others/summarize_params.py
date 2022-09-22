# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 15:45:46 2021

@author: lcunha
"""
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 14:58:36 2021

@author: lcunha
"""
import os
from osgeo import ogr
from osgeo.gdalconst import GA_ReadOnly
import matplotlib.pyplot as plt     
import sys 
import pandas as pd
import geopandas as gpd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.getcwd())))
sys.path.append(BASE_DIR+"/CAMELS/params_code/")
import summarize_results_functions as FC

    
# Read file using gpd.read_file()
CAMELS_points=BASE_DIR+"/CAMELS/CAMELS_WHUC06.shp"
pt_data = gpd.read_file(CAMELS_points) 

# Read file with list of 516 CAMELS - remaining CAMELS are uncertain in terms of area
CAMELS_list_516="/home/west/Projects/CAMELS/camels_basin_list_516.txt"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id': str})
CAMELS_516=CAMELS_516.set_index(['hru_id'])   

CAMELS_names_file="/home/west/Projects/CAMELS/Attributes/camels_attributes_v2.0/camels_name.txt"
CAMELS_names=pd.read_csv(CAMELS_names_file, sep = ';',dtype={'gauge_id': str,'huc_02': str})
CAMELS_names=CAMELS_names.set_index(['gauge_id']) 

CAMELS_Attribute_file="/home/west/Projects/CAMELS/Attributes/camels_attributes_v2.0/camels_topo.txt"
CAMELS_Attributes=pd.read_csv(CAMELS_Attribute_file, sep = ';',dtype={'gauge_id': str})
CAMELS_Attributes=CAMELS_Attributes.set_index(['gauge_id'])   

Output_folder=BASE_DIR+"/CAMELS/PerBasin4/"
NoFilesAll=pd.DataFrame()
TWIListAll=[]  
CAMELS_516['Nelem']=0 
pt_data=pt_data.set_index(['hru_id'])
pt_data.index=pt_data.index.map(str)
Area_df=pd.DataFrame()
No_Hydrofabric=[]
for i in range (0,len(CAMELS_516)):
    hru_id=CAMELS_516.index[i]
    
    if(hru_id in CAMELS_Attributes.index):
        CAMELS_Attributes.loc[hru_id]
        area_gages2=CAMELS_Attributes.loc[hru_id]['area_gages2']
        area_geospa_fabric=CAMELS_Attributes.loc[hru_id]['area_geospa_fabric']
        huc_id_corr=np.copy(hru_id)
    else:
        print ("DID NOT FIND BASIN "+hru_id)
    
    hydro_fabrics_input_dir=Output_folder+"/"+hru_id+"/spatial/"   
     
    catchments_file = os.path.join(hydro_fabrics_input_dir, 'catchment_data.geojson')  
    if os.path.exists(catchments_file):
            
        catchments = gpd.read_file(catchments_file)     
        area_hydrofabric=sum(catchments['area_sqkm'])
    
        Area_df_temp=pd.DataFrame([(area_gages2,area_geospa_fabric,area_hydrofabric)],index=[str(huc_id_corr)],columns=(['area_gages2','area_geospa_fabric','area_hydrofabric']))    
        Area_df=pd.concat([Area_df,Area_df_temp])
        
        # vds = ogr.Open(catchments, GA_ReadOnly)  # TODO maybe open update if we want to write stats
        # assert(vds)
        # vlyr = vds.GetLayer(0)
        # total = vlyr.GetFeatureCount(force = 0)
        # vlyr.ResetReading()
        # feat = vlyr.GetNextFeature()
        # IDs=[]
        # while feat is not None:
        #     IDs.append(feat.GetField('ID'))
        #     rvds = None
        #     mem_ds = None
        #     feat = vlyr.GetNextFeature()   
        
        CAMELS_516.at[hru_id,'Nelem']=len(catchments)
        Resolution=30
        method=1
        input_twi=Output_folder+"/data_CAMELS/"+hru_id+"/Topmodel/"
        outputfolder_summary=Output_folder+"/data_CAMELS/plots/"
        if not os.path.exists(outputfolder_summary): os.mkdir(outputfolder_summary)   
        filename=hru_id    
        [NoFiles,TWIList]=FC.plot_twi_CAMELS(hru_id,catchments['id'].values,input_twi,outputfolder_summary,filename,50)    
        NoFilesAll=pd.concat([NoFilesAll,NoFiles])
        TWIListAll=TWIListAll+TWIList
        FC.plot_width_function_CAMELS(catchments['id'].values,input_twi,outputfolder_summary,filename,2000)
        
        input_giuh=Output_folder+"/data_CAMELS/"+hru_id+"/CFE/"
        outputfolder_summary=Output_folder+"/data_CAMELS/plots/"
        if not os.path.exists(outputfolder_summary): os.mkdir(outputfolder_summary)   
    
        FC.plot_giuh_CAMELS(catchments['id'].values,input_giuh,outputfolder_summary,filename,15)
    else:
        No_Hydrofabric.append(hru_id)
        
Area_df['ratio_original']=Area_df['area_gages2']/Area_df['area_geospa_fabric']
Area_df['ratio_geospa_fabric']=Area_df['area_geospa_fabric']/Area_df['area_hydrofabric']
Area_df['ratio_area_gages2']=Area_df['area_gages2']/Area_df['area_hydrofabric']


Gauges_With_Area_Issue=Area_df[(Area_df['ratio_area_gages2']<0.8) | (Area_df['ratio_area_gages2']>1.2)] 
Gauges_With_Area_Issue.index.name="gage_id"
Gauges_With_Area_Issue.to_csv(Output_folder+"Area_issue.csv")

NoFilesAll=NoFilesAll.set_index(['hru_id'])    
Per_hru_id=NoFilesAll.groupby(level=0).count()
Per_hru_id["HUC02"]=-9
Per_hru_id["Nelem"]=-9

for i in range(0,len(Per_hru_id)):
    Per_hru_id.at[Per_hru_id.index[i],'HUC02']=CAMELS_names.at[Per_hru_id.index[i],'huc_02']
    Per_hru_id.at[Per_hru_id.index[i],'Nelem']=CAMELS_516.at[Per_hru_id.index[i],'Nelem']

Per_hru_id["Porc"]=Per_hru_id['cat']/Per_hru_id['Nelem']
Per_hru_id.to_csv(Output_folder+"Missing_files_issue.csv")