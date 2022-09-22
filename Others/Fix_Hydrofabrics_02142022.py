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

def ckdnearest(zones, zones_previous):
    import numpy as np
    from scipy.spatial import cKDTree
    from shapely.geometry import Point, LineString
    zones_previous=zones_previous.rename(columns={'id':'id_previous'})
    zones=zones.rename(columns={'id':'id_new'})
    nA = np.array(list(zones.geometry.apply(lambda x: (x.centroid.x, x.centroid.y))))
    nB = np.array(list(zones_previous.geometry.apply(lambda x: (x.centroid.x, x.centroid.y))))
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=1)
    gdB_nearest = zones_previous.iloc[idx].drop(columns="geometry").reset_index(drop=True)
    gdf = pd.concat(
        [
            zones.reset_index(drop=True),
            gdB_nearest,
            pd.Series(dist, name='dist')
        ], 
        axis=1)

    return gdf


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

Dif_Number_of_Catchments=[]
Dif_Catchments_ID=[]
Not_found_all=[]    
for i in range (999,len(hru_id_CAMELS)): 
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
                 
    str_sub='rm -rf '+CAMELS_DEM+hru_id+"/crosswalks/"
    out=subprocess.call(str_sub,shell=True)
    str_sub='rm -rf '+CAMELS_DEM+hru_id+"/graph/"
    out=subprocess.call(str_sub,shell=True)
    str_sub='rm -rf '+CAMELS_DEM+hru_id+"/spatial/"
    out=subprocess.call(str_sub,shell=True)
    str_sub='rm -rf '+CAMELS_DEM+hru_id+"/parameters/"
    out=subprocess.call(str_sub,shell=True)      
    
    str_sub='cp -r ' + outfolder+"/spatial" +"*"+ " " + CAMELS_DEM+hru_id
    out=subprocess.call(str_sub,shell=True) 
    str_sub='cp -r ' + outfolder+"/parameters" +"*"+ " " + CAMELS_DEM+hru_id
    out=subprocess.call(str_sub,shell=True) 
    str_sub='cp -r ' + outfolder+"/reference*" +"*"+ " " + CAMELS_DEM+hru_id
    out=subprocess.call(str_sub,shell=True)     
    
    zones = gpd.GeoDataFrame.from_file(catchment_file)    
    catchment_file_previous=PreviousVersion+hru_id+"/hydrofabrics/spatial/catchment_data.geojson"

    if(os.path.exists(catchment_file_previous)):
        zones_previous = gpd.GeoDataFrame.from_file(catchment_file_previous)
    
        if(len(zones)==len(zones_previous)): 
            print ("Same number of catchments " +hru_id)
                       
            all_forcing=glob.glob(outfolder_forcing+"*.csv")
            all_forcing_list_id=[]
            for j in all_forcing:        
                all_forcing_list_id.append(j.replace(outfolder_forcing,"").replace(".csv",""))
            
            count=0
            Not_found=[]
            Flag=0
            for index,row in zones.iterrows():
                if(row.id in all_forcing_list_id):
                    count=count+1
                else:
                    Flag=1
                    Not_found.append(row.id)                
            
            if(Flag==1): 
                out_db=ckdnearest(zones,zones_previous)
                Dif_Catchments_ID.append(hru_id)
                Not_found_all.append([hru_id,len(all_forcing_list_id),count,len(Not_found)])         
                for j in range(0,len(out_db)):
                    if(out_db.iloc[j]['id_previous'] != out_db.iloc[j]['id_new']):
                        str_sub="cp " + outfolder_forcing +"/"+out_db.iloc[j]['id_previous']+".csv " + outfolder_forcing +"/"+out_db.iloc[j]['id_new']+".csv" 
                        out=subprocess.call(str_sub,shell=True)              
                
            #namelist_ori=namelist_ori.replace("40.01",str(row.geometry.centroid.y))
            #namelist_ori=namelist_ori.replace("-88.37",str(row.geometry.centroid.x))
        else:
            Dif_Number_of_Catchments.append(hru_id)
            out_db=ckdnearest(zones,zones_previous)
            Dif_Catchments_ID.append(hru_id)
            Not_found_all.append([hru_id,len(all_forcing_list_id),count,len(Not_found)])         
            for j in range(0,len(out_db)):
                if(out_db.iloc[j]['id_previous'] != out_db.iloc[j]['id_new']):
                    str_sub="cp " + outfolder_forcing +"/"+out_db.iloc[j]['id_previous']+".csv " + outfolder_forcing +"/"+out_db.iloc[j]['id_new']+".csv" 
                    out=subprocess.call(str_sub,shell=True)  

    
Not_found_all_df=pd.DataFrame(Not_found_all,columns=['hru_id','all_forcing','good','Not_found'])
Not_found_all_df.to_csv(Output_folder+"Not_found_all_afterfix.csv")   

Dif_Number_of_Catchments_df=pd.DataFrame(Dif_Number_of_Catchments,columns=['Dif_Number_of_Catchments'])
Dif_Number_of_Catchments_df.to_csv(Output_folder+"Dif_Number_of_Catchments_afterfix.csv") 

Dif_Catchments_ID_df=pd.DataFrame(Dif_Catchments_ID,columns=['Dif_Catchments_ID'])
Dif_Catchments_ID_df.to_csv(Output_folder+"Dif_Catchments_ID_afterfix.csv") 
    # outfolder_forcing=Output_folder+"/"+Folder_CAMELS[i]+"/forcing/"
    # if not os.path.exists(outfolder_forcing): os.mkdir(outfolder_forcing)         
    # str_sub="aws s3 cp --recursive s3://formulations-dev/forcings/camels/20220202/"+hru_id+"/ " +outfolder_forcing    
    # out=subprocess.call(str_sub,shell=True)        
    

    # all_forcing=glob.glob(outfolder_forcing+"*.csv")
    # all_forcing_list_id=[]
    # for j in all_forcing:        
    #     all_forcing_list_id.append(j.replace(outfolder_forcing,"").replace(".csv",""))
    
    # count=0
    # Not_found=[]
    # for index,row in zones.iterrows():
    #     if(row.id in all_forcing_list_id):
    #         print (row.id)    
    #         count=count+1
    #     else:
    #         Not_found.append(row.id)
    # Not_found_all.append([len(all_forcing_list_id),count,len(Not_found)])        

