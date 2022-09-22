"""

author: lcunha

Function to generate namelist file for NOAH-modular surface bmi
https://github.com/NOAA-OWP/evapotranspiration


Reads hydrofabrics
Alter specific parameters
 
"""

import pandas as pd
import os
import geopandas as gpd
import glob
import subprocess
import osgeo.gdal as gdal
import osgeo.osr as osr
import numpy as np
from numpy import ma




Hydrofabrics_folder="/media/west/Expansion/hydrofabrics/"
#DEM_folder="/media/west/Expansion/DEM/"
list_huc=Hydrofabrics_folder+"VPU_hydrofabrics.txt"
VPU=pd.read_csv(list_huc)

print (VPU)
DEM_file="/media/west/Expansion/Projects/GIS/elev_100m_4269.tif"
ds = gdal.Open(DEM_file)
transform = ds.GetGeoTransform() # (-2493045.0, 30.0, 0.0, 3310005.0, 0.0, -30.0)
xOrigin = transform[0] # -2493045.0
yOrigin = transform[3] # 3310005.0
pixelWidth = transform[1] # 30.0
pixelHeight = transform[5] # -30.0
band = ds.GetRasterBand(1) # 1-based index
data = band.ReadAsArray()

base_config='/home/west/git_repositories/ngen_08022022/ngen/extern/evapotranspiration/evapotranspiration/configs/pet_config_bmi.txt'
MPTABLE_veg_file='/home/west/Projects/CAMELS/params_code/MPTABLE_VEG_LandType.csv'
MPTABLE_veg=pd.read_csv(MPTABLE_veg_file,index_col=0)

MPTABLE_albedo_file='/home/west/Projects/CAMELS/params_code/MPTABLE_albedo_SoilType.csv'    
MPTABLE_albedo=pd.read_csv(MPTABLE_albedo_file,index_col=0)

for i in range (len(VPU)-1,len(VPU)):   
    vpu_id=VPU.iloc[i]['vpu']
    print (vpu_id)
    
    catchments=Hydrofabrics_folder+"/"+vpu_id+'/catchment_data.geojson'
    wrf_hydro=Hydrofabrics_folder+"/"+vpu_id+'/cfe_noahowp_attributes.csv'
    basin_attribute_file=Hydrofabrics_folder+"/"+vpu_id+'/basin_attributes.csv'
    outputfolder_CAMELS=Hydrofabrics_folder+"/"+vpu_id+"/PET_2/"
    if(vpu_id=="CONUS"):
        print ("Running CONUS")
        catchments=Hydrofabrics_folder+"/CONUS/conus/catchment_data.geojson"
        wrf_hydro=Hydrofabrics_folder+"/CONUS/conus/cfe_noahowp_attributes.csv"
        outputfolder_CAMELS="/home/west/conus/PET_2/"
        #basin_attribute_file=Hydrofabrics_folder+"/CONUS/conus/basin_attributes.csv"
    
    
    if not os.path.exists(outputfolder_CAMELS): os.mkdir(outputfolder_CAMELS)
    
    
#def generate_namelist_per_basin(catchments,nwm_wrf_hydro,outputfolder):

    if os.path.exists(catchments): 
        print(catchments)
        zones = gpd.GeoDataFrame.from_file(catchments)
        print(len(zones))
        param=pd.read_csv(wrf_hydro,index_col=0)
        param = param[~param.index.duplicated(keep='first')]
        #basin_attribute=pd.read_csv(basin_attribute_file,index_col=0)
  
                              
        # Xin_param=pd.read_csv(Xinanjiang_param,index_col=0)
        # soil_params['AXAJ']=Xin_param.loc[soil_params['wf_ISLTYP'].values]['AXAJ'].values
        # soil_params['BXAJ']=Xin_param.loc[soil_params['wf_ISLTYP'].values]['BXAJ'].values
        # soil_params['XXAJ']=Xin_param.loc[soil_params['wf_ISLTYP'].values]['XXAJ'].values
        
        
        for index,row in zones.iterrows():
            with open(base_config) as f:
                config_ori=f.read()
            catstr=row[0]
            if("e" in catstr):
                print (catstr)
                nc=int(float(catstr.split("-")[1]))
                catstr="cat-"+nc
                
            if("--" in catstr):
                catstr=catstr.replace("--","")                
                print (" -- issue " + catstr)
            wf_ISLTYP=int(param.loc[row[0]]['ISLTYP'])
            wf_IVGTYP=int(param.loc[row[0]]['IVGTYP'])
            
            config_ori=config_ori.replace('pet_method=5','pet_method=1')
            
            config_ori=config_ori.replace('latitude_degrees=37.25','latitude_degrees='+str(row.geometry.centroid.y))
            config_ori=config_ori.replace('longitude_degrees=-97.5554','longitude_degrees='+str(row.geometry.centroid.x))
            #config_ori=config_ori.replace('site_elevation_m=303.33','site_elevation_m='+str(int(basin_attribute.loc[row[0]]['elevation']))) 
           
            x = row.geometry.centroid.x
            y = row.geometry.centroid.y
            xOffset = int((x - xOrigin) / pixelWidth)
            yOffset = int((y - yOrigin) / pixelHeight)

            # get individual pixel values
            value = data[yOffset][xOffset]
    
    
            config_ori=config_ori.replace('site_elevation_m=303.33','site_elevation_m='+str(value))            
            config_ori=config_ori.replace('vegetation_height_m=0.12','vegetation_height_m='+str(MPTABLE_veg.loc[wf_IVGTYP]['HVT']))
            config_ori=config_ori.replace('zero_plane_displacement_height_m=0.0003','zero_plane_displacement_height_m='+str(2.*MPTABLE_veg.loc[wf_IVGTYP]['HVT']/3.))
            config_ori=config_ori.replace('momentum_transfer_roughness_length=0.0','momentum_transfer_roughness_length='+str(MPTABLE_veg.loc[wf_IVGTYP]['Z0MVT']))
            config_ori=config_ori.replace('heat_transfer_roughness_length_m=0.0','heat_transfer_roughness_length_m='+str(0.1*MPTABLE_veg.loc[wf_IVGTYP]['Z0MVT']))
            config_ori=config_ori.replace('surface_shortwave_albedo=0.22','surface_shortwave_albedo='+str(MPTABLE_veg.loc[wf_ISLTYP]['albedo_mean']))    
            config_ori=config_ori.replace('shortwave_radiation_provided=0','shortwave_radiation_provided=1')        
            
            with open(outputfolder_CAMELS+catstr+"_pet_config.txt", "w") as f:
                f.write(config_ori)
            
    
    
       