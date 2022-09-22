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
from random import randrange
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pptx
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches
from pptx import Presentation
from glob import glob
from datetime import datetime,timedelta
import sys
import df2img
sys.path.append("/home/west/Projects/CAMELS/CAMELS_Files_Ngen/")
import sens_analysis_functions as SA
from pptx.enum.text import PP_ALIGN
from fcmeans import FCM

sys.path.append("/home/west/git_repositories/ngen-cal/python/ngen_cal/")
import objectives as OB


# Input
CAMELS_Folder="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"
Output_Folder="/media/west/Expansion/Projects/CAMELS/CAMELS_Files_Ngen/Results/"
N_sample=6
Next_gen="/home/west/git_repositories/ngen_05032022_2/ngen "
start_time="2007-10-01 00:00:00"
end_time="2013-10-01 00:00:00"
flag_baseline=0 # 1 to use minimum, 2 to use maximum, 0 to useNWM
Spinup= 360 #in days
Flag_reRun=0 # Re-run even if files exists
Model_PET=["NOAH-OWP"]
Model_Runoff=['Topmodel']
Model_PET=["NOAH-OWP"]
Model_Runoff=['CFE_X']

#Model=["CFE"]
NCluster=17
#CriteriaAr=["Cluster_"+str(NCluster),"OnebyHUC(top)"]
#CriteriaAr=["Cluster_"+str(NCluster)]
CriteriaAr=["Selected"] #Option to select different basins
Var_dictionary={'Topmodel':['Qout','land_surface_water__runoff_mass_flux,land_surface_water__baseflow_volume_flux','land_surface_water__baseflow_volume_flux'],
                 'CFE':['Q_OUT','GIUH_RUNOFF','NASH_LATERAL_RUNOFF','DEEP_GW_TO_CHANNEL_FLUX','ACTUAL_ET','POTENTIAL_ET','GW_STORAGE','SOIL_STORAGE'],
                 'CFE_X':['Q_OUT','GIUH_RUNOFF','NASH_LATERAL_RUNOFF','DEEP_GW_TO_CHANNEL_FLUX','ACTUAL_ET','POTENTIAL_ET','GW_STORAGE','SOIL_STORAGE']}
Var_name={'Topmodel':['Qout','DIRECT_RUNOFF','BASEFLOW'],
          'CFE':['Q_OUT','DIRECT_RUNOFF','NASH_LATERAL_RUNOFF','DEEP_GW_TO_CHANNEL_FLUX','ACTUAL_ET','POTENTIAL_ET','GW_STORAGE','SOIL_STORAGE'],
          'CFE_X':['Q_OUT','DIRECT_RUNOFF','NASH_LATERAL_RUNOFF','DEEP_GW_TO_CHANNEL_FLUX','ACTUAL_ET','POTENTIAL_ET','GW_STORAGE','SOIL_STORAGE']}
stats=['Total','Q50','Peak']
Param_range_file_runoff={'Topmodel':'sens_params_topmodel.csv',
                  'CFE':'sens_params_cfe_04272022.csv',
                  'CFE_X':'sens_params_cfe_X_04272022.csv'}
Param_range_file_PET={'NOAH-OWP':'sens_params_noah.csv',
                      'PET': 'sens_params_pet.csv'}
Obj_functions_main=['nash_sutcliffe','normalized_nash_sutcliffe','custom']
Obj_functions_all=['peak_error_single','volume_error']
ArrayOfStats=['normalized_nash_sutcliffe','volume_error','peak_error_single']

GIUH=["1.0","0.34,0.33,0.33","0.01,0.01,0.01,0.34,0.33,0.3","0.01,0.01,0.01,0.01,0.01,0.01,0.34,0.3,0.3","0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.31,0.3,0.3","0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.3,0.3,0.28","0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.85"]

#Param_range_file=CAMELS_Folder+"sens_params_topmodel.csv"

# Read file with list of 516 CAMELS - remaining CAMELS are uncertain in terms of area
CAMELS_list_516="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/CAMELS_v3_complete.csv"
CAMELS_516=pd.read_csv(CAMELS_list_516,dtype={'hru_id_CAMELS': str})
CAMELS_516=CAMELS_516.set_index(['hru_id_CAMELS'])

