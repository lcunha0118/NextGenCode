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



CAMELS_list_516="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/CAMELS_v3_complete.csv"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id_CAMELS': str})
CAMELS_516=CAMELS_516.set_index(['hru_id_CAMELS'])
#CAMELS_516=CAMELS_516[CAMELS_516['SA_analysis']==1]
Hyd_folder="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"  

Results=  Hyd_folder+"Results/" 
if not os.path.exists(Results): os.mkdir(Results)

CAMELS_516[CAMELS_516.index=="01466500"]
for i in range (0,len(CAMELS_516)):   
    hru_id=CAMELS_516.index[i]
    Folder=CAMELS_516.iloc[i]['Folder_CAMELS']
    LocalFolder=Hyd_folder+"/"+Folder+"/"
    Rem_folder=LocalFolder+"Output_ngen_03032022"
    str_sub="rm -rf "+Rem_folder
    if os.path.exists(Rem_folder): out=subprocess.call(str_sub,shell=True)   
    Rem_folder=LocalFolder+"Output_ngen_paral"
    str_sub="rm -rf "+Rem_folder
    if os.path.exists(Rem_folder): out=subprocess.call(str_sub,shell=True)  
    Rem_folder=LocalFolder+"Output_ngen2"
    str_sub="rm -rf "+Rem_folder
    if os.path.exists(Rem_folder): out=subprocess.call(str_sub,shell=True)  
    Rem_folder=LocalFolder+"CFE_GW"
    str_sub="rm -rf "+Rem_folder
    if os.path.exists(Rem_folder): out=subprocess.call(str_sub,shell=True)   
    Rem_folder=LocalFolder+"CFE_GWIC8"
    str_sub="rm -rf "+Rem_folder
    if os.path.exists(Rem_folder): out=subprocess.call(str_sub,shell=True)   
    Rem_folder=LocalFolder+"CFE_klNash"
    str_sub="rm -rf "+Rem_folder
    if os.path.exists(Rem_folder): out=subprocess.call(str_sub,shell=True)   
    Rem_folder=LocalFolder+"CFE_kNash"
    str_sub="rm -rf "+Rem_folder
    if os.path.exists(Rem_folder): out=subprocess.call(str_sub,shell=True)   
    Rem_folder=LocalFolder+"CFE_test"
    str_sub="rm -rf "+Rem_folder
    if os.path.exists(Rem_folder): out=subprocess.call(str_sub,shell=True)   
    Rem_folder=LocalFolder+"CFE_test"
    str_sub="rm -rf "+Rem_folder
    if os.path.exists(Rem_folder): out=subprocess.call(str_sub,shell=True)   
    Rem_folder=LocalFolder+"*_16.json"
    str_sub="rm "+Rem_folder
    out=subprocess.call(str_sub,shell=True) 

    Rem_folder=LocalFolder+"Realization*.json"
    str_sub="rm "+Rem_folder
    out=subprocess.call(str_sub,shell=True) 
    Rem_folder=LocalFolder+"ngen_02272022"
    if os.path.exists(Rem_folder): str_sub="rm "+Rem_folder
    out=subprocess.call(str_sub,shell=True) 
    
    Results_sub_folder=Results + Folder 
    if not os.path.exists(Results_sub_folder): os.mkdir(Results_sub_folder)
    str_sub="mv "+LocalFolder+"Output_* "+Results_sub_folder
    out=subprocess.call(str_sub,shell=True)     
    str_sub="mv "+LocalFolder+"Sens_Analysis_NextGen "+Results_sub_folder
    out=subprocess.call(str_sub,shell=True)   

    
    # str_sub='aws s3 rm s3://formulations-dev/ --recursive --exclude "*" --include  CAMELS20/'+Folder +"/Output_ngen_03092022/*"
    # out=subprocess.call(str_sub,shell=True)   
    # str_sub='aws s3 rm s3://formulations-dev/ --recursive --exclude "*" --include  CAMELS20/'+Folder +"/Output_ngen_paral/*"
    # out=subprocess.call(str_sub,shell=True)  
    # str_sub='aws s3 rm s3://formulations-dev/ --recursive --exclude "*" --include  CAMELS20/'+Folder +"/Sens_Analysis_NextGen/*"
    # out=subprocess.call(str_sub,shell=True) 
    # str_sub='aws s3 rm s3://formulations-dev/ --recursive --exclude "*" --include  CAMELS20/'+Folder +"/CFE_test/*"
    # out=subprocess.call(str_sub,shell=True) 
    # str_sub='aws s3 rm s3://formulations-dev/ --recursive --exclude "*" --include  CAMELS20/'+Folder +"/CFE_Nash/*"
    # out=subprocess.call(str_sub,shell=True) 
    # str_sub='aws s3 rm s3://formulations-dev/ --recursive --exclude "*" --include  CAMELS20/'+Folder +"/CFE_GW/*"
    # out=subprocess.call(str_sub,shell=True) 
        
    str_sub="aws s3 sync "+LocalFolder +" s3://formulations-dev/CAMELS20/"+Folder + " --exclude Results/*"+ " --exclude ngen_02272022/*"+ " --exclude ngen/* --exclude parameters/* --exclude spatial/*"
    out=subprocess.call(str_sub,shell=True)   

        
         
