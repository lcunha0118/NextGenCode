#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 10:23:53 2022

@author: west
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 14:01:06 2022

@author: west
"""
from pathlib import Path
import matplotlib.pylab as plt
import json
#from ngen_cal import plot_objective, plot_stuff, plot_obs, plot_output, plot_parameter_space
import pandas as pd
import os
import subprocess
import time
import yaml
import io


CAMELS_list_516="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/CAMELS_v3_complete.csv"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id_CAMELS': str})
CAMELS_516=CAMELS_516.set_index(['hru_id_CAMELS'])


Select_calibration="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/Select_calibration_HLR_RFC.csv"
Select_cal=pd.read_csv(Select_calibration,dtype={'hru_id_CAMELS': str})
Select_cal=Select_cal.set_index(['hru_id_CAMELS'])

ngen_utilities="/home/west/git_repositories/ngen_08022022/ngen/utilities/data_conversion"
for i in range(0,len(Select_cal)):
    Folder_CAMELS=Select_cal.iloc[i]['Folder_CAMELS']
    input_dir="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"+Folder_CAMELS+"/forcing/"
    output_file="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"+Folder_CAMELS+"/forcing.nc"
    if os.path.exists(output_file):
        print ("File Exists: "+Folder_CAMELS)
        
    else: 
        os.chdir(ngen_utilities)
    
        str_sub="python csv2catchmentnetcdf.py -i "+input_dir+ " -o "+ output_file+ " -j 2"
        out=subprocess.call(str_sub,shell=True)          