CAMELS_names_file="/home/west/Projects/CAMELS/Attributes/camels_attributes_v2.0/camels_name.txt"
CAMELS_names=pd.read_csv(CAMELS_names_file, sep = ';',dtype={'gauge_id': str,'huc_02': str})
CAMELS_names=CAMELS_names.set_index(['gauge_id']) 
CAMELS_names.index.names = ['hru_id_CAMELS']

CAMELS_516=pd.concat([CAMELS_516,CAMELS_names],axis=1,join="inner")

CAMELS_sel=CAMELS_516[CAMELS_516['SA_analysis']==1]
CAMELS_sel=CAMELS_sel.sort_values(by=['frac_snow'],ascending=True)

SitesToRun=pd.DataFrame()
#SitesToRun=SitesToRun.append(CAMELS_516[CAMELS_516.index=='02177000'])
for crit_id in range(0,len(CriteriaAr)):
    Criteria=CriteriaAr[crit_id]
    
    if("HUC" in Criteria):
        for i in range(1,18):
            hru_id=CAMELS_516[CAMELS_516['huc_02']==str(i).zfill(2)].index[0]
            List_forcing=glob(CAMELS_Folder+"/"+hru_id+"/forcing/*.csv")
            if(len(List_forcing)==0):
                SitesToRun=SitesToRun.append(CAMELS_516[CAMELS_516['huc_02']==str(i).zfill(2)].iloc[1])
            else:
                SitesToRun=SitesToRun.append(CAMELS_516[CAMELS_516['huc_02']==str(i).zfill(2)].iloc[0])

    elif ("Cluster" in Criteria): 
        Cluster_var=np.array([CAMELS_516['aridity'].values,CAMELS_516['frac_snow'].values,CAMELS_516['p_seasonality'].values]).transpose()
        fcm=FCM(n_clusters=NCluster)
        fcm.fit(Cluster_var)
        fcm_centers=fcm.centers
        fcm_labels=fcm.predict(Cluster_var)
        CAMELS_516['Cluster']=fcm_labels
        
        for i in range(0,NCluster):        
            SitesToRun=SitesToRun.append(CAMELS_516[CAMELS_516['Cluster']==i].iloc[0])   
                
    elif ("Selected" in Criteria): 
        for i in range(0,NCluster):        
            SitesToRun=CAMELS_sel.copy()
    
    else:
        print("No Criteria found" )
        sys.exit()
    #Processed=pd.DataFrame(columns=['huc_02','gauge_name'])
    SitesToRun['Lat']=-9.0
    SitesToRun['Long']=-9.0
    for index_im in range(0,len(Model_Runoff)):
        m_runoff=  Model_Runoff[index_im]   
        m_PET=  Model_PET[index_im]           
        # Read minimum and maximum parameter values for runoff 
        Param_range_file_R=CAMELS_Folder+Param_range_file_runoff[m_runoff]
        param_range_runoff_all=pd.read_csv(Param_range_file_R,index_col=0) 
        param_range_runoff_all['Model']= m_runoff
        #param_range_runoff=param_range_runoff_file[param_range_runoff_file['sens_flag']==1] 
        
        
        Param_range_file_P=CAMELS_Folder+Param_range_file_PET[m_PET]
        param_range_PET_all=pd.read_csv(Param_range_file_P,index_col=0)   
        param_range_PET_all['Model']= m_PET      

        #param_range_PET=param_range_PET_file[param_range_PET_file['sens_flag']==1] 
        
        Gen_description=m_PET+"_"+m_runoff+ "_"+start_time.replace(' 00:00:00',"")+ "_"+end_time.replace(' 00:00:00',"")+"_Spinup"+str(Spinup)                                
        Range_param=pd.DataFrame()
        # Powerpoint=CAMELS_Folder+Criteria+"_"+m_runoff+"_Sens_analys_Nsample"+str(N_sample)+"_"+start_time.replace(' 00:00:00',"")+ "_"+end_time.replace(' 00:00:00',"")+"Spinup"+str(Spinup)+"_testv4.pptx"
        # if os.path.exists(Powerpoint): 
        #     print("delete powerpoint " + Powerpoint)
        #     sys.exit()

        Btw_site_comparison=Output_Folder+"/BTW_site_comparison/"
        if not os.path.exists(Btw_site_comparison): os.mkdir(Btw_site_comparison)  
        # prs = Presentation()
        # title_slide_layout=prs.slide_layouts[6]
        df_column_all_stats=['hru_id','cat_id','Variable','Objective','Param','Ratio_baseline','Param_Value','Value']
        Stats_All=pd.DataFrame()        
        for iss in range (9,len(SitesToRun)):  
            hru_id=SitesToRun.index[iss]   
            Folder=SitesToRun.iloc[iss]['Folder_CAMELS']  
            huc_02=SitesToRun.iloc[iss]['huc_02']
            if ("Cluster" in Criteria): 
                Cluster=SitesToRun.iloc[iss]['Cluster']
            else:
                Cluster=""
            #hru_id='01054200'
            #Working_dir
            Working_dir=CAMELS_Folder+"/"+ Folder+"/"
            
            
            Output_dir=CAMELS_Folder+"/"+ Folder+"/Sens_Analysis_NextGen_042022/" 
            if(not os.path.exists(Output_dir)): os.mkdir(Output_dir)
            
            
            
            if(os.path.exists(Working_dir)):
                # Sensitivity Analysis Directory
                
                
                outfolder_results= Output_dir+m_runoff+"/"   
                if not os.path.exists(outfolder_results): os.mkdir(outfolder_results)
                # Create folder for results     
                outfolder_results_hyd=outfolder_results+"/Hydrographs/"    
                if not os.path.exists(outfolder_results_hyd): os.mkdir(outfolder_results_hyd)                
                
                                
                Final_ouput=Output_Folder+Folder+"/Sens_Analysis_NextGen_042022/" +m_runoff+"/"
                # Select smallest basin
                Hydrofabrics=CAMELS_Folder+"/"+Folder+"/spatial/catchment_data.geojson"
                basin = gpd.read_file(Hydrofabrics) 
                basin_id=basin.sort_values(by="area_sqkm",ascending=True).iloc[0].id
                nexus_id=basin.sort_values(by="area_sqkm",ascending=True).iloc[0].toid
                SitesToRun.at[hru_id,'Lat']=basin.sort_values(by="area_sqkm",ascending=True).iloc[0].geometry.centroid.y
                SitesToRun.at[hru_id,'Long']=basin.sort_values(by="area_sqkm",ascending=True).iloc[0].geometry.centroid.x      
                SitesToRun_geo = gpd.GeoDataFrame(SitesToRun,geometry=gpd.points_from_xy(SitesToRun.Long,SitesToRun.Lat))
                Variables=Var_dictionary[m_runoff]
                Variables_names=Var_name[m_runoff]                
                
                Simulation_Descriptio=hru_id+ "-"+ basin_id  + Gen_description                            
                Output_Site_Baseline_file=Final_ouput+"Baseline"+Simulation_Descriptio+".csv"           
                Stats_Site_file=Final_ouput+"Stats_all_"+Simulation_Descriptio+".csv"
                param_range_mod_file=Final_ouput+"Param_range_mod_"+Simulation_Descriptio+".csv"
                param_range_file=Final_ouput+"Annotation_"+Simulation_Descriptio+".csv"
                str_ratio_file=Final_ouput+"Ratio"+Simulation_Descriptio+".csv"
                str_ratio_title="["
                
                if(not os.path.exists(Stats_Site_file)) | (not os.path.exists(param_range_file)) | (Flag_reRun==1): 
                    os.chdir(Output_dir)

                    Output_Site_Baseline_file=outfolder_results+"Baseline"+Simulation_Descriptio+".csv"           
                    Stats_Site_file=outfolder_results+"Stats_all_"+Simulation_Descriptio+".csv"
                    param_range_mod_file=outfolder_results+"Param_range_mod_"+Simulation_Descriptio+".csv"
                    param_range_file=outfolder_results+"Annotation_"+Simulation_Descriptio+".csv"
                    str_ratio_file=outfolder_results+"Ratio"+Simulation_Descriptio+".csv"
                    str_ratio_title="["
                    
                    [Run_nextgen,param_range_runoff_all,param_range_PET_all,Runoff_Config_FILES,PET_Config_FILES]=SA.prepare_data(m_PET,m_runoff,CAMELS_Folder,Working_dir,Output_dir,Next_gen,hru_id,basin_id,nexus_id,flag_baseline,param_range_runoff_all,param_range_PET_all,start_time,end_time)
                    
                    # STOPPED HERE
                    Increments=np.round(np.arange(0,1.01,1./N_sample),2)
                    param_range_sens=param_range_runoff_all[param_range_runoff_all['sens_flag']==1] 
                    param_range_sens=pd.concat([param_range_sens,param_range_PET_all[param_range_PET_all['sens_flag']==1]])
                    Param_range=pd.DataFrame(index=Increments,columns=param_range_sens.index)
                    Param_range=Param_range.fillna("")
                    for i in range(0,len(param_range_sens)):
                        if(param_range_sens.iloc[i]['Model']=='CFE') | (param_range_sens.iloc[i]['Model']=='Topmodel') | (param_range_sens.iloc[i]['Model']=='CFE_X') :
                            minValue=param_range_sens.iloc[i]['minValue']
                            maxValue=param_range_sens.iloc[i]['maxValue']             
                            parameter=param_range_sens.index[i]        
                            param_value=param_range_sens.iloc[i]['for_cat_rel']
                            param_value_abs=param_range_sens.iloc[i]['for_cat_abs']
                            if(param_value<=Param_range.index[0]): Param_range.at[0,parameter]="below"+str(round(param_value_abs,2))
                            for j in range(1,len(Param_range)):                
                                if(param_value>=Param_range.index[j-1]) & (param_value<Param_range.index[j]): Param_range.at[Param_range.index[j-1],parameter]=str(round(param_value_abs,2))
                            if(param_value>Param_range.index[len(Param_range)-1]): Param_range.at[Param_range.index[j+1],parameter]="above"  +round(str(param_value_abs)  ,2)
                        
                    nsim=0
                   
                    #Run Nextgen to obtain baseline results
                    out=subprocess.call(Run_nextgen,shell=True) 
                    
                    output=pd.read_csv("./"+basin_id+".csv",parse_dates=True,index_col=1)                    
                    
                    for iv in range(0,len(Variables)):
                        Variab_name=Variables[iv].split(",")
                        Out=output[Variab_name[0]].copy()
                        if(len(Variab_name)>1):                           
                           for ivv in range(1,len(Variab_name)):
                                Out=Out-output[Variab_name[ivv]]
                        output[Variables[iv]]=Out                                                                       
                        Nnan=Out.isna().sum()
                        if(Nnan>0):
                            print("Error: Nan in the baseline resuls: " + Run_nextgen)
                            #sys.exit()
                    
                    
                    Filename=outfolder_results_hyd+"BaselineHydrographs.png"
                    str_title="Baseline ID="+Simulation_Descriptio
                    SA.generate_hydrograph(output,Variables,Variables_names,Spinup,str_title,Filename)
                    output=output[output.index>output.index.min()+timedelta(days=Spinup)]   
                    output=output.dropna()
                    if(isinstance(output.index.min(),str)):
                        output.index=pd.to_datetime(output.index)
                    output_baseline=output.copy() 
                    
                    # Calculate the ratio of each runoff component
                    df_column_baseline=['hru_id','cat_id','Variable','Stats','Value']
                    Output_Site_Baseline=pd.DataFrame(columns=df_column_baseline)
                    str_ratio="["
                    
                    for i in range(1,len(Variables)):
                        Var=Variables[i]
                        Ratio=output[Var].sum()/output[Variables[0]].sum()
                        str_var="Ratio"+Var+"_"+Variables[0]
                        Output_Site_Baseline_temp=pd.DataFrame([(hru_id,basin_id,str_var,"Total",Ratio)],columns=df_column_baseline)
                        Output_Site_Baseline=pd.concat([Output_Site_Baseline,Output_Site_Baseline_temp])                    
                        str_ratio=str_ratio+str(round(Ratio,2))+","
                        str_ratio_title=str_ratio_title+Variables_names[i]+"/"+Variables_names[0]+","
    
                    str_ratio=str_ratio+"]"
                    str_ratio=str_ratio.replace(",]","]")
                    str_ratio_title=str_ratio_title+"]"
                    str_ratio_title=str_ratio_title.replace(",]","]")                
                    

                    All_parameter_sample=[]    
            
                    Stats_Site=pd.DataFrame() 
                    for i in range(0,len(param_range_sens)):
                        model=param_range_sens.iloc[i]['Model']
                        parameter=param_range_sens.index[i]
                        minValue=param_range_sens.iloc[i]['minValue']
                        maxValue=param_range_sens.iloc[i]['maxValue']
                        rangevalue=float(maxValue-minValue)
                        
                        if(rangevalue<0):
                            print("Check range parameter definition for " + parameter)
                            exit(0)
                        # Re-write CFE/topmodel Config file
                        for j in range(0,len(Increments)):
                            Mod_param=param_range_sens['for_cat_abs'].copy()
                            Modified_Parameter=str(minValue+Increments[j]*rangevalue)
                            if(parameter=="N_nash"):Modified_Parameter=str(int(minValue+Increments[j]*rangevalue))
                            if(parameter=="giuh_ordinates"):Modified_Parameter=GIUH[j]
                            All_parameter_sample.append([model,parameter,Increments[j],Modified_Parameter])


                    ## Include parallelization here 
                    for i_mod_param in range(0,len(All_parameter_sample)):  
                        #Create a folder inside of CFE with run_id
                        #Create a symbolic link to ngen
                        #Copy NOAH namelis
                        #Copy realization modified realization file
                        #Run_simulation(im,param_range_mod[im])
                        model=All_parameter_sample[i_mod_param][0]
                        parameter=All_parameter_sample[i_mod_param][1]
                        Increment=All_parameter_sample[i_mod_param][2]
                        Modified_Parameter=All_parameter_sample[i_mod_param][3]
                        
                        # TODO: Create function - Create config file
                        if(model=="CFE") | (model == "CFE_X"):
                            Mod_param=pd.read_csv(Runoff_Config_FILES[0],delimiter="=",index_col=0,header=None)
                            if("nash_storage" in parameter):
                                Nash_ori=Mod_param.loc['nash_storage'].values[0].split(",")
                                if("nash_storage1" in parameter): Mod_param.loc['nash_storage']=Modified_Parameter+","+Nash_ori[1]
                                else: Mod_param.loc['nash_storage']=Nash_ori[0]+","+Modified_Parameter
                            else:
                                Mod_param.loc[parameter]=Modified_Parameter
                            Mod_param.to_csv(Runoff_Config_FILES[1],sep="=",header=False)                            
                            str_sub="cp " + PET_Config_FILES[0] + " " + PET_Config_FILES[1]
                            out=subprocess.call(str_sub,shell=True) 
                            
                        elif(model=="Topmodel"):
                            #print("This needs to be fixed")
                            Topmodel_param="Senstivity analysis \n "
                            Params=pd.read_csv(Runoff_Config_FILES[0],delimiter=r"\s+",header=None,skiprows=1)
                            for i in range(0,len(param_range_runoff_all)):
                                if(parameter==param_range_runoff_all.index[i]): Params.at[0,i]=Modified_Parameter
                            for i in range(0,len(param_range_runoff_all)):
                                Topmodel_param=Topmodel_param+str(Params.at[0,i])+" "
                            fid=open(Runoff_Config_FILES[1],'w')
                            fid.write(Topmodel_param)
                            fid.close()            
                            str_sub="cp " + PET_Config_FILES[0] + " " + PET_Config_FILES[1]
                            out=subprocess.call(str_sub,shell=True) 
                        elif(model=="NOAH-OWP"):                            
                            fid=open(PET_Config_FILES[0],"r")
                            lines=fid.readlines()
                            flag=0
                            ic=0
                            while(flag==0):
                                ic=ic+1
                                if(parameter in lines[ic]):
                                    print (lines[ic])
                                    flag=1
                            Array_num=lines[ic].split(",")
                            new_string=lines[ic].split("=")[0]+" = "
                            for i in range(1,len(Array_num)):
                                new_string=new_string+Modified_Parameter+" , "
                            new_string=new_string+"\n"    
                            lines[ic]=new_string
                            
                            fid=open(PET_Config_FILES[1],'w')
                            for s in lines:
                                fid.write(s)
                            fid.close()  
                            str_sub="cp " + Runoff_Config_FILES[0] + " " + Runoff_Config_FILES[1]
                            out=subprocess.call(str_sub,shell=True)                             
                        else:
                            print("model not recognized : " + m_runoff)
                        print (parameter + " " + Modified_Parameter)
                        
                        out=subprocess.call(Run_nextgen,shell=True)          
                        try:
                            output=pd.read_csv("./"+basin_id+".csv",parse_dates=True,index_col=1)
                            #output=output.dropna()
                            if(isinstance(output.index.min(),str)):
                                output.index=pd.to_datetime(output.index)
                        except:
                            out=subprocess.call(Run_nextgen,shell=True) 
                            output=pd.read_csv("./"+basin_id+".csv",parse_dates=True,index_col=1) 
                            #output=output.dropna()
                            if(isinstance(output.index.min(),str)):
                                output.index=pd.to_datetime(output.index)
                        for iv in range(0,len(Variables)):
                            Variab_name=Variables[iv].split(",")
                            Out=output[Variab_name[0]].copy()
                            if(len(Variab_name)>1):                           
                               for ivv in range(1,len(Variab_name)):
                                    Out=Out-output[Variab_name[ivv]]
                            output[Variables[iv]]=Out                                                                       

                                                  
                        Filename=outfolder_results_hyd+parameter+str(Modified_Parameter)+"Hydrographs.png"
                        str_title=parameter+" - " + str(Modified_Parameter)+"\n ID="+hru_id+ " - "+ basin_id  + " From: "+start_time.replace(' 00:00:00',"")+" To: " +end_time.replace(' 00:00:00',"") + "Spinup: " + str(Spinup)

                        SA.generate_hydrograph(output,Variables,Variables_names,Spinup,str_title,Filename)
                        output=output[output.index>output.index.min()+timedelta(days=Spinup)]  
                        
                        # TODO: Create function - calculate stats
                        
                        Stats_Site_temp=SA.calculate_stats(hru_id,basin_id,parameter,Increment,Modified_Parameter,Variables,output_baseline,output,df_column_all_stats)
                        Stats_Site=pd.concat([Stats_Site,Stats_Site_temp])
                        # TODO: Create function - Generate plots and add to powerpoint(?)
                    
                        #Stats_Site=Stats_Site.set_index("hru_id")
                        #Output_Site_Baseline=Output_Site_Baseline.set_index("hru_id")
                        
                    
                    
                    Output_Site_Baseline.to_csv(Output_Site_Baseline_file)            
                    Stats_Site.to_csv(Stats_Site_file)
                    param_range_sens.to_csv(param_range_mod_file)
                    Param_range.to_csv(param_range_file)
                    #str_ratio.to_csv(str_ratio_file,delimiter=" ")
                    fid = open(str_ratio_file,'w')
                    fid.write(str_ratio)
                    fid.close()
                        
                    Filename_ID_QOut=outfolder_results+"ParamTable_"+Simulation_Descriptio+".png"
                    SA.Table_to_figure(m_runoff,param_range_sens,Filename_ID_QOut)
                    
                    str_command="mv -rf " + Output_dir + " " + Output_Folder+Folder
                    out=subprocess.call(str_command,shell=True) 
                else:
                    print ("Reading previous runs")
                    print(Output_Site_Baseline_file)
                    Output_Site_Baseline=pd.read_csv(Output_Site_Baseline_file,dtype={'hru_id': str,'huc_02': str})
                    Output_Site_Baseline=Output_Site_Baseline.set_index(['hru_id'])                        
                    Stats_Site=pd.read_csv(Stats_Site_file,dtype={'hru_id': str,'huc_02': str})
                    Stats_Site=Stats_Site.set_index(['hru_id'])
                    param_range_mod=pd.read_csv(param_range_mod_file,index_col='parameter')
                    Param_range=pd.read_csv(param_range_file,index_col=0)
                    fid = open(str_ratio_file,'r')
                    str_ratio=str(fid.readlines()).replace('[',"").replace(']',"")
                        
                                        
                for ii in range(0,len(Variables)):
                    Var=Variables[ii]
                    str_title=Variables_names[ii]+Simulation_Descriptio
                    str_title=str_title+"\n Ratio: " + str_ratio
                    Filename_ID_QOut=outfolder_results+"Heatmap"+Var.replace('land_surface_water__',"")+Simulation_Descriptio+".png"
                    range_temp=SA.generate_heatmap_rel_comparison_v2(Var,ArrayOfStats,Stats_Site,Param_range,str_title,Filename_ID_QOut)
                    if("Cluster" in Criteria): 
                        range_temp['hru_id']=hru_id;range_temp['huc_02']=huc_02;range_temp['Model']=m_runoff ;range_temp['Descrip']="HUC"+huc_02+"-C"+str(int(Cluster))+"-"+hru_id+"\n"+str_ratio
                    range_temp['hru_id']=hru_id;range_temp['huc_02']=huc_02;range_temp['Model']=m_runoff ;range_temp['Descrip']="HUC"+huc_02+"-"+hru_id+"\n"+str_ratio
                    Range_param=pd.concat([Range_param,range_temp])                            
                    Filename_ID_QOut=outfolder_results+"Scatter"+Var.replace('land_surface_water__',"")+Simulation_Descriptio+".png"
                    SA.generate_scatter_rel_comparison_v2(Var,ArrayOfStats,Stats_Site,Param_range,str_title,Filename_ID_QOut)

                Stats_All=pd.concat([Stats_All,Stats_Site])
        # something wrong with the calculation of the ange for each runoff variable.
        # Check for example 10336 - it is indicating 100% direct runoff
        # Since it is wrong I removed. 
        Range_param['Descrip']=Range_param['Descrip'].str.slice(0,14)
        title=Criteria+"_" + m_runoff + "_"+start_time.replace(' 00:00:00',"")+ "_"+end_time.replace(' 00:00:00',"")+" Spinup"+str(Spinup)+"\n"    
        title=title+str_ratio_title
        #if('Cgw' in Range_param.columns):Range_param=Range_param.drop(['Cgw'],axis=1)
        SA.Between_site_range(Range_param,Variables,Variables_names,ArrayOfStats,title,Btw_site_comparison) 
        
        ShowVariables=[Variables_names[0]]
        Filename_ID_QOut=Btw_site_comparison+title.split("\n")[0].replace(" ","")+"Boxplot_Q.png"
        SA.Range_parameter(Range_param,ShowVariables,ArrayOfStats,title,Filename_ID_QOut) 
        
        Stats_All.to_csv(Btw_site_comparison+Criteria+"_" + m_runoff + "_"+start_time.replace(' 00:00:00',"")+ "_"+end_time.replace(' 00:00:00',"")+" Spinup"+str(Spinup)+".csv")                                             
        Filename_ID_QOut=Btw_site_comparison+title.split("\n")[0].replace(" ","")+"Boxplot_Q_QL.png"
        ShowVariables=[Variables_names[0],Variables_names[1]]                
        SA.Range_parameter(Range_param,ShowVariables,ArrayOfStats,title,Filename_ID_QOut) 
        
        Stats_All.to_csv(Btw_site_comparison+Criteria+"_" + m_runoff + "_"+start_time.replace(' 00:00:00',"")+ "_"+end_time.replace(' 00:00:00',"")+" Spinup"+str(Spinup)+".csv")  
        Filename_ID_QOut=Btw_site_comparison+title.split("\n")[0].replace(" ","")+"Boxplot_QD_QL_QG.png"
        ShowVariables=[Variables_names[0],Variables_names[1],Variables_names[2]]        
        SA.Range_parameter(Range_param,ShowVariables,ArrayOfStats,title,Filename_ID_QOut) 
        Stats_All.to_csv(Btw_site_comparison+Criteria+"_" + m_runoff + "_"+start_time.replace(' 00:00:00',"")+ "_"+end_time.replace(' 00:00:00',"")+" Spinup"+str(Spinup)+".csv")  
                                                  
      
       
# for jj in range(0,len(ArrayOfStats)):
#     for ii in range(0,len(Var_name[m_runoff])):
        
#         sns.boxplot(x='Param',y='Value',hue='Objective',data=Temp)
#         Temp=Stats_All[Stats_All['Variable']==Var_name[m_runoff][ii]]
#         Temp=Temp[Temp['Objective'].isin(ArrayOfStats)]





            
        
        
        