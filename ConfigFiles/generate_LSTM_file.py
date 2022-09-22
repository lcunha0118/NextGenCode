"""

author: lcunha

Function to generate namelist file for NOAH-modular surface bmi
https://github.com/NOAA-OWP/noah-mp-modular

Reads hydrofabrics
Alter specific parameters
 
"""

import pandas as pd
import os
import geopandas as gp
import glob

# for example
Hyd_folder="/home/west/Projects/CAMELS/PerBasin4/"
CAMELS_list_516="/home/west/Projects/CAMELS/camels_basin_list_516.txt"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id': str})
CAMELS_516=CAMELS_516.set_index(['hru_id'])   


outputfolder='/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/'


for i in range (516,len(CAMELS_516)):    
    hru_id=CAMELS_516.index[i]
    hru_id='HUC01'
    
    catchments=Hyd_folder+"/"+hru_id+'/spatial/catchment_data.geojson'
    LSTM_file=Hyd_folder+"/"+hru_id+'/parameters/camels.csv'
    base_namelist='/home/west/git_repositories/lstm/bmi_config_files/01022500_hourly_slope_mean_precip_temp.yml'

    outputfolder_CAMELS=outputfolder+"/"+hru_id+"/LSTM/"
    if not os.path.exists(outputfolder_CAMELS): os.mkdir(outputfolder_CAMELS)
#def generate_namelist_per_basin(catchments,nwm_wrf_hydro,outputfolder):

    
    zones = gp.GeoDataFrame.from_file(catchments)
    
    if(os.path.isfile(LSTM_file)): 
        param=pd.read_csv(LSTM_file,index_col=0)
    else:
        print ("LSTM parameters file not available")

    
    for index,row in zones.iterrows():
        with open(base_namelist) as f:
            namelist_ori=f.read()
        catstr=row[0]
        #if(isinstance(row[0], float)): catstr=str(int(row[0]))
        #if(not "cat" in catstr): catstr="cat-"+catstr        
        #start_time="2007-01-01 00:00:00"
        #end_time="2019-12-31 00:00:00" 

        namelist_ori=namelist_ori.replace("Narraguagus River at Cherryfield, Maine",catstr)
        namelist_ori=namelist_ori.replace("01022500",catstr)
        namelist_ori=namelist_ori.replace("620.38",str(row['area_sqkm']))
        namelist_ori=namelist_ori.replace("44.60797",str(row.geometry.centroid.y))
        namelist_ori=namelist_ori.replace("-67.93524",str(row.geometry.centroid.x))
        namelist_ori=namelist_ori.replace("17.79072",str(param.loc[catstr].slope))
        namelist_ori=namelist_ori.replace("92.68",str(param.loc[catstr].elevation))

        with open(outputfolder_CAMELS+catstr+".yml", "w") as f:
            f.write(namelist_ori)
    
    
    
       