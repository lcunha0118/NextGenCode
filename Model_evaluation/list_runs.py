#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 09:20:43 2021

@author: west
"""
import pandas as pd
import geopandas as gp
from datetime import datetime,timedelta
import os
import matplotlib.pyplot as plt
import glob
import geopandas as gpd
import seaborn as sns
import numpy as np
import subprocess

    
# for example
Hyd_folder="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"
Output_folder="/media/west/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Results/"

Output_ngen=["Output_ngen_03292022"]

CAMELS_list_516="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/CAMELS_v3_complete.csv"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id_CAMELS': str})
CAMELS_516=CAMELS_516.set_index(['hru_id_CAMELS'])
#CAMELS_516=CAMELS_516[CAMELS_516['SA_analysis']==1]

CAMELS_516['Lat']=-9.0
CAMELS_516['Long']=-9.0
for i in range (0,len(CAMELS_516)):  
    hru_id=CAMELS_516.index[i]
    Folder=CAMELS_516.iloc[i]['Folder_CAMELS']
    Hydrofabrics=Hyd_folder+"/"+Folder+"/spatial/catchment_data.geojson"
    basin = gpd.read_file(Hydrofabrics) 
    basin_id=basin.sort_values(by="area_sqkm",ascending=True).iloc[0].id
    nexus_id=basin.sort_values(by="area_sqkm",ascending=True).iloc[0].toid
    CAMELS_516.at[hru_id,'Lat']=basin.sort_values(by="area_sqkm",ascending=True).iloc[0].geometry.centroid.y
    CAMELS_516.at[hru_id,'Long']=basin.sort_values(by="area_sqkm",ascending=True).iloc[0].geometry.centroid.x      

General_Dir="/data_CAMELS/"
ID_format="id"
Models=["NOAH_CFE","NOAH_CFE_KNash","NOAH_CFE_klNash","NOAH_CFE_GWIC8","PET_1_CFE","PET_2_CFE","PET_3_CFE","PET_4_CFE","PET_5_CFE","NOAH_CFE_X","PET_1_CFE_X","PET_2_CFE_X","PET_3_CFE_X","PET_4_CFE_X","PET_5_CFE_X","NOAH_Topmodel","PET_1_Topmodel","PET_2_Topmodel","PET_3_Topmodel","PET_4_Topmodel","PET_5_Topmodel"]
#Models=["NOAH_CFE"]
Models=["NOAH_CFE","NOAH_CFE_X","NOAH_Topmodel","PET_1_CFE","PET_1_CFE_X","PET_1_Topmodel","PET_4_CFE","PET_4_CFE_X","PET_4_Topmodel"]
Models=["NOAH_CFE","NOAH_CFE_X","NOAH_Topmodel"]

#Models=["PET_1_CFE","PET_2_CFE","PET_3_CFE","PET_4_CFE","PET_5_CFE"]

#Models=["NOAH_Topmodel"]
Config_file=[Hyd_folder+"CFE_output_var_config.csv",Hyd_folder+"Topmodel_output_var_config.csv"]
Models_run=pd.DataFrame()

# Models=["NOAH_CFE"]
# Config_file=[Hyd_folder+"CFE_output_var_config.csv"]
Spinnup=365 # in Days
#min_date_plot=min_date
min_date_plot=datetime(2007,10,1,0,0)
#min_date_plot=datetime(2012,10,1,0,0)
max_date_plot=datetime(2013,10,1,0,0)

#CAMELS_516=pd.read_csv("/home/west/Projects/CAMELS/HUC01_camels_calib.txt",header=None,dtype=str)
sns.set_style("whitegrid")
Problem_simulations=[]

CAMELS_516['area_sqkm']=0
CAMELS_516['NOAH_CFE']=0
CAMELS_516['NOAH_CFE_X']=0
CAMELS_516['NOAH_Topmodel']=0

#CAMELS_516=CAMELS_516[CAMELS_516.NCat<=1]
#CAMELS_516=CAMELS_516[CAMELS_516.index=="01466500"]
for i in range (0,len(CAMELS_516)):   
    hru_id=CAMELS_516.index[i]
    Folder=CAMELS_516.iloc[i]['Folder_CAMELS']
    print (hru_id)
  
    Daily_Q_all_Model=pd.DataFrame()  
    
    for j in range (0,len(Models)):  
        print(Models[j])
        for z in range(0,len(Output_ngen)):
            
            if ("PET" in Models[j]) and (CAMELS_516.iloc[i]['RunPET']==0):
                print("Snow dominated areas, do not plot PET")
            else:

                 
                # Read output config file
                if("CFE" in Models[j]):  file=Config_file[0]
                else:  file=Config_file[1]
                Output_config=pd.read_csv(file,index_col=0)
                outfolder=Hyd_folder+"/"+Folder+"/"
                catchment_file=Hyd_folder+"/"+Folder+'/spatial/catchment_data.geojson'    
                
                Results=Output_folder+"/"+Folder+"/"+Output_ngen[z]+"/"+Models[j]+"/"
                all_results=glob.glob(Results+"cat*.csv")
                flag_empty=0
                for f in all_results:
                    if(os.path.getsize(f)==0):
                        flag_empty=1
                flag_wrong=0
                if(flag_empty==0) & (len(all_results)>0):        
                    Cat_out_file=f
                    Cat_out=pd.read_csv(Cat_out_file,parse_dates=True,index_col=1)                    
                    nvar=0
                    if(len(all_results)>1):
                        for ff in range(0,len(Output_config)):
                            if(not Output_config.output_var_names[ff] in Cat_out.columns):
                                print ("did not find variable " + Output_config.output_var_names[ff])
                                
                                nvar=nvar+1
                        if(nvar>3):  
                            flag_wrong=1   
                if(flag_empty==1) | (flag_wrong==1):
                    for f in os.listdir(Results):
                       os.remove(os.path.join(Results,f))                        
                zones = gp.GeoDataFrame.from_file(catchment_file)
                CAMELS_516.at[hru_id,'area_sqkm']=sum(zones['area_sqkm'])
                
                if(len(all_results)<len(zones)) | (flag_empty==1) | (flag_wrong==1):
                    Temp=pd.DataFrame([[hru_id,Models[j],CAMELS_516.iloc[i]['frac_snow'],0]],columns=['hru_id','Models','frac_snow','Done'])
                    Models_run=Models_run.append(Temp)
                    if(os.path.exists(Results)) & (len(all_results)>0): 
                        Problem_simulations.append([hru_id,Models[j],"Not Enough files"])
                        print (hru_id + "  Not Enough files")
                        for f in os.listdir(Results):
                            os.remove(os.path.join(Results,f))
                    os.chdir(Hyd_folder+"/"+Folder)
                    if(Models[j]=="NOAH_CFE"): Realiz_out="Realization_noahowp_cfe_calib.json"
                    elif(Models[j]=="NOAH_CFE_X"): Realiz_out="Realization_noahowp_cfe_X_calib.json"
                    elif(Models[j]=="NOAH_Topmodel"): Realiz_out="Realization_noahowp_topmodel_calib.json"
                    else: 
                        if("Topmodel" in Models[j]): Realiz_out="Realization_pet_topmodel_calib.json"
                        elif("CFE" in Models[j]): Realiz_out="Realization_pet_cfe_calib.json"
                        else: Realiz_out="Realization_pet_CFE_X_calib.json"
                        
                        
                            
                    print("Will run nextgen")
                    Run_nextgen="./ngen/cmake_build/ngen "+ "./spatial/catchment_data.geojson '' ./spatial/nexus_data.geojson '' "+Realiz_out    
                    os.chdir(Hyd_folder+"/"+Folder)
                    if("PET" in Models[j]):
                        ID=Models[j].split("_")[1]
                        for idd in range(1,6):
                            Run_sed="sed -i 's/pet_method="+str(idd)+"/pet_method='"+str(ID)+"'/g' ./PET/*"
                            out=subprocess.call(Run_sed,shell=True)
                    out=subprocess.call(Run_nextgen,shell=True) 
                    os.mkdir(Results)
                    mv_files="mv "+Hyd_folder+"/"+Folder+"/cat*csv " + Results
                    print("Move to " + Results)
                    #out=subprocess.call(mv_files,shell=True) 
                            
                else:
                    Temp=pd.DataFrame([[hru_id,Models[j],CAMELS_516.iloc[i]['frac_snow'],1]],columns=['hru_id','Models','frac_snow','Done'])
                    Models_run=Models_run.append(Temp)      
                    CAMELS_516.at[hru_id,Models[j]]=1
Models_run.to_csv(Hyd_folder+"List_runs9.csv")   
CAMELS_516.to_csv(Hyd_folder+"CAMELS_runs9.csv")  