# COPY VALIDATION FILES
for i in range (0,len(CAMELS_v2_df)): 
    hru_id=hru_id_CAMELS[i]
    Val_folder=Output_folder+"/"+Folder_CAMELS[i]+"/Validation/"
    if not os.path.exists(Val_folder): os.mkdir(Val_folder)    
    Valid_Folder_previous=PreviousVersion+hru_id+"/Validation/*"
    str_sub="cp -rf " + Valid_Folder_previous +" "+Val_folder
    out=subprocess.call(str_sub,shell=True)  


# COPY HYDROFABRICS FILES        
Output_folder2="/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/"       
NoFiles=[]
for i in range (990,len(CAMELS_516)):    
    hru_id=CAMELS_516.index[i]
    outfolder=Output_folder+"/"+hru_id+"/"
    outfolder2=Output_folder2+"/"+hru_id+"/"

        # Data might not exist yet, so just run if data was successfully downloaded
    if os.path.exists(outfolder+"spatial"):
        print ("move")
        str_sub="cp "+outfolder+"spatial/catchment_data.geojson " +outfolder2
        out=subprocess.call(str_sub,shell=True)
        str_sub="cp "+outfolder+"spatial/nexus_data.geojson " +outfolder2
        out=subprocess.call(str_sub,shell=True)
    else:
        NoFiles.append(hru_id)

    
# CHECK PREVIOUS VERSION OF HYDROFABRICS FILES    
hyd_folder3="/media/west/Expansion/CAMELS/PerBasin3/"    
hyd_folder4="/home/west/Projects/CAMELS/PerBasin4/"       
NoFiles=[]
GoodBasins=[]
GoodBasinsInt=[]
for i in range (0,0):    
    hru_id=CAMELS_516.index[i]
    hyd_folder3_file=hyd_folder3+"/"+hru_id+"/aggregated_catchments.geojson"
    hyd_folder4_file=hyd_folder4+"/"+hru_id+'/spatial/catchment_data.geojson'
    if os.path.exists(hyd_folder3_file):
        zones3 = gpd.GeoDataFrame.from_file(hyd_folder3_file)
        if os.path.exists(hyd_folder4_file):    
            zones4 = gpd.GeoDataFrame.from_file(hyd_folder4_file)
            if(len(zones4)==len(zones3)): 
                GoodBasins.append(hru_id)
                GoodBasinsInt.append(int(hru_id))
            else:
                print("not same length "+hru_id+ " zone3 " + str(len(zones3)) + " zone4 " + str(len(zones4)))
        else:
            print("no file 4" + hyd_folder4_file)
            NoFiles.append([hru_id,4])
    else:
        print("no file 3" + hyd_folder4_file)
        NoFiles.append([hru_id,3])
        

# Copy hydrofabrics  
for i in range (0,0):    
    hru_id=CAMELS_516.index[i]
    folder_in="/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4/"+hru_id+"/crosswalks"
    folder_out="/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/"+"/"+hru_id+"/hydrofabrics/"
    str_sub="cp -rf " +folder_in + " " + folder_out 
    out=subprocess.call(str_sub,shell=True)  
    
    folder_in="/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4/"+hru_id+"/parameters"
    folder_out="/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/"+"/"+hru_id+"/hydrofabrics/"
    str_sub="cp -rf " +folder_in + " " + folder_out 
    out=subprocess.call(str_sub,shell=True)  
    
    folder_in="/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4/"+hru_id+"/graph"
    folder_out="/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/"+"/"+hru_id+"/hydrofabrics/"
    str_sub="cp -rf " +folder_in + " " + folder_out                 
    out=subprocess.call(str_sub,shell=True)  
    
    folder_in="/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4/"+hru_id+"/spatial"
    folder_out="/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/"+"/"+hru_id+"/hydrofabrics/"
    str_sub="cp -rf " +folder_in + " " + folder_out    
    out=subprocess.call(str_sub,shell=True)  
    

for i in range (0,0):    
    hru_id=CAMELS_516.index[i]
    folder_in="/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4/"+hru_id+"/crosswalks"
    folder_out="/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/"+hru_id+"/*.geojson"
    str_sub="rm " +folder_out  
    out=subprocess.call(str_sub,shell=True)      
    print (str_sub)

outfolder
for i in range (0,len(CAMELS_516)):    
    hru_id=CAMELS_516.index[i]    
    inputfolder="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/camels_01022500_2677104/spatial/"
    str_sub="rm "+outfolder+"flowpath_data.geojson "
    out=subprocess.call(str_sub,shell=True)
    
    str_sub="ogr2ogr -f \"GeoJSON\" "+outfolder+"flowpath_data.geojson " +outfolder+"hydrofabric.gpkg" + " flowpaths"
    #str_sub="ogr2ogr -f \"ESRI Shapefile\" "+outfolder+"gage_"+hru_id+".gpkg"
    out=subprocess.call(str_sub,shell=True)
    #str_sub="rm "+outfolder+"gage_0"+hru_id+".gpkg"
    #out=subprocess.call(str_sub,shell=True)
    
    hru_id=CAMELS_516.index[i]    
    outfolder="/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4/"+hru_id+"/spatial/"