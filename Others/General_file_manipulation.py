#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 15:41:10 2022

@author: west
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 11:32:28 2021

@author: west
"""


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
import matplotlib.pyplot as plt
import subprocess

# for example
Hyd_folder="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"
CAMELS_list_516="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/CAMELS_v3_complete.csv"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id_CAMELS': str})
CAMELS_516=CAMELS_516.set_index(['hru_id_CAMELS'])

for i in range (0,len(CAMELS_516)):   
    hru_id=CAMELS_516.index[i]
    Folder=CAMELS_516.loc[hru_id]['Folder_CAMELS']
    Hyd_folder_c=Hyd_folder+Folder+"/"
    HD_folder_c="/media/west/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/"+Folder+"/"
    str_sub="mv "+Hyd_folder_c+"/forcing.nc " +HD_folder_c
    out=subprocess.call(str_sub,shell=True)
    str_sub="rm "+Hyd_folder_c+"/*.nc.* "
    out=subprocess.call(str_sub,shell=True)    