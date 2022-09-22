#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 11:31:10 2022

@author: west
"""

import os
import subprocess
import time
import yaml
import io
import pandas as pd
import json
import shutil 
import glob
from difflib import Differ

os.environ['PATH']="/home/west/git_repositories/ngen_08022022/ngen/venv2/bin:/home/west/anaconda3/bin:/home/west/anaconda3/condabin:/sbin:/bin:/usr/bin:/usr/local/bin:/snap/bin"
params_AR=['maxsmc', 'satdk', 'slope', 'b', 'Klf', 'Kn', 'Cgw', 'expon', 'satpsi','wltsmc','max_gw_storage','alpha_fc','refkdt', 'N_nash']
params_config_AR=['soil_params.smcmax=0.485421211', 'soil_params.satdk=5.94e-07', 'soil_params.slop=0.043736834',
        'soil_params.b=7.0', 'K_lf=0.01', 'K_nash=0.03', 'Cgw=1.8e-05', 'expon=7.0', 'soil_params.satpsi=0.759000003',
        'soil_params.wltsmc=0.083999999','max_gw_storage=0.011536753654','alpha_fc=0.33','refkdt=1.337907195', 'N_nash']

str_sub="source ~/git_repositories/ngen_08022022/ngen/venv2/bin/activate"
out=subprocess.call(str_sub,shell=True)  

params_values=['0.1', '0.004', '0.1',
        '2.0', '0.5', '0.5', '2.0e-02', '3.0', '0.1',
        '0.2','0.2','0.8','3.0', '7']
diff_1_2=[]
diff_3_4=[]
diff_1_4=[]
diff_2_4=[]
for pr in range(0,len(params_AR)-1):
    
    params=params_AR[pr]
    params_config=params_config_AR[pr]
    workdir="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/camels_05507600_4868933/"
    os.chdir(workdir)
    str_sub="rm -rf Run*"
    out=subprocess.call(str_sub,shell=True)   
    realiz_ori=workdir+"./Realization_noahowp_cfe_calib_test.json"
    #Run 1: Run current version, with original configuration file
    str_sub="rm -rf ngen"
    out=subprocess.call(str_sub,shell=True) 
    str_sub="ln -s ~/git_repositories/ngen_07252022/ngen"
    out=subprocess.call(str_sub,shell=True) 
    try:
        str_sub="./ngen/cmake_build/ngen spatial/catchment_data.geojson cat-12 spatial/nexus_data.geojson nex-7 " + realiz_ori
        out=subprocess.call(str_sub,shell=True) 
        word_dir_run1=workdir+"Run1_"+params
        if( not os.path.exists(word_dir_run1)): os.mkdir(word_dir_run1)
        str_sub="mv cat*.csv "+word_dir_run1
        out=subprocess.call(str_sub,shell=True)
        str_sub="mv nex*.csv "+word_dir_run1
        out=subprocess.call(str_sub,shell=True)
        str_sub="mv tnx*.csv "+word_dir_run1
        out=subprocess.call(str_sub,shell=True)    
    except:
        print ("did not run 2")  
    
    #define the ngen
    str_sub="rm -rf ngen"
    out=subprocess.call(str_sub,shell=True) 
    str_sub="ln -s /home/west/git_repositories/ngen_08022022/ngen"
    out=subprocess.call(str_sub,shell=True)  

    try:
        #Run 2: Run the version in this PR, with original configuration file
        str_sub="./ngen/cmake_build/ngen spatial/catchment_data.geojson cat-12 spatial/nexus_data.geojson nex-7 " + realiz_ori
        out=subprocess.call(str_sub,shell=True) 
        word_dir_run2=workdir+"Run2_"+params
        if( not os.path.exists(word_dir_run2)): os.mkdir(word_dir_run2)
        str_sub="mv cat*.csv "+word_dir_run2
        out=subprocess.call(str_sub,shell=True)
        str_sub="mv nex*.csv "+word_dir_run2
        out=subprocess.call(str_sub,shell=True)
        str_sub="mv tnx*.csv "+word_dir_run2
        out=subprocess.call(str_sub,shell=True)    
    except:
        print ("did not run 2") 
         
    #Run 3: Run the version in this PR, with modified configuration file (change the param in the config file)
    word_dir_run3=workdir+"Run3_"+params
    if( not os.path.exists(word_dir_run3)): os.mkdir(word_dir_run3)
    CFE_file="./CFE/cat-12_bmi_config_cfe_pass.txt"
    str_sub="cp "+CFE_file+" "+CFE_file.replace(".txt","Ori._txt")
    out=subprocess.call(str_sub,shell=True)
    new_line=params_config.split("=")[0]+"="+params_values[pr]
    str_sub="sed -i 's/"+params_config+"/"+new_line+"/g' "+workdir+CFE_file
    out=subprocess.call(str_sub,shell=True)
    str_sub="cp "+CFE_file+" "+word_dir_run3
    out=subprocess.call(str_sub,shell=True)
    
    try:
        str_sub="./ngen/cmake_build/ngen spatial/catchment_data.geojson cat-12 spatial/nexus_data.geojson nex-7 " + realiz_ori
        out=subprocess.call(str_sub,shell=True) 
        str_sub="mv cat*.csv "+word_dir_run3
        out=subprocess.call(str_sub,shell=True)
        str_sub="mv nex*.csv "+word_dir_run3
        out=subprocess.call(str_sub,shell=True)
        str_sub="mv tnx*.csv "+word_dir_run3
        out=subprocess.call(str_sub,shell=True)    
        str_sub="cp "+CFE_file.replace(".txt","Ori._txt")+" "+CFE_file
        out=subprocess.call(str_sub,shell=True)   
    except:
        print ("did not run 3")
        
    #Run 4: Run the version in this PR, with original configuration file and modified realization file (change the param with ngen)

    data_loaded_real_ori=json.load(open(realiz_ori))  
    data_loaded_real=data_loaded_real_ori.copy()                             
    data_loaded_real['global']['formulations'][0]['params']['modules'][1]['params']['model_params'][params]=params_values[pr]
    calib_realiz_mod=realiz_ori.replace(".json","mod.json")
    json_object=json.dumps(data_loaded_real,indent=4)
    with open(calib_realiz_mod,"w") as outfile:
        outfile.write(json_object)  
    try:
        str_sub="./ngen/cmake_build/ngen spatial/catchment_data.geojson cat-12 spatial/nexus_data.geojson nex-7 " + calib_realiz_mod
        out=subprocess.call(str_sub,shell=True) 
        word_dir_run4=workdir+"Run4_"+params
        if( not os.path.exists(word_dir_run4)): os.mkdir(word_dir_run4)
        str_sub="mv "+calib_realiz_mod + " " +word_dir_run4
        out=subprocess.call(str_sub,shell=True)
        str_sub="mv cat*.csv "+word_dir_run4
        out=subprocess.call(str_sub,shell=True)
        str_sub="mv nex*.csv "+word_dir_run4
        out=subprocess.call(str_sub,shell=True)
        str_sub="mv tnx*.csv "+word_dir_run4
        out=subprocess.call(str_sub,shell=True)    
    except:
        print ("did not run 4")
    file1=word_dir_run1+"/cat-12.csv"
    file2=word_dir_run2+"/cat-12.csv"
    file3=word_dir_run3+"/cat-12.csv"
    file4=word_dir_run4+"/cat-12.csv"
    str_sub="diff "+file1+ " " + file2 +" > diff_1_2.txt"
    out=subprocess.call(str_sub,shell=True) 
    if(os.path.getsize("diff_1_2.txt")>0):
        diff_1_2.append("diff_1_2 file size larger than zero,"+ str(params))
        print("diff_1_2 file size larger than zero "+ str(params))

    str_sub="diff "+file3+ " " + file4 +" > diff_3_4.txt"
    out=subprocess.call(str_sub,shell=True) 
    if(os.path.getsize("diff_3_4.txt")>0):
        diff_3_4.append("diff_3_4 file size larger than zero,"+ str(params))       
    str_sub="diff "+file1+ " " + file4 +" > diff_1_4.txt"
    out=subprocess.call(str_sub,shell=True) 
    if(os.path.getsize("diff_1_4.txt")==0):
        diff_1_4.append("diff_1_4 file size should not be zero,"+ str(params))
    str_sub="diff "+file2+ " " + file4 +" > diff_2_4.txt"
    out=subprocess.call(str_sub,shell=True) 
    if(os.path.getsize("diff_2_4.txt")==0):
        diff_2_4.append("diff_2_4 file size should not be zero,"+ str(params))        
#Results from Run 1 = Results from Run 2 - guarantee we did not change the results
#Results from Run 3 = Results from Run 4 - guarantee the model parameters were correctly changed by ngen, and the CFE results are the same if the parameter was changed in the config file or through the realization file.
