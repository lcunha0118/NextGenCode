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

# for example

Hyd_folder="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"
CAMELS_list_516="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/CAMELS_v3_complete.csv"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id_CAMELS': str})
CAMELS_516=CAMELS_516.set_index(['hru_id_CAMELS'])
#CAMELS_516=CAMELS_516.set_index(['Folder_CAMELS'])   
CAMELS_516=CAMELS_516.append(pd.DataFrame(index=['HUC01']))
CAMELS_516.at['HUC01','Folder_CAMELS']='HUC01'
outputfolder='/home/west/Projects/CAMELS/CAMELS_Files_Ngen/'

for i in range (405,len(CAMELS_516)):    
    hru_id=CAMELS_516.index[i]
    Folder=CAMELS_516.loc[hru_id]['Folder_CAMELS']
    
    catchments=Hyd_folder+"/"+Folder+'/spatial/catchment_data.geojson'
    wrf_hydro=Hyd_folder+"/"+Folder+'/parameters/cfe.csv'
    basin_attribute_file=Hyd_folder+"/"+Folder+'/parameters/basin_attributes.csv'
    base_config='/home/west/git_repositories/ngen_03032022/ngen/extern/evapotranspiration/evapotranspiration/configs/pet_config_bmi.txt'
    MPTABLE_veg_file='/home/west/Projects/CAMELS/params_code/MPTABLE_VEG_LandType.csv'
    MPTABLE_veg=pd.read_csv(MPTABLE_veg_file,index_col=0)
    
    MPTABLE_albedo_file='/home/west/Projects/CAMELS/params_code/MPTABLE_albedo_SoilType.csv'    
    MPTABLE_albedo=pd.read_csv(MPTABLE_albedo_file,index_col=0)
    
    outputfolder_CAMELS=outputfolder+"/"+Folder+"/PET/"
    if not os.path.exists(outputfolder_CAMELS): os.mkdir(outputfolder_CAMELS)

    
#def generate_namelist_per_basin(catchments,nwm_wrf_hydro,outputfolder):

    if os.path.exists(catchments): 
        zones = gpd.GeoDataFrame.from_file(catchments)
       
        param=pd.read_csv(wrf_hydro,index_col=0)
        basin_attribute=pd.read_csv(basin_attribute_file,index_col=0)
  
                              
        # Xin_param=pd.read_csv(Xinanjiang_param,index_col=0)
        # soil_params['AXAJ']=Xin_param.loc[soil_params['wf_ISLTYP'].values]['AXAJ'].values
        # soil_params['BXAJ']=Xin_param.loc[soil_params['wf_ISLTYP'].values]['BXAJ'].values
        # soil_params['XXAJ']=Xin_param.loc[soil_params['wf_ISLTYP'].values]['XXAJ'].values
        
        
        for index,row in zones.iterrows():
            with open(base_config) as f:
                config_ori=f.read()
            catstr=row[0]
            print (catstr)
            wf_ISLTYP=int(param.loc[row[0]]['wf_ISLTYP'])
            wf_IVGTYP=int(param.loc[row[0]]['wf_IVGTYP'])
            
            config_ori=config_ori.replace('pet_method=5','pet_method=1')
            config_ori=config_ori.replace('latitude_degrees=37.25','latitude_degrees='+str(row.geometry.centroid.y))
            config_ori=config_ori.replace('longitude_degrees=-97.5554','longitude_degrees='+str(row.geometry.centroid.x))
            config_ori=config_ori.replace('site_elevation_m=303.33','site_elevation_m='+str(int(basin_attribute.loc[row[0]]['elevation'])))            
            config_ori=config_ori.replace('vegetation_height_m=0.12','vegetation_height_m='+str(MPTABLE_veg.loc[wf_IVGTYP]['HVT']))
            config_ori=config_ori.replace('zero_plane_displacement_height_m=0.0003','zero_plane_displacement_height_m='+str(2.*MPTABLE_veg.loc[wf_IVGTYP]['HVT']/3.))
            config_ori=config_ori.replace('momentum_transfer_roughness_length=0.0','momentum_transfer_roughness_length='+str(MPTABLE_veg.loc[wf_IVGTYP]['Z0MVT']))
            config_ori=config_ori.replace('heat_transfer_roughness_length_m=0.0','heat_transfer_roughness_length_m='+str(0.1*MPTABLE_veg.loc[wf_IVGTYP]['Z0MVT']))
            config_ori=config_ori.replace('surface_shortwave_albedo=0.22','surface_shortwave_albedo='+str(MPTABLE_veg.loc[wf_ISLTYP]['albedo_mean']))    
            config_ori=config_ori.replace('shortwave_radiation_provided=0','shortwave_radiation_provided=1')        
            
            with open(outputfolder_CAMELS+catstr+"_pet_config.txt", "w") as f:
                f.write(config_ori)
    
    
    
       