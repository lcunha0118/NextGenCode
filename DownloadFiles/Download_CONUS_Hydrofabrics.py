#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  6 14:43:26 2021

@author: lcunha
"""


import os
#import geopandas as gpd
import subprocess

import zipfile
import pandas as pd
import generate_travel_time_by_pixel_sca as F1
import generate_giuh_per_basin_params_withUnits_sca as GIUH
import generate_twi_per_basin_sca as TWI
import argparse
import geopandas as gp

taudem="/usr/local/taudem/"
os.environ["PATH"] += os.pathsep + taudem
TauDEMDependencies="/home/west/TauDEMDependencies/mpich/mpich-install/bin"
os.environ["PATH"] += os.pathsep + TauDEMDependencies
TauDEMDependencies="/home/west/TauDEMDependencies/mpich/mpich-install/bin"
os.environ["GDAL_DATA"] = "/home/west/anaconda3/envs/ewatercycle/share/gdal"
os.environ["PROJ_LIB"] += os.pathsep + "/home/west/anaconda3/envs/ewatercycle/share/proj"
os.environ["PROJ_LIB"] += os.pathsep +"./usr/share/proj"


def main():
    #print("Start Running")
    parser = argparse.ArgumentParser()
    parser.add_argument("-hh", dest="Hydrofabrics_folder", type=str, required=True, help="The Hydrofabrics_folder directory with geojson")
    parser.add_argument("-d", dest="DEM_folder", type=str, required=True, help="The DEM output")
    parser.add_argument("-l", dest="list_huc", type=str, required=True, help="txt file with HUC")
    parser.add_argument("-rr", dest="re_run", type=int, required=False, default=0,help="If want to re run all processes")
    args = parser.parse_args()

    #retrieve parsed values
    Hydrofabrics_folder = args.Hydrofabrics_folder
    DEM_folder = args.DEM_folder
    list_huc = args.list_huc    
    re_run = args.re_run   
    
    
    #Hydrofabrics_folder="/media/west/Expansion/hydrofabrics/"
    #DEM_folder="/media/west/Expansion/DEM/"
    #Hydrofabrics_folder+"VPU_hydrofabrics.txt"
    VPU=pd.read_csv(list_huc)
    #print(VPU)
    print  ("re_run " + str(re_run))
    
#    
#    for i in range (0,len(VPU)):  
#        print(i)
#        if (re_run==1): 
#            print ("RE_RUN")
#            
#        vpu_id=VPU.iloc[i]['vpu']
#        huc=vpu_id[0:2]
#        Output_folder=Hydrofabrics_folder+"/"+vpu_id+"/"
#        print (Output_folder)
#        if not os.path.exists(Output_folder): os.mkdir(Output_folder)
#        zip_file=Output_folder+"nextgen_"+vpu_id+".zip"
#        gpkg_file=Output_folder+"nextgen_"+vpu_id+".gpkg" 
#        if not os.path.exists(zip_file) | (re_run==1): 
#            str_sub="aws s3 cp s3://nextgen-hydrofabric/v1.0/nextgen_"+vpu_id+".zip " +Output_folder   
#            out=subprocess.call(str_sub,shell=True)
#        if not os.path.exists(gpkg_file)  | (re_run==1): 
#            str_sub="aws s3 cp s3://nextgen-hydrofabric/v1.0/nextgen_"+vpu_id+".gpkg " +Output_folder   
#            out=subprocess.call(str_sub,shell=True)
#        if not os.path.exists(Output_folder+"/catchment_data.geojson")  | (re_run==1):
#            with zipfile.ZipFile(Output_folder+"nextgen_"+vpu_id+".zip","r") as zip_ref:
#                zip_ref.extractall(Output_folder)
#                # Data might not exist yet, so just run if data was successfully downloaded
#        
#        str_sub="rm -rf "+Output_folder+"flowpaths_4269.geojson"
#        out=subprocess.call(str_sub,shell=True)
#        str_sub="rm -rf "+Output_folder+"catchment_data_4269.geojson"
#        out=subprocess.call(str_sub,shell=True)         
#        if not os.path.exists(Output_folder+"/flowpaths_4269.geojson")  | (re_run==1):
#            str_sub="ogr2ogr -f \"GeoJSON\" "+Output_folder+"/flowpaths.geojson " +Output_folder+"/nextgen_"+vpu_id+".gpkg flowpaths"
#            out=subprocess.call(str_sub,shell=True)
#            str_sub="ogr2ogr -f \"GeoJSON\" "+Output_folder+"/flowpaths_4269.geojson " +Output_folder+"/flowpaths.geojson -s_srs EPSG:5070 -t_srs EPSG:4269"
#            out=subprocess.call(str_sub,shell=True)
#            str_sub="ogr2ogr -f \"GeoJSON\" "+Output_folder+"/catchment_data_4269.geojson " +Output_folder+"/catchment_data.geojson -s_srs EPSG:4326 -t_srs EPSG:4269"
#            print(str_sub)
#            print (Output_folder+"/catchment_data_4269.geojson ")
#            out=subprocess.call(str_sub,shell=True)
#    flow=pd.DataFrame()
#    for i in range (0,len(VPU)):  
#        vpu_id=VPU.iloc[i]['vpu']
#        Output_folder_hyd=Hydrofabrics_folder+"/"+vpu_id+"/"
#        flow_file=Output_folder_hyd+"/flowpaths_4269.geojson"
#        flow=pd.concat([flow,gp.read_file(flow_file)])
#    
#    flow.to_file(Hydrofabrics_folder+"/flowpaths_all_4269.geojson", driver='GeoJSON')
        
    for i in range (2,3):  
        HUC_str=str(i).zfill(2)
        HUC_int=i
        print(VPU["HUC"])
        HUC_temp=VPU[VPU["HUC"]==HUC_int]
        print(HUC_str)
        print(HUC_temp)
        print(len(HUC_temp))
        Output_folder_hyd=Hydrofabrics_folder+"/"+HUC_str+"/"
        #Output_folder=Hydrofabrics_folder+"/"+HUC_str+"/"
        
        cat_file=Output_folder_hyd+"/catchment_data_4269.geojson"
        flow_file=Output_folder_hyd+"/flowpaths_4269.geojson"
        if(len(HUC_temp)>=2):
            cat=pd.DataFrame()
            flow=pd.DataFrame()
            for j in range(0,len(HUC_temp)):
                vpu_id=HUC_temp.iloc[j]['vpu']
                Output_folder_hyd_temp=Hydrofabrics_folder+"/"+vpu_id+"/"
                
                
                cat_file=Output_folder_hyd_temp+"/catchment_data_4269.geojson"
                flow_file=Output_folder_hyd_temp+"/flowpaths_4269.geojson"
                cat=pd.concat([cat,gp.read_file(cat_file) ])       
                flow=pd.concat([flow,gp.read_file(flow_file)])
        #print(cat)  
            if not os.path.exists(Output_folder_hyd): os.mkdir(Output_folder_hyd)
            str_sub="rm -rf "+Output_folder_hyd+"/catchment_data_4269.geojson"
            out=subprocess.call(str_sub,shell=True)
            str_sub="rm -rf "+Output_folder_hyd+"/flowpaths_4269.geojson"
            out=subprocess.call(str_sub,shell=True)
            cat.to_file(Output_folder_hyd+"/catchment_data_4269.geojson", driver='GeoJSON')            
            flow.to_file(Output_folder_hyd+"/flowpaths_4269.geojson", driver='GeoJSON')
            
            
        cat_file_buffer=Output_folder_hyd+"/catchment_data_4269_buf.geojson"
        if not os.path.exists(cat_file_buffer): 
            Catchment_data = gp.read_file(cat_file) 
            Catchment_data["all"]=1
            Catchment_data = Catchment_data.dissolve(by='all')
            Catchment_data_buf = Catchment_data.buffer(0.2)            
            Catchment_data_buf.to_file(cat_file_buffer)  
        
        file_name=DEM_folder+"huc"+HUC_str+"-res-1.tif"
        file_name_90=DEM_folder+"huc"+HUC_str+"-res-190.tif"
        file_name_90cp=DEM_folder+"huc"+HUC_str+"-res-190cp.tif"
        namestr="huc"+HUC_str+"-res-190cp"
        file_name_90cpfel=DEM_folder+"huc"+HUC_str+"-res-190cpfel.tif"
        file_name_90cpang=DEM_folder+"huc"+HUC_str+"-res-190cpang.tif"
        file_name_90cpslp=DEM_folder+"huc"+HUC_str+"-res-190cpslp.tif"
        file_name_90cphf=DEM_folder+"huc"+HUC_str+"-res-190cphf.tif"
        file_name_90cpsca=DEM_folder+"huc"+HUC_str+"-res-190cpsca.tif"
        #file_name_90cpad8=DEM_folder+"huc"+huc+"-res-190cpad8.tif"
        #file_name_90cpsa=DEM_folder+"huc"+huc+"-res-190cpsa.tif"
        #file_name_90cpp=DEM_folder+"huc"+huc+"-res-190cpp.tif"
        file_name_90cpdt=DEM_folder+"huc"+HUC_str+"-res-190cpdt.tif"
        file_name_90cpwg=DEM_folder+"huc"+HUC_str+"-res-190cpwg1.tif"
        file_name_90cpdsave=DEM_folder+"huc"+HUC_str+"-res-190cpdsave1.tif"
        file_name_90cp_noweight=DEM_folder+"huc"+HUC_str+"-res-190cpdsave_noweight.tif"
        file_name_90cptwi=DEM_folder+"huc"+HUC_str+"-res-190cptwi.tif"
        


        if (not os.path.exists(file_name_90))  | (re_run==1): 
            str_sub="gdalwarp -overwrite "+file_name+" "+file_name_90+" -tr 0.0008333 0.0008333 -r max"
            out=subprocess.call(str_sub,shell=True)
        if (not os.path.exists(file_name_90cp) ) | (re_run==1): 
            str_sub="gdalwarp -cutline --config GDALWARP_IGNORE_BAD_CUTLINE YES "+cat_file_buffer+"-dstalpha "+file_name_90+" -dstnodata -999.0 " +file_name_90cp
            
            out=subprocess.call(str_sub,shell=True)
        if (not os.path.exists(file_name_90cpfel))  | (re_run==1):
            str_sub="mpiexec -np 8 pitremove -z "+file_name_90cp+" -fel "+file_name_90cpfel
            out=subprocess.call(str_sub,shell=True)
        if (not os.path.exists(file_name_90cpang))  | (re_run==1):
            str_sub="mpiexec -np 8 dinfflowdir -ang "+file_name_90cpang+" -slp "+file_name_90cpslp+" -fel "+file_name_90cpfel
            out=subprocess.call(str_sub,shell=True) 
        if (not os.path.exists(file_name_90cpsca))  | (re_run==1):
            str_sub="mpiexec -np 8 areadinf -ang "+file_name_90cpang+" -sca "+file_name_90cpsca
            print("Here 1 " + str_sub)
            out=subprocess.call(str_sub,shell=True) 
        #if (not os.path.exists(file_name_90cptwi))  | (re_run==1):
        str_sub="mpiexec -np 8 twi -slp "+file_name_90cpslp+" -sca "+file_name_90cpsca + " -twi "+ file_name_90cptwi
        out=subprocess.call(str_sub,shell=True) 
	#if test -f ${Outdir}${file_name}sca.tif; then
	#	echo "${Outdir}${file_name}sca.tif exists"
	#else
#		mpiexec -np $nproc  areadinf -ang ${Outdir}${file_name}ang.tif -sca ${Outdir}${file_name}sca.tif 
	#fi	
    
#        if (not os.path.exists(file_name_90cpsa))  | (re_run==1):
#            str_sub="mpiexec -np 8 slopearea "+file_name_90cp
#            out=subprocess.call(str_sub,shell=True) 
#        if (not os.path.exists(file_name_90cpp))  | (re_run==1):
#            str_sub="mpiexec -np 8 d8flowdir "+file_name_90cp
#            out=subprocess.call(str_sub,shell=True) 
#        if (not os.path.exists(file_name_90cpad8))  | (re_run==1):
#            print("Re-run " + file_name_90cpad8)
#            str_sub="mpiexec -np 8 aread8 "+file_name_90cp
#            out=subprocess.call(str_sub,shell=True)    
       
        if (not os.path.exists(file_name_90cphf))  | (re_run==1):
            str_sub="rm "+file_name_90cphf
            out=subprocess.call(str_sub,shell=True) 
            #if (not os.path.exists(file_name_90cphf))  | (re_run==1):
            str_sub="gdal_translate  -scale 0  40000000000000 0 0 "+file_name_90cpfel+" " + file_name_90cphf
            print (str_sub)
            out=subprocess.call(str_sub,shell=True) 
            print ("GENERATE FLOWPATH " + Hydrofabrics_folder+"/flowpaths_all_4269.geojson ")
            str_sub="gdal_rasterize -b 1 -burn 1  "+Hydrofabrics_folder+"/flowpaths_all_4269.geojson " +file_name_90cphf	
            print (str_sub)
            out=subprocess.call(str_sub,shell=True)  

        if (not os.path.exists(file_name_90cpdt))  | (re_run==1):
            str_sub="mpiexec -np 8 dinfdistdown -ang "+file_name_90cpang+" -fel "+file_name_90cpfel+" -src "+file_name_90cphf+" -dd "+file_name_90cpdt+" -m ave s"	
            out=subprocess.call(str_sub,shell=True)  
        
        if (not os.path.exists(file_name_90cpwg))  | (re_run==1):
            F1.generate_travel_time_by_pixel(namestr, DEM_folder, DEM_folder)

        #str_sub="rm "+file_name_90cpdsave
        #out=subprocess.call(str_sub,shell=True) 
        
        if (not os.path.exists(file_name_90cpdsave))  | (re_run==1):
            str_sub="mpiexec -np 8 dinfdistdown -ang " + file_name_90cpang+" -fel "+file_name_90cpfel+" -src "+file_name_90cphf+" -wg "+file_name_90cpwg+ " -dd "+file_name_90cpdsave+" -m ave s"
            out=subprocess.call(str_sub,shell=True)  
        
        if(len(HUC_temp)==1):       
            GIUH.generate_giuh_per_basin_withUnits(HUC_str,cat_file,file_name_90cpdsave,Output_folder_hyd+"cfe_noahowp_attributes.csv",Output_folder_hyd)
        else:
            for j in range(0,len(HUC_temp)):
                vpu_id=HUC_temp.iloc[j]['vpu']
                Output_folder_hyd=Hydrofabrics_folder+"/"+vpu_id+"/"
                cat_file=Output_folder_hyd+"/catchment_data_4269.geojson"
                print(" OUTPUT " + Output_folder_hyd)
                GIUH.generate_giuh_per_basin_withUnits(HUC_str,cat_file,file_name_90cpdsave,Output_folder_hyd+"cfe_noahowp_attributes.csv",Output_folder_hyd)

        if (not os.path.exists(file_name_90cp_noweight))  | (re_run==1):
            str_sub="mpiexec -np 8 dinfdistdown -ang " + file_name_90cpang+" -fel "+file_name_90cpfel+" -src "+file_name_90cphf+ " -dd "+file_name_90cp_noweight+" -m ave s"
            out=subprocess.call(str_sub,shell=True)  
#        if(len(HUC_temp)==1):       
#            print("twi" + file_name_90cptwi)
#            TWI.generate_twi_per_basin(HUC_str,cat_file,file_name_90cptwi,file_name_90cpslp,file_name_90cp_noweight,Output_folder_hyd+"cfe_noahowp_attributes.csv",Output_folder_hyd)
#        else:
#            for j in range(0,len(HUC_temp)):
#                vpu_id=HUC_temp.iloc[j]['vpu']
#                Output_folder_hyd=Hydrofabrics_folder+"/"+vpu_id+"/"
#                cat_file=Output_folder_hyd+"/catchment_data_4269.geojson"
#                print(" OUTPUT " + Output_folder_hyd)
#                TWI.generate_twi_per_basin(HUC_str,cat_file,file_name_90cptwi,file_name_90cpslp,file_name_90cp_noweight,Output_folder_hyd+"cfe_noahowp_attributes.csv",Output_folder_hyd)
# 

# namestr='01022500'
# catchments='../PerBasin4//'+namestr+'/spatial/catchment_data.geojson'
# twi_raster='../PerBasin4//'+namestr+'/'+namestr+'twi.tif'
# slope_raster='../PerBasin4//'+namestr+'/'+namestr+'slp.tif'
# dist_to_outlet_raster='../PerBasin4//'+namestr+'/'+namestr+'dsave_noweight.tif'
# outputfolder_twi="../PerBasin4/data_CAMELS/"+namestr+"/"


# nodata_value = -999
# buffer_distance = 0.001
# output_flag = 1
# global_src_extent = 0
                
                          
if __name__ == "__main__":
    main()