"""

author: lcunha


Download hydrofabrics forcing
 
"""

import pandas as pd
import os
import geopandas as gp
import glob
import subprocess


# Read file with list of 516 CAMELS - remaining CAMELS are uncertain in terms of area
CAMELS_list_516="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/CAMELS_v3_complete.csv"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id_CAMELS': str})
CAMELS_516=CAMELS_516.set_index(['hru_id_CAMELS']) 
#CAMELS_516=CAMELS_516[CAMELS_516['SA_analysis']==1]

outputfolder='/home/west/Projects/CAMELS/CAMELS_Files_Ngen/'


for i in range (0,len(CAMELS_516)):   
    hru_id=CAMELS_516.index[i]   
    Folder=CAMELS_516.iloc[i]['Folder_CAMELS']  
    #huc_02=CAMELS_516.iloc[i]['huc_02']
    
    print (hru_id + " " + str(i))    
    catchments=outputfolder+"/"+Folder+'/spatial/catchment_data.geojson'

    outfolder=outputfolder+"/"+Folder+"/forcing/"
    if not os.path.exists(outfolder): os.mkdir(outfolder)   
    subbasins = gp.GeoDataFrame.from_file(catchments)

    
    #Deleting existing files
    str_sub="rm " +outfolder + "*" 
    out=subprocess.call(str_sub,shell=True)     
    # Downdload from aws
    str_sub="aws s3 cp --recursive s3://formulations-dev/forcings/camels/20220315/"+hru_id+"/"  + " " +outfolder   
    out=subprocess.call(str_sub,shell=True)

    for index,row in subbasins.iterrows():
        catstr=row[0]
        outfolder_file=outfolder+catstr+ ".csv"
        if not os.path.exists(outfolder_file): 
            print ("File does not exist for : " + outfolder_file ) 


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
