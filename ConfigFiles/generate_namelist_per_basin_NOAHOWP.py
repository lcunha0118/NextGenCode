"""

author: lcunha

Function to generate namelist file for NOAH-modular surface bmi
https://github.com/NOAA-OWP/noah-owp-modular

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
CAMELS_list_516="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/CAMELS_v2_list.csv"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id_CAMELS': str})
CAMELS_516=CAMELS_516.set_index(['Folder_CAMELS'])   
#CAMELS_516=CAMELS_516.append(pd.DataFrame(index=['HUC01']))

outputfolder='/home/west/Projects/CAMELS/CAMELS_Files_Ngen/'
startdate="200710010000" 
enddate="201912310000" 

for i in range (0,len(CAMELS_516)):    
    hru_id=CAMELS_516.index[i]
    
    catchments=Hyd_folder+"/"+hru_id+'/spatial/catchment_data.geojson'
    wrf_hydro=Hyd_folder+"/"+hru_id+'/parameters/cfe.csv'
    base_namelist='/home/west/git_repositories/ngen_07252022/ngen/extern/noah-owp-modular/noah-owp-modular/run/namelist.input'
    
    
    outputfolder_CAMELS=outputfolder+"/"+hru_id+"/NOAH/"
    if not os.path.exists(outputfolder_CAMELS): os.mkdir(outputfolder_CAMELS)
    outputfolder_CAMELS_paramTable=outputfolder+"/"+hru_id+"/NOAH/parameters/"
    if not os.path.exists(outputfolder_CAMELS_paramTable): os.mkdir(outputfolder_CAMELS_paramTable)
    str_sub="rm "+ outputfolder_CAMELS_paramTable+"/*"
    out=subprocess.call(str_sub,shell=True) 
    str_sub="cp -r /home/west/git_repositories/ngen_07252022/ngen/extern/noah-owp-modular/noah-owp-modular/parameters/* "+outputfolder_CAMELS_paramTable
    out=subprocess.call(str_sub,shell=True) 
#def generate_namelist_per_basin(catchments,nwm_wrf_hydro,outputfolder):

    if os.path.exists(catchments): 
        zones = gpd.GeoDataFrame.from_file(catchments)
       
        if(os.path.isfile(wrf_hydro)): 
            param=pd.read_csv(wrf_hydro,index_col=0)
        else:
            IDAr=[]
            for index,row in zones.iterrows():
    
                IDAr.append(row.ID)       
            param=pd.DataFrame(index=IDAr)
        
            param['wf_ISLTYP']= 1.0   # correspond to isltyp - from wrfinput_CONUS.nc
            param['wf_IVGTYP']= 1.0    # correspond to vegtyp - from wrfinput_CONUS.nc                         
        
        param['soilcolor']= 4.0 # set to 4 - not available in wrfinput_CONUS.nc
        
        
        for index,row in zones.iterrows():
            with open(base_namelist) as f:
                namelist_ori=f.read()
            catstr=row[0]
            #if(isinstance(row[0], float)): catstr=str(int(row[0]))
            #if(not "cat" in catstr): catstr="cat-"+catstr        
            #start_time="2007-01-01 00:00:00"
            #end_time="2019-12-31 00:00:00" 
            namelist_ori=namelist_ori.replace("1800.0",'3600.0')
            namelist_ori=namelist_ori.replace("1800.0",'3600.0')
            namelist_ori=namelist_ori.replace("../parameters",'./NOAH/parameters/')
            namelist_ori=namelist_ori.replace("199801010630",startdate)
            namelist_ori=namelist_ori.replace("199901010630",enddate)
            namelist_ori=namelist_ori.replace("../data/bondville.dat","./forcing/"+catstr+".csv")
            namelist_ori=namelist_ori.replace("../data/output.nc","out_"+catstr+".csv")
            namelist_ori=namelist_ori.replace("40.01",str(row.geometry.centroid.y))
            namelist_ori=namelist_ori.replace("-88.37",str(row.geometry.centroid.x))
            namelist_ori=namelist_ori.replace("subsurface_option                 = 1","subsurface_option                 = 2")
            namelist_ori=namelist_ori.replace("runoff_option                     = 8","runoff_option                     = 3")
            namelist_ori=namelist_ori.replace("dynamic_veg_option                = 1","dynamic_veg_option                = 4")
            namelist_ori=namelist_ori.replace("MODIFIED_IGBP_MODIS_NOAH","USGS")
            namelist_ori=namelist_ori.replace("-88.37",str(row.geometry.centroid.x))
            namelist_ori=namelist_ori.replace("evap_srfc_resistance_option       = 1","evap_srfc_resistance_option       = 4")
            namelist_ori=namelist_ori.replace("nveg             = 20","nveg             = 27")
            
            namelist_ori=namelist_ori.replace("isltyp           = 1","isltyp           = "+str(int(param.loc[row[0]]['wf_ISLTYP'])))
            namelist_ori=namelist_ori.replace("vegtyp           = 1","vegtyp           = "+str(int(param.loc[row[0]]['wf_IVGTYP'])))
            namelist_ori=namelist_ori.replace("soilcolor           = 4","soilcolor           = "+str(int(param.loc[row[0]]['soilcolor'])))
            
            with open(outputfolder_CAMELS+catstr+".input", "w") as f:
                f.write(namelist_ori)
    
    
    
       