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
import subprocess

# for example
Hyd_folder="/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/"
CAMELS_list_516="/home/west/Projects/CAMELS/camels_basin_list_516.txt"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id': str})
CAMELS_516=CAMELS_516.set_index(['hru_id'])   


outputfolder='/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/'
count=0
outfolder_temp=outputfolder+"/forcing/"
if not os.path.exists(outfolder_temp): os.mkdir(outfolder_temp) 

for i in range (0,len(CAMELS_516)):   

    hru_id=CAMELS_516.index[i]
    print (hru_id + " " + str(i))    
    catchments=Hyd_folder+"/"+hru_id+'/catchment_data.geojson'

    outfolder=outputfolder+"/"+hru_id+"/forcing/"
    if not os.path.exists(outfolder): os.mkdir(outfolder)   
    subbasins = gp.GeoDataFrame.from_file(catchments)
    
    #Deleting existing files
    str_sub="rm " +outfolder + "*" 
    out=subprocess.call(str_sub,shell=True)     
    
    str_sub="aws s3 cp --recursive s3://formulations-dev/forcings/camels/20220202/"+hru_id+"/"  + " " +outfolder    
    out=subprocess.call(str_sub,shell=True)
    for index,row in subbasins.iterrows():
        catstr=row[0]
        outfolder_file=outfolder+catstr+ ".csv"
        if not os.path.exists(outfolder_file): 
            print ("File does not exist for : " + outfolder_file ) 
        # source=outfolder_temp+catstr.replace("cat-","") + ".csv"
        # destination=outfolder+"cat-"+catstr + ".csv"

        # if os.path.exists(source):
        #     os.rename(source,destination)
        # else:
        #     print ("File has not been downloaded")
        # count=count+1
 
print ("There are " + str(count) +" subbasins in CAMELS")
    


# Original_folder='/media/west/Expansion/CAMELS/PerBasin3/data_CAMELS/'
# Out_folder='/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/'
# if not os.path.exists(Out_folder): os.mkdir(Out_folder) 
# for i in range (0,1):       
#     hru_id=CAMELS_516.index[i]
#     print (hru_id + " " + str(i))    
#     source=Original_folder+hru_id + "/forcing/"
#     destination=Out_folder+hru_id 
#     if not os.path.exists(destination): os.mkdir(destination) 
#     destination=Out_folder+hru_id + "/forcing/"
#     if not os.path.exists(destination): os.mkdir(destination)     
#     str_sub="mv " + source+"* "+destination    
#     out=subprocess.call(str_sub,shell=True)      
