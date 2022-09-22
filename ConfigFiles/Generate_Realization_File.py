#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 29 11:29:40 2021

@author: west
"""


import os
import sys, getopt
import geopandas as gpd
import random
import json
from shutil import copy
import fileinput
import subprocess
import pandas as pd
import copy

# #Set directory path for catchment specific BMI configuration files
# bmi_config_dir = "./catchment_bmi_configs"

# #Set paths from where to retrieve catchment specific files
# global_catchment_specific_file_from_path = "../global_catchment_specific_files"
# if not os.path.exists(global_catchment_specific_file_from_path): os.mkdir(global_catchment_specific_file_from_path)
# formulation_1_catchment_specific_file_from_path = "../data/catchment_specific_files"
# if not os.path.exists(formulation_1_catchment_specific_file_from_path):os.mkdir(formulation_1_catchment_specific_file_from_path)
# #Set forcing file path
# forcing_file_path = "./data/forcing/"

# #Set forcing file date time
# forcing_file_date_time = "2012-05-01_00_00_00_2012-06-29_23_00_00"

# #Set forcing file extenstion
# forcing_file_extension = ".csv"


# #Set params
# global_params = {
#   "model_type_name": "bmi_c_cfe",
#   "library_file": "../ngen_test_setup/ngen/extern/alt-modular/cmake_am_libs/libcfebmi.so",
#   "init_config": "",
#   "main_output_variable": "Q_OUT",
#   "registration_function": "register_bmi_cfe",
#   "variables_names_map" : {
#     "water_potential_evaporation_flux" : "potential_evapotranspiration",
#     "atmosphere_water__liquid_equivalent_precipitation_rate" : "precip_rate",
#     "atmosphere_air_water~vapor__relative_saturation" : "SPFH_2maboveground",
#     "land_surface_air__temperature" : "TMP_2maboveground",
#     "land_surface_wind__x_component_of_velocity" : "UGRD_10maboveground",
#     "land_surface_wind__y_component_of_velocity" : "VGRD_10maboveground",
#     "land_surface_radiation~incoming~longwave__energy_flux" : "DLWRF_surface",
#     "land_surface_radiation~incoming~shortwave__energy_flux" : "DSWRF_surface",
#     "land_surface_air__pressure" : "PRES_surface"
#      },
#   "uses_forcing_file": False,
#   "allow_exceed_end_time": True
# }

# formulation_1_params = {
#   "model_type_name": "bmi_topmodel",
#   "library_file": "../ngen_test_setup/ngen/extern/alt-modular/cmake_am_libs/libtopmodelbmi.so",
#   "init_config": "",
#   "main_output_variable": "Qout",
#   "registration_function": "register_bmi_topmodel",
#   "variables_names_map" : {
#     "water_potential_evaporation_flux" : "potential_evapotranspiration",
#     "atmosphere_water__liquid_equivalent_precipitation_rate" : "precip_rate"
#      },
#   "uses_forcing_file": False
# }

# #Set BMI config file params
# global_bmi_params = {
#   "forcing_file": "BMI",
#   "soil_params.depth": "2.0",
#   "soil_params.b": "4.05",
#   "soil_params.mult": "1000.0",
#   "soil_params.satdk": "0.00000338",
#   "soil_params.satpsi": "0.355",
#   "soil_params.slop": "1.0",
#   "soil_params.smcmax": "0.439",
#   "soil_params.wltsmc": "0.066",
#   "max_gw_storage": "16.0",
#   "Cgw": "0.01",
#   "expon": "6.0",
#   "gw_storage": "50%",
#   "alpha_fc": "0.33",
#   "soil_storage": "66.7%",
#   "K_nash": "0.03",
#   "K_lf": "0.01",
#   "nash_storage": "0.0,0.0",
#   "giuh_ordinates": "0.06,0.51,0.28,0.12,0.03"
# }

# formulation_1_bmi_params = {
#    "name": "Catchment Calibration Data",
#    "inputs_file": "inputs.dat", #currently unused file
#    "subcat_file": "", #given unique name per catchment
#    "params_file": "../param_files/params.dat", #enter path to single file shared by all catchments
#    "topmod_output_file": "topmod.out", #leave as is for now
#    "hydro_output_file": "hyd.out" #leave as is for now
# }

# #Set global forcing
# global_forcing = {
#   "file_pattern": ".*{{id}}.*." + forcing_file_extension,
#   "path": forcing_file_path
# }

# #Set time values
# start_time = "2012-05-01 00:00:00"
# end_time = "2012-05-02 23:00:00"
# output_interval = 3600


def read_catchment_data_geojson(catchment_data_file,ID_format):
  """
  Read cathcment data from geojson file and return a series
  of catchment ids.
  """
  catchment_data_df = gpd.read_file(catchment_data_file)
  catchment_id_series = catchment_data_df[ID_format]
  
  return catchment_id_series




def set_up_config_dict(catchment_df,Model,Dir,Subset,start_time,end_time,output_interval,remove_key,ID_format,Flag):
                       
  """
  Construct and return a dictionary for the entire configuration
  """

  #Convert catchment_df to dictionary
  catchment_dict = catchment_df.to_dict()
  # Opening JSON file
  with open(Model['Example_Realization']) as json_file:
    data = json.load(json_file)
  if(Model["Type"]=="Multi"): key='global'
  else: key='cat-27'
  global_real=copy.deepcopy(data[key])
  global_real['forcing']['file_pattern']="{{id}}.csv"
  global_real['forcing']['provider']="CsvPerFeature"
  global_real['forcing']['path']=Dir+"forcing/"
  #Outline of full config dictionary

  if(Model['Formulation_Name']=='bmi_multi_noahmp_cfe'):
      global_real['formulations'][0]['params']['modules'][0]['params']['init_config']=Dir+Model['Init_conf_dir'][0]+"/{{id}}.input"
      global_real['formulations'][0]['params']['modules'][1]['params']['init_config']=Dir+Model['Init_conf_dir'][1]+"/{{id}}_bmi_config_cfe_pass.txt"
  elif(Model['Formulation_Name']=='bmi_multi_noahmp_topmodel'):
      global_real['formulations'][0]['params']['modules'][0]['params']['init_config']=Dir+Model['Init_conf_dir'][0]+"/{{id}}.input"
      global_real['formulations'][0]['params']['modules'][1]['params']['init_config']=Dir+Model['Init_conf_dir'][1]+"/topmod_{{id}}.run"
  elif(Model['Formulation_Name']=='CFE'):
      global_real['formulations'][0]['params']['init_config']=Dir+Model['Init_conf_dir']+"/{{id}}_bmi_config_cfe_pass.txt"
  elif(Model['Formulation_Name']=='topmodel'):
      global_real['formulations'][0]['params']['init_config']=Dir+Model['Init_conf_dir']+"/topmod_{{id}}.run"
  elif(Model['Formulation_Name']=='bmi_fortran_noahmp'):
      global_real['formulations'][0]['params']['init_config']=Dir+Model['Init_conf_dir']+"/{{id}}.input"
  else: 
      print ("Check Formulation_Name " + Model['Formulation_Name'])
      exit()
          
      
      print ("Single")
    #Cycle through each catcment and add the catchment name/id, formulation,
  #and the formulation's corresponding params to the config dictionary.
  if(Flag=="All_basins"):
      config_dict = {
        "global": global_real,
        "time":
        {
          "start_time": start_time,
          "end_time": end_time,
          "output_interval": output_interval
        },
        "catchments": {}
      }
 
      if(Model["Type"]=="Single"):
          for index, row in catchment_df.iterrows():
            catchment_id = catchment_df.at[index, ID_format]
            catchment_id_file=catchment_df.at[index, ID_format]
            
            if(catchment_id_file==1): 
                catchment_id_file="cat-"+str(int(catchment_id_file))
            if(isinstance(catchment_id_file, float)): 
                catchment_id_file=str(int(catchment_id_file))
                catchment_id_file="cat-"+catchment_id_file
            if(not "cat" in catchment_id_file): catchment_id_file="cat-"+catchment_id_file
    
            if(catchment_id in Subset):
                Tempdict=copy.deepcopy(data[key])
                for i in remove_key:        
                    Tempdict['formulations'][0]['params'].pop(i, None)
                Tempdict['formulations'][0]['params']['init_config']=Dir+Model['Init_conf_dir']+"/"+catchment_id_file+'.csv'
            
                #Tempdict['forcing']['path']='./data/forcing/'+catchment_id+'.csv'
                Tempdict['forcing']['path']=Dir+'/forcing/'+catchment_id_file+'.csv'
                catchment_dict = {catchment_id: Tempdict}
                config_dict["catchments"].update(catchment_dict)
      else:   
          del data[key]['forcing']['file_pattern']
          for index, row in catchment_df.iterrows():
            catchment_id = catchment_df.at[index, ID_format]
            catchment_id_file=catchment_df.at[index, ID_format]
        
            if(catchment_id_file==1): 
                catchment_id_file="cat-"+str(int(catchment_id_file))
            if(isinstance(catchment_id_file, float)): 
                catchment_id_file=str(int(catchment_id_file))
                catchment_id_file="cat-"+catchment_id_file
            if(not "cat" in catchment_id_file): catchment_id_file="cat-"+catchment_id_file
            
            if(catchment_id in Subset):
                Tempdict=copy.deepcopy(data[key])
                for i in remove_key:        
                    Tempdict['formulations'][0]['params'].pop(i, None)
                    if(Model['Formulation_Name']=='bmi_multi_noahmp_cfe'):
                        Tempdict['formulations'][0]['params']['modules'][0]['params']['init_config']=Dir+Model['Init_conf_dir'][0]+"/"+catchment_id_file+".input"
                        Tempdict['formulations'][0]['params']['modules'][1]['params']['init_config']=Dir+Model['Init_conf_dir'][1]+"/"+catchment_id_file+"_bmi_config_cfe_pass.txt"
                    elif(Model['Formulation_Name']=='bmi_multi_noahmp_topmodel'):
                        Tempdict['formulations'][0]['params']['modules'][0]['params']['init_config']=Dir+Model['Init_conf_dir'][0]+"/"+catchment_id_file+".input"
                        Tempdict['formulations'][0]['params']['modules'][1]['params']['init_config']=Dir+Model['Init_conf_dir'][1]+"/"+catchment_id_file+"_topmod.run"


                
                #Tempdict['forcing']['path']='./data/forcing/'+catchment_id+'.csv'
                Tempdict['forcing']['path']=Dir+'/forcing/'+catchment_id_file+'.csv'
                catchment_dict = {catchment_id: Tempdict}
                config_dict["catchments"].update(catchment_dict)
  else:
      config_dict = {
        "global": global_real,
        "time":
        {
          "start_time": start_time,
          "end_time": end_time,
          "output_interval": output_interval
        },
      }
    # catchment_formulation = catchment_df.at[index, "Formulation"]
    # catchment_formulation_name = catchment_df.at[index, "Formulation_Name"]
    
    # forcing_file_name = catchment_id + "_" + forcing_file_date_time + forcing_file_extension

    # forcing_file_name_and_path = os.path.join(forcing_file_path, forcing_file_name) 

    # forcing_dict = {"path": forcing_file_name_and_path}

    # #Add catchment name/id and params
    # if catchment_formulation == global_formulation:
      
    #   #Call to create unique directory to hold BMI configuraton file for the given catchment
    #   bmi_config_file = create_catchment_bmi_directory_and_config_file(catchment_id, global_bmi_params, "global_formulation")

    #   global_params_for_catchment = global_params.copy()

    #   global_params_for_catchment["init_config"] = bmi_config_file
      
    #   #Use below if forcing file is passed through BMI
    #   #global_params_for_catchment["forcing_file"] = forcing_file_name_and_path

    #   formulation_dict = {"name": catchment_formulation_name, "params": global_params_for_catchment}

    # else:
      
    #   #Call to create unique directory to hold BMI configuraton file for the given catchment
    #   bmi_config_file = create_catchment_bmi_directory_and_config_file(catchment_id, formulation_1_bmi_params, "formulation_1")

    #   formulation_1_params_for_catchment = formulation_1_params.copy()

    #   formulation_1_params_for_catchment["init_config"] = bmi_config_file
      
    #   #Use below if forcing file is passed through BMI
    #   #formulation_1_params_for_catchment["forcing_file"] = forcing_file_name_and_path
      
    #   formulation_dict = {"name": catchment_formulation_name, "params": formulation_1_params_for_catchment}
      
    # #Formulations is a list with currently only one formulation.
    # #The ability to add multiple formulations for each catchment will
    # #be added in the future.
    # formulations_list = []

    #formulations_list.append(formulation_dict)


    
  return config_dict


def dump_dictionary_to_json(config_dict, output_file):
  """
  Dump config dictionary to JSON file
  """

  with open(output_file, "w") as open_output_file: 
    json.dump(config_dict, open_output_file, indent=4)


def dump_dictionary_to_ini(config_dict, output_file):
  """
  Dump config dictionary to INI file
  """
    
  with open(output_file, "w") as open_output_file: 
    for key, value in config_dict.items():
      open_output_file.write(key + "=" +  value + "\n")                 


def dump_dictionary_values_to_text_file(config_dict, output_file):
  """
  Dump config dictionary values to text file
  """
    
  with open(output_file, "w") as open_output_file: 
    for key, value in config_dict.items():
      open_output_file.write(value + "\n")                 

def create_hydrofabric_subset(catchment_file,nexus_file,Subset,Subset_name,ID_format):
    ######### Create a subset for catchment
    output_file=catchment_file.replace(".geojson",Subset_name+".geojson")
    with open(catchment_file) as json_file:
        data = json.load(json_file)
    i=0
    while i<len(data['features']):
        if not data['features'][i]['properties'][ID_format] in Subset:
            print ("deleting " + str(data['features'][i]['properties'][ID_format]))
            del data['features'][i]        
        else:
            i=i+1
    data        
    with open(output_file, "w") as open_output_file: 
            json.dump(data, open_output_file)
    
    ######### Create a subset for nexus
    output_file=nexus_file.replace(".geojson",Subset_name+".geojson")
    with open(nexus_file) as json_file:
        data = json.load(json_file)
    i=0
    while i<len(data['features']):
        if not data['features'][i]['properties']['realized_catchment'] in Subset:
            print ("deleting " + str(data['features'][i]['properties']['realized_catchment']))
            del data['features'][i]   
        else:
            i=i+1
    with open(output_file, "w") as open_output_file: 
            json.dump(data, open_output_file)
        
## User input
#catchment_file="/home/west/git_repositories/topmodel_fork_NOAA/topmodel/params/data/hydrofabrics/releases/beta/01a/catchments_id.geojson"
#nexus_file="/home/west/git_repositories/topmodel_fork_NOAA/topmodel/params/data/hydrofabrics/releases/beta/01a/flowpaths_id.geojson"
Desired_Model=["NOAH_CFE","NOAH_topmodel","NOAH-MP","CFE","topmodel"]
Desired_Model=["CFE","topmodel"]
Example_Realization_Dir="/home/west/git_repositories/topmodel_fork_NOAA/topmodel/params/data/"
start_time="2007-01-01 00:00:00" #"2007-01-01 00:00:00"
end_time="2019-12-30 00:00:00" #"2019-12-31 00:00:00" 
Subset=[]
Subset_name='Test'

output_interval=3600

## Models setup
# Model is user defined
# Example_realization: example of configurations 
# Formulation_Name is the "model_type_name"
# Formulation is "name"
Model_dic={
    'Model':['NOAH-MP',"CFE","topmodel","NOAH_CFE","NOAH_topmodel"],
    'Type':['Single',"Single","Single","Multi","Multi"],
    'Example_Realization':[Example_Realization_Dir+'Example_realization_noahmp.json',Example_Realization_Dir+"Example_realization_CFE.json",Example_Realization_Dir+"Example_realization_topmodel.json",Example_Realization_Dir+"Example_realization_NOAH_CFE_2.json",Example_Realization_Dir+"Example_realization_NOAH_Topmodel_2.json"],
    'Formulation_Name':['bmi_fortran_noahmp',"CFE","topmodel","bmi_multi_noahmp_cfe","bmi_multi_noahmp_topmodel"],
    'Formulation':['bmi_fortran',"bmi_c","bmi_c","bmi_multi","bmi_multi"],
    'Init_conf_dir':['NOAH',"CFE","Topmodel",["NOAH","CFE"],["NOAH","Topmodel"]]}
Model_df=pd.DataFrame(data=Model_dic)
Model_df=Model_df.set_index('Model')
## End of Model setup   

# for example
Hyd_folder="/home/west/Projects/CAMELS/PerBasin4/"
CAMELS_list_516="/home/west/Projects/CAMELS/camels_basin_list_516.txt"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id': str})
CAMELS_516=CAMELS_516.set_index(['hru_id'])   
CAMELS_516=CAMELS_516.append(pd.DataFrame(index=['HUC01']))

General_Dir="/data_CAMELS/"
ID_format="id"
len(CAMELS_516)

for i in range (0,len(CAMELS_516)):    
    hru_id=CAMELS_516.index[i]
    print (hru_id)
    outfolder=Hyd_folder+"/"+hru_id+"/"
    str_sub="rm "+Hyd_folder+"data_CAMELS/"+hru_id+'/Reali*All_basins.json'
    out=subprocess.call(str_sub,shell=True)
    catchment_file=Hyd_folder+"/"+hru_id+'/spatial/catchment_data.geojson'    
    if(os.path.isfile(catchment_file)):
        catchment_df = read_catchment_data_geojson(catchment_file,ID_format).to_frame()
        catchment_df['Formulation']=""
        catchment_df['Formulation_Name']=""
        Subset=catchment_df[ID_format].values
        Dir="./"
        for model in Desired_Model:
            Flag="Only_Global"   # Options: Only_Global or All_basins
            output_file=Hyd_folder+"data_CAMELS/"+hru_id+'/Realization_'+hru_id+"_"+Model_df.at[model,'Formulation_Name']+Flag+".json"
            catchment_df['Formulation']=Model_df.at[model,'Formulation']
            catchment_df['Formulation_Name']=Model_df.at[model,'Formulation_Name']
            remove_key=['variables_names_map']
    
            config_dict = set_up_config_dict(catchment_df,Model_df.loc[model],Dir,Subset,start_time,end_time,output_interval,remove_key,ID_format,Flag)    
            dump_dictionary_to_json(config_dict, output_file)
            #create_hydrofabric_subset(catchment_file,nexus_file,Subset,Subset_name,ID_format)
            # Flag="All_basins"   # Options: Only_Global or All_basins
            # output_file=Hyd_folder+"data_CAMELS/"+hru_id+'/Realization_'+hru_id+"_"+Model_df.at[model,'Formulation_Name']+Flag+".json"
            # catchment_df['Formulation']=Model_df.at[model,'Formulation']
            # catchment_df['Formulation_Name']=Model_df.at[model,'Formulation_Name']
            # remove_key=['variables_names_map']
    
            # config_dict = set_up_config_dict(catchment_df,Model_df.loc[model],Dir,Subset,start_time,end_time,output_interval,remove_key,ID_format,Flag)    
            # dump_dictionary_to_json(config_dict, output_file)
