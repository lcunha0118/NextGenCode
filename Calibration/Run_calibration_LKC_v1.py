#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 14:01:06 2022

@author: west
"""
#from pathlib import Path
#import matplotlib.pylab as plt
#import json
#from ngen_cal import plot_objective, plot_stuff, plot_obs, plot_output, plot_parameter_space

import os
import subprocess
import time
import yaml
import io
import pandas as pd
import json
import shutil 
import glob

calib_output_folder="calibSep_5"
Hydrofabrics_folder="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"
Select_calibration_file="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/Select_calibration_HLR_RFC.csv"
Selected_calibration=pd.read_csv(Select_calibration_file,dtype={'hru_id_CAMELS': str})
Selected_calibration=Selected_calibration.set_index(['hru_id_CAMELS'])


os.environ['PATH']="/home/west/git_repositories/ngen_08022022/ngen/venv2/bin:/home/west/anaconda3/bin:/home/west/anaconda3/condabin:/sbin:/bin:/usr/bin:/usr/local/bin:/snap/bin"
calib_config_dir="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/calib_conf/"
calib_config_base=calib_config_dir+"calib_config_CAMELS_CFE_Calib_Sep_2.yaml"
calib_realiz_base=calib_config_dir+"Realization_noahowp_cfe_calib_NCForcing.json"

# LKC - to implement
param_to_remove=[] 
iterations=300 
start_time="2008-10-01 00:00:00"
end_time="2013-10-01 00:00:00"
        
for i in range(30,40):
    Folder_CAMELS=Selected_calibration.iloc[i]['Folder_CAMELS']
    word_dir=Hydrofabrics_folder+Folder_CAMELS+"/"
    os.chdir(word_dir)
    calib_folder=word_dir+calib_output_folder  
    objective_log = calib_folder+'/ngen-calibration_objective.txt'    
    str_sub="rm -rf "+calib_folder
    out=subprocess.call(str_sub,shell=True)
    
    if(Selected_calibration.iloc[i]['N_nexus']>=2) & (not os.path.exists(objective_log)):
        
        try:
            
            
            print(Folder_CAMELS)
            hru_id=Selected_calibration.index[i]

            str_sub="sed -i 's/gw_storage=0.05/gw_storage=0.35/g' "+word_dir+"/CFE/*"
            out=subprocess.call(str_sub,shell=True)
            str_sub="sed -i 's/soil_storage=0.05/soil_storage=0.35/g' "+word_dir+"/CFE/*"
            out=subprocess.call(str_sub,shell=True)
            
            str_sub="rm flowveldepth_Ngen.h5"
            out=subprocess.call(str_sub,shell=True)
            str_sub="rm test_log"
            out=subprocess.call(str_sub,shell=True)
            str_sub="rm ngen-calibration* "
            out=subprocess.call(str_sub,shell=True)
            str_sub="rm reference.gpkg "
            out=subprocess.call(str_sub,shell=True)   
            str_sub="rm *parameter_df_state.parquet "
            out=subprocess.call(str_sub,shell=True) 


            str_sub="rm ./ngen-cal"
            out=subprocess.call(str_sub,shell=True)      
            #str_sub="ln -s /home/west/git_repositories/ngen-cal"
            str_sub="ln -s /home/west/git_repositories/ngen-cal/"
            out=subprocess.call(str_sub,shell=True)  
            
            str_sub="rm ./ngen"
            out=subprocess.call(str_sub,shell=True)         
            str_sub="ln -s /home/west/git_repositories/ngen_08022022/ngen"
            out=subprocess.call(str_sub,shell=True)  
            str_sub="source ~/git_repositories/ngen_08022022/ngen/venv2/bin/activate"
            out=subprocess.call(str_sub,shell=True)  
            
            str_sub="aws s3 cp --recursive s3://formulations-dev/CAMELS20/"+Folder_CAMELS+"/parameters ./parameters/"  
            out=subprocess.call(str_sub,shell=True)  
            
            str_sub="rm -rf ./t-route "
            out=subprocess.call(str_sub,shell=True) 
            
            str_sub="cp -rf /home/west/Projects/CAMELS/CAMELS_Files_Ngen/t-route ."  
            out=subprocess.call(str_sub,shell=True)  
            
            str_sub="cp "+calib_realiz_base + " ." 
            out=subprocess.call(str_sub,shell=True)  
            realiz_name=os.path.basename(calib_realiz_base)
            calib_realiz=word_dir+realiz_name
            
            str_sub="cp "+calib_config_base + " ." 
            out=subprocess.call(str_sub,shell=True)   
            
            calib_name=os.path.basename(calib_config_base)
            calib_config=word_dir+calib_name
            # Modify calib_config to have correct parameters and directory
            
            with open(calib_config, 'r') as stream:
                data_loaded_ori = yaml.load(stream,Loader=yaml.FullLoader)
            data_loaded = data_loaded_ori.copy()
            data_loaded['general']['workdir']=word_dir
            data_loaded['general']['iterations']=iterations
            data_loaded['general']['evaluation_start']=start_time
            data_loaded['general']['evaluation_stop']=end_time
            data_loaded['model']['realization']="./"+realiz_name
                        
            #catchment_data_file = word_dir/'spatial/catchment_data.geojson'
            NWM_param_file=word_dir+'/parameters/cfe.csv'
            soil_params=pd.read_csv(NWM_param_file,index_col=0)
            soil_params['gw_Zmax'] = soil_params['gw_Zmax'].fillna(16.0)/1000.
            soil_params['gw_Coeff'] = soil_params['gw_Coeff'].fillna(0.5)*3600*pow(10,-6)           
            dict_param_name={"maxsmc":"sp_smcmax_soil_layers_stag=1",
                             "satdk":"sp_dksat_soil_layers_stag=1",
                             "slope":"sp_slope",
                             "b":"sp_bexp_soil_layers_stag=1",
                             "Cgw":"gw_Coeff",
                             "expon":"gw_Expon",
                             "satpsi":"sp_psisat_soil_layers_stag=1",
                             "b":"gw_Expon",
                             "max_gw_storage":"gw_Zmax",
                             "refkdt":"sp_refkdt",
                             "slope":"sp_slope",
                             "wltsmc":"sp_smcwlt_soil_layers_stag=1"}
            
        
            n_params=data_loaded['model']['params']['CFE']
            for j in range(0,len(data_loaded['cfe_params'])):
                para=data_loaded['model']['params']['CFE'][j]['name']
                
                if para in dict_param_name:
                    data_loaded['cfe_params'][j]['init']=str(soil_params[dict_param_name[para]].mean())

            with io.open(calib_config, 'w') as outfile:
                yaml.dump(data_loaded, outfile)
            
            
            data_loaded_real_ori=json.load(open(calib_realiz))  
            data_loaded_real=data_loaded_real_ori.copy()
            
            for j in range(0,len(data_loaded['cfe_params'])):
                para=data_loaded['model']['params']['CFE'][j]['name']
                if para in dict_param_name:                              
                    data_loaded_real['global']['formulations'][0]['params']['modules'][1]['params']['model_params'][para]=soil_params[dict_param_name[para]].mean() 
            calib_realiz_ini=calib_realiz.replace(".json","ini.json")
            json_object=json.dumps(data_loaded_real,indent=4)
            with open(calib_realiz_ini,"w") as outfile:
                outfile.write(json_object)
            
            #str_sub="./ngen/cmake_build/ngen spatial/catchment_data.geojson \"all\" spatial/nexus_data.geojson \"all\" " + calib_realiz
            #out=subprocess.call(str_sub,shell=True)  
            # Ori_paramResults_old=calib_folder+"Ori_param/"           
            # Ori_paramResults=word_dir+"/Ori_param/"
            # os.mkdir(Ori_paramResults)
            # str_sub="mv "+Ori_paramResults_old+"/* " +Ori_paramResults
            # out=subprocess.call(str_sub,shell=True)
            # str_sub="rm -rf "+Ori_paramResults_old
            # out=subprocess.call(str_sub,shell=True)
            # str_sub="mv cat*.csv "+Ori_paramResults
            # out=subprocess.call(str_sub,shell=True)
            # str_sub="mv nex*.csv "+Ori_paramResults
            # out=subprocess.call(str_sub,shell=True)
            # str_sub="mv tnx*.csv "+Ori_paramResults
            # out=subprocess.call(str_sub,shell=True)    
            # str_sub="mv flowveldepth_Ngen.h5* "+Ori_paramResults
            # out=subprocess.call(str_sub,shell=True)            

            #str_sub="./ngen/cmake_build/ngen spatial/catchment_data.geojson \"all\" spatial/nexus_data.geojson \"all\" " + calib_realiz_ini
            #out=subprocess.call(str_sub,shell=True)  
            # Ori_paramResults_old=calib_folder+"Spatially_unif_ini/"
            # Ori_paramResults=word_dir+"/Spatially_unif_ini/"
            # os.mkdir(Ori_paramResults)
            # str_sub="mv "+Ori_paramResults_old+"/* " +Ori_paramResults
            # out=subprocess.call(str_sub,shell=True)
            # str_sub="rm -rf "+Ori_paramResults_old
            # out=subprocess.call(str_sub,shell=True)

            
            # os.mkdir(Ori_paramResults)
            # str_sub="mv cat*.csv "+Ori_paramResults
            # out=subprocess.call(str_sub,shell=True)
            # str_sub="mv nex*.csv "+Ori_paramResults
            # out=subprocess.call(str_sub,shell=True)
            # str_sub="mv tnx*.csv "+Ori_paramResults
            # out=subprocess.call(str_sub,shell=True)    
            # str_sub="mv flowveldepth_Ngen.h5* "+Ori_paramResults
            # out=subprocess.call(str_sub,shell=True)
            
            str_sub="python ./ngen-cal/python/calibration.py ./" +calib_name
            # Running calibration 
            print('Running calibration Ncat: ' + str(Selected_calibration.iloc[i]['NCat']))
            start_run_time=time.time()
            out=subprocess.call(str_sub,shell=True)
            end_run_time=time.time()
            elapsed_time = end_run_time - start_run_time
            print('Execution time:', elapsed_time, 'seconds' + " Ncat: " + str(Selected_calibration.iloc[i]['NCat']))

            #str_sub="rm -rf calib1"
            #out=subprocess.call(str_sub,shell=True)
            
            # flag=0;j=1
            # while(flag==0):
            #     calib_folder=word_dir+"calibSep_2_"+str(j)
            #     if not os.path.exists(calib_folder): 
            #         os.mkdir(calib_folder)
            #         flag=1
            #     j=j+1
             
            calib_folder=    word_dir+calib_output_folder
            
            os.mkdir(calib_folder)            
            LastRun=calib_folder+"/LastRun/"
            os.mkdir(LastRun)
            BestRun=calib_folder+"/BestRun/"
            os.mkdir(BestRun)

            str_sub="mv *best* "+BestRun
            out=subprocess.call(str_sub,shell=True)
            files=glob.glob(BestRun+"/*")
            for i_file in files: shutil.move(i_file, i_file.replace(".best.","."))
            
            str_sub="mv cat*.csv "+LastRun
            out=subprocess.call(str_sub,shell=True)
            str_sub="mv nex*.csv "+LastRun
            out=subprocess.call(str_sub,shell=True)
            str_sub="mv tnx*.csv "+LastRun
            out=subprocess.call(str_sub,shell=True)    
            str_sub="mv flowveldepth_Ngen.h5* "+LastRun
            out=subprocess.call(str_sub,shell=True)
            
            
            str_sub="mv "+calib_config+" "+calib_folder
            out=subprocess.call(str_sub,shell=True)
            str_sub="mv reference.gpkg "+calib_folder
            out=subprocess.call(str_sub,shell=True)          

            str_sub="mv ngen-calibration* "+calib_folder
            out=subprocess.call(str_sub,shell=True)
            str_sub="mv reference.gpkg "+calib_folder
            out=subprocess.call(str_sub,shell=True)   
            str_sub="mv "+calib_realiz+" "+calib_folder
            out=subprocess.call(str_sub,shell=True)
            str_sub="mv test_log* "+calib_folder
            out=subprocess.call(str_sub,shell=True)
            #str_sub="cp reference.gpkg "+calib_folder
            #out=subprocess.call(str_sub,shell=True) 
            str_sub="mv *parameter_df_state.parquet "+calib_folder
            out=subprocess.call(str_sub,shell=True) 
            
            
        except:
            log_file=open(Hydrofabrics_folder+"Calib_error.csv","a")
            log_file.write(hru_id)
            log_file.close()
            

    
