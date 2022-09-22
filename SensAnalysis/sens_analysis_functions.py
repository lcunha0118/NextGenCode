#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 09:29:00 2022

@author: west
"""
import pandas as pd
def generate_heatmap_rel_comparison(Var,stats,Output_All,Param_range,str_title,Filename_ID_QOut):
    
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    fig,(ax)= plt.subplots(len(stats),1, figsize = (10,8))
    cmap = sns.color_palette("seismic", as_cmap=True)
    cmap=cmap.reversed()
    cmap.set_bad(color='yellow')
    Range=pd.DataFrame()
    for i in range(0,len(stats)):
        Output_All_filter=Output_All[(Output_All['Variable']==Var) & (Output_All['Stats']==stats[i])][['Param','Ratio_baseline','Rel_Dif']]
        Output_All_filter_pivot=Output_All_filter.pivot(index='Ratio_baseline',columns='Param')
        Output_All_filter_pivot=Output_All_filter_pivot.Rel_Dif[Param_range.columns.values]
        if(len(stats)>1):    y=ax[i]
        else: y=ax
        y=sns.heatmap(Output_All_filter_pivot.astype(float,errors='raise'), cmap = cmap, 
                    cbar_kws = {'pad': 0.015, 'ticks': [-1,0,1],
                                'label': Var.replace('land_surface_water__',"")+"-"+stats[i]+'\nRelative difference to baseline'}, 
                    linewidths = 0.50, linecolor = 'grey', ax = y,annot=Param_range,annot_kws={"color":"black"},fmt="",
                    vmin=-1, vmax=1)
        #ax1.plot(param_range_mod['for_cat'],'o',color='gray')
        y.invert_yaxis()
        y.set(ylabel="Normalized range")
        y.set(ylabel="Normalized range",xlabel="Parameters")
        if(i==0): y.set_title(str_title)
        if(i<len(stats)-1): y.axes.xaxis.set_visible(False)
        
        Range_temp=(Output_All_filter_pivot.max()-Output_All_filter_pivot.min()).to_frame()
        Range_temp=Range_temp.rename(columns={Range_temp.columns[0]:Var}).transpose()
        Range_temp['stats']=stats[i]
        Range=pd.concat([Range,Range_temp])
    fig.savefig(Filename_ID_QOut, bbox_inches='tight',dpi=300)
    plt.close()   
    return Range
    
def generate_heatmap_rel_comparison_v2(Var,ArrayOfStats,Stats_All,Param_range,str_title,Filename_ID_QOut):
    
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    fig,(ax)= plt.subplots(len(ArrayOfStats),1, figsize = (10,8))
    cmap = sns.color_palette("seismic", as_cmap=True)
    cmap=cmap.reversed()
    cmap.set_bad(color='yellow')  
    Range=pd.DataFrame()
    for i in range(0,len(ArrayOfStats)):
        Stats_All_filter=Stats_All[(Stats_All['Variable']==Var) & (Stats_All['Objective']==ArrayOfStats[i])][['Param','Ratio_baseline','Value']]
        Output_All_filter_pivot=Stats_All_filter.pivot(index='Ratio_baseline',columns='Param')
        Output_All_filter_pivot=Output_All_filter_pivot.Value[Param_range.columns.values]
        if(len(ArrayOfStats)>1):    y=ax[i]
        else: y=ax

        if(ArrayOfStats[i]=="normalized_nash_sutcliffe"): 
            v_min=0; v_max=1 
            cmap = sns.color_palette("Reds", as_cmap=True)
            cmap=cmap.reversed()
            cmap.set_bad(color='yellow')
        elif(ArrayOfStats[i]=="custom"): 
            v_min=0; v_max=1 
            cmap = sns.color_palette("Reds", as_cmap=True)
            cmap.set_bad(color='yellow')
        else: 
            v_min=-1; v_max=1
            cmap = sns.color_palette("seismic", as_cmap=True)
            cmap=cmap.reversed()
            cmap.set_bad(color='yellow')
            
        y=sns.heatmap(Output_All_filter_pivot.astype(float,errors='raise'), cmap = cmap, 
                    cbar_kws = {'pad': 0.015, 'ticks': [-1,0,1],
                                'label': ArrayOfStats[i]}, 
                    linewidths = 0.50, linecolor = 'grey', ax = y,annot=Param_range,annot_kws={"color":"black"},fmt="",
                    vmin=v_min, vmax=v_max)
        #ax1.plot(param_range_mod['for_cat'],'o',color='gray')
        y.invert_yaxis()
        y.set(ylabel="Normalized range")
        y.set(ylabel="Normalized range",xlabel="Parameters")
        if(i==0): y.set_title(str_title)
        if(i<len(ArrayOfStats)-1): y.axes.xaxis.set_visible(False)
        
        Range_temp=(Output_All_filter_pivot.max()-Output_All_filter_pivot.min()).to_frame()
        Range_temp=Range_temp.rename(columns={Range_temp.columns[0]:Var}).transpose()
        Range_temp['stats']=ArrayOfStats[i]
        Range=pd.concat([Range,Range_temp])
    fig.savefig(Filename_ID_QOut, bbox_inches='tight',dpi=300)
    plt.close()   
    return Range
    
def generate_scatter_rel_comparison_v2(Var,ArrayOfStats,Stats_All,Param_range,str_title,Filename_ID_QOut):       
    import seaborn as sns
    import matplotlib.pyplot as plt
    fig,(ax)= plt.subplots(len(ArrayOfStats),1, figsize = (10,8))
    cmap = sns.color_palette("seismic", as_cmap=True)
    cmap=cmap.reversed()
    cmap.set_bad(color='yellow')
    sns.set(font_scale=0.90)
    for i in range(0,len(ArrayOfStats)):
        Stats_All_filter=Stats_All[(Stats_All['Variable']==Var) & (Stats_All['Objective']==ArrayOfStats[i])][['Param','Ratio_baseline','Value']]
        
        Output_All_filter_pivot=Stats_All_filter.pivot(index='Ratio_baseline',columns='Param')
        Output_All_filter_pivot=Output_All_filter_pivot.Value[Param_range.columns.values].transpose()   
        ax[i].plot(Output_All_filter_pivot,'o')
        #ax1.plot(param_range_mod['for_cat'],'o',color='gray'
        y_label=ArrayOfStats[i]
        
        ax[i].set(ylabel=y_label,xlabel="Parameters")        
        ax[i].set_xticklabels(Param_range.columns.values,rotation=90)
        if(i==0): 
            ax[i].set_title(str_title)
            ax[i].legend(Output_All_filter_pivot.columns,title="param range",ncol=3)
        if(i<len(ArrayOfStats)-1): 
            ax[i].axes.xaxis.set_visible(False)
    fig.savefig(Filename_ID_QOut, bbox_inches='tight',dpi=300)
    plt.close()       

    
def generate_scatter_rel_comparison(Var,stats,Output_All,Param_range,str_title,Filename_ID_QOut):       
    import seaborn as sns
    import matplotlib.pyplot as plt
    fig,(ax)= plt.subplots(len(stats),1, figsize = (10,8))
    cmap = sns.color_palette("seismic", as_cmap=True)
    cmap=cmap.reversed()
    cmap.set_bad(color='yellow')
    sns.set(font_scale=0.90)
    for i in range(0,len(stats)):
        Output_All_filter=Output_All[(Output_All['Variable']==Var) & (Output_All['Stats']==stats[i])][['Param','Ratio_baseline','Rel_Dif']]
        Output_All_filter_pivot=Output_All_filter.pivot(index='Ratio_baseline',columns='Param')
        Output_All_filter_pivot=Output_All_filter_pivot.Rel_Dif[Param_range.columns.values].transpose()   
        ax[i].plot(Output_All_filter_pivot,'o')
        #ax1.plot(param_range_mod['for_cat'],'o',color='gray'
        y_label=Var.replace('land_surface_water__',"")+" - "+stats[i]
        
        ax[i].set(ylabel=y_label,xlabel="Parameters")        
        ax[i].set_xticklabels(Param_range.columns.values,rotation=90)
        if(i==0): 
            ax[i].set_title(str_title)
            ax[i].legend(Output_All_filter_pivot.columns,title="param range",ncol=3)
        if(i<len(stats)-1): 
            ax[i].axes.xaxis.set_visible(False)
    fig.savefig(Filename_ID_QOut, bbox_inches='tight',dpi=300)
    plt.close()   
    
def generate_hydrograph(output,Variables,Variables_names,Spinup,str_title,Filename):       
    import seaborn as sns
    import matplotlib.pyplot as plt
    from datetime import timedelta
    fig,(ax)= plt.subplots(len(Variables),1, figsize = (10,10))
    cmap = sns.color_palette("seismic", as_cmap=True)
    cmap=cmap.reversed()
    cmap.set_bad(color='yellow')
    Spinup_time=output.index.min()+timedelta(days=Spinup)
    Max_Y=0
    Min_Y=10000000
    for i in range(0,len(Variables)):
        if(len(output[Variables[i]][output.index>Spinup_time].dropna())>0) & (not "STORAGE" in Variables[i])  :
            Max_Y=max(1.05*output[Variables[i]][output.index>Spinup_time].max(),1.05*Max_Y)
            Min_Y=min(output[Variables[i]][output.index>Spinup_time].min(),Min_Y)

    for i in range(0,len(Variables)):
        if(len(output[Variables[i]][output.index>Spinup_time].dropna())>0) & ("STORAGE" in Variables[i])  :
            Max_Y_storage=max(1.05*output[Variables[i]][output.index>Spinup_time].max(),1.05*Max_Y)
            Min_Y_storage=min(output[Variables[i]][output.index>Spinup_time].min(),Min_Y)
    for i in range(0,len(Variables)):
        Min=Min_Y
        Max=Max_Y
        if("STORAGE" in Variables[i]):
            Min=Min_Y_storage
            Max=Max_Y_storage           
        ax[i].plot(output[Variables[i]])
        ax[i].plot([Spinup_time,Spinup_time],[Min_Y,Max_Y],'-')
        #ax1.plot(param_range_mod['for_cat'],'o',color='gray'
        y_label=Variables_names[i]        
        ax[i].set(ylabel=y_label,xlabel="time")  
        ax[i].set_ylim([Min,Max])
        if(i==0): 
            ax[i].set_title(str_title)
        if(i<len(Variables)-1): 
            ax[i].axes.xaxis.set_visible(False)
    fig.savefig(Filename, bbox_inches='tight',dpi=300)
    plt.close()  

# def plot_obj_functions(Stats_All,Obj_functions,str_title,Filename_ID_QOut):       
#     import seaborn as sns
#     import matplotlib.pyplot as plt
#     fig,(ax)= plt.subplots(len(Obj_functions),1, figsize = (10,8))
#     cmap = sns.color_palette("seismic", as_cmap=True)
#     cmap=cmap.reversed()
#     cmap.set_bad(color='yellow')
#     sns.set(font_scale=0.90)
#     for i in range(0,len(Obj_functions)):
        
#         df_column_all_stats=['hru_id','cat_id','Objective','Param','Ratio_baseline','Param_Value','Value']
#         Stats_All_filter=Stats_All[(Output_All['Objective']==Obj_functions[i])][['Param','Ratio_baseline','Value']]
#         Output_All_filter_pivot=Output_All_filter.pivot(index='Ratio_baseline',columns='Param')
#         Output_All_filter_pivot=Output_All_filter_pivot.Value[Param_range.columns.values].transpose()   
#         ax[i].plot(Output_All_filter_pivot,'o')
#         #ax1.plot(param_range_mod['for_cat'],'o',color='gray'
#         y_label=Obj_functions[i]
        
#         ax[i].set(ylabel=y_label,xlabel="Parameters")        
#         ax[i].set_xticklabels(Param_range.columns.values,rotation=90)
#         if(i==0): 
#             ax[i].set_title(str_title)
#             ax[i].legend(Output_All_filter_pivot.columns,title="param range",ncol=3)
#         if(i<len(stats)-1): 
#             ax[i].axes.xaxis.set_visible(False)
#     fig.savefig(Filename_ID_QOut, bbox_inches='tight')
#     plt.close()    

def Between_site_range(Range_param,Variables,Variables_names,stats,title,Btw_site_comparison):
    import seaborn as sns
    import matplotlib.pyplot as plt
    cmap = sns.color_palette("YlOrRd", as_cmap=True)        
    cmap.set_bad(color='black')
    sns.set(font_scale=0.8)
    for ii in range(0,len(Variables)):       
       print(Variables[ii]) 
       for ij in range(0,len(stats)): 
           print(stats[ij]) 
           Range_param_m=Range_param[(Range_param['stats']==stats[ij]) & (Range_param.index==Variables[ii])]
           Range_param_m=Range_param_m.set_index('Descrip')
           Range_param_m_crop=Range_param_m.drop(columns=['stats', 'hru_id', 'huc_02','Model'])
           heigh=len(Range_param_m_crop)*0.4
           fig,(ax)= plt.subplots(1,1, figsize = (5,heigh))
           if(stats[ij]=="normalized_nash_sutcliffe"): 
               v_min=0; v_max=1 
               cmaptickes=[0,0.2,0.4,0.6,0.8,1.0]
               cmap = sns.color_palette("YlOrRd", as_cmap=True)
               #cmap=cmap.reversed()
               cmap.set_bad(color='gray')
           elif(stats[ij]=="custom"): 
               v_min=0; v_max=1 
               cmap = sns.color_palette("YlOrRd", as_cmap=True)
               cmap.set_bad(color='gray')
           else: 
               v_min=0; v_max=5
               cmaptickes=range(v_min,v_max)
               cmap = sns.color_palette("YlOrRd", as_cmap=True)
               #cmap=cmap.reversed()
               cmap.set_bad(color='gray')
           ax=sns.heatmap(Range_param_m_crop, cmap = cmap, 
                           cbar_kws = {'pad': 0.015, 'ticks': cmaptickes,
                                       'label': 'Sensitivity range'}, 
                           linewidths = 0.50, linecolor = 'grey', ax = ax,
                           vmin=v_min, vmax=v_max)           
           #y_label=Var.replace('land_surface_water__',"")+" - "+stats[i]
           #ax[i].set(ylabel=y_label,xlabel="Parameters")        
           ax.set_xticklabels(Range_param_m_crop.columns.values,rotation=90)
           str_title=title.split("\n")[0].replace(" ","")+"\n"+Variables_names[ii] + " - " + stats[ij]
           ax.set_title(str_title)
           Filename_ID_QOut=Btw_site_comparison+str_title.replace("\n","").replace(" ","").replace("-","_")+".png"

           fig.savefig(Filename_ID_QOut, bbox_inches='tight',dpi=300)
           
           plt.close()  

def Range_parameter(Range_param,ShowVariables,ArrayOfStats,title,Filename_ID_QOut) :  
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    Range_param['Var']=Range_param.index
    Temp0=Range_param.melt(id_vars=['Var','stats','hru_id', 'huc_02', 'Model', 'Descrip'],
    var_name="Param",
    value_name="Value")
    Temp1=Temp0[Temp0['stats']==ArrayOfStats[0]]
    Temp1=Temp1[Temp1['Var'].isin(ShowVariables)]
    Temp2=Temp0[Temp0['stats']==ArrayOfStats[1]]
    Temp2=Temp2[Temp2['Var'].isin(ShowVariables)]
    Temp3=Temp0[Temp0['stats']==ArrayOfStats[2]]
    Temp3=Temp3[Temp3['Var'].isin(ShowVariables)]
     #Temp=Temp[Temp['Objective'].isin(ArrayOfStats)]
     
     
    num_subplots = 3 #If plotting cumulative precipitation/soil moisture, use 3 subplots (flow, cumulative rain, soil moisture)
    plt.rcParams["figure.figsize"] = (12,8)
    fig, ax_compare = plt.subplots(num_subplots, 1) #Create the plot for this zone
    
    sns.boxplot(x='Param',y="Value",hue='Var',data=Temp1,ax=ax_compare[0])
    ax_compare[0].set_xlabel ('Parameter'); 
    ax_compare[0].set_ylabel('Difference Range \n'+ArrayOfStats[0])
    ax_compare[0].set_ylim([0,1])
    ax_compare[0].set(xticklabels=[])
    ax_compare[0].set(xlabel=None)
    
    sns.boxplot(x='Param',y="Value",hue='Var',data=Temp2,ax=ax_compare[1])
    ax_compare[1].set_xlabel ('Parameter'); 
    ax_compare[1].set_ylabel('Difference Range \n'+ArrayOfStats[1])
    ax_compare[1].set(xticklabels=[])
    ax_compare[1].set_ylim([-1,15])
    ax_compare[1].set(xlabel=None)
    
    sns.boxplot(x='Param',y="Value",hue='Var',data=Temp3,ax=ax_compare[2],)
    ax_compare[2].set_xlabel ('Parameter'); 
    ax_compare[2].set_ylabel('Difference Range \n'+ArrayOfStats[2])
    ax_compare[2].set_ylim([-1,15])
    ax_compare[2].tick_params(axis='x',rotation=90)
    #ax_compare[0].set_title("Daily runoff - Nash = " + str(round(Value,2)))
 
    plt.figtext(0.005,0.65,"(a)",fontsize=13)
    plt.figtext(0.005,0.32,"(b)",fontsize=13)
    plt.figtext(0.005,0.005,"(c)",fontsize=13)
 
    fig.savefig(Filename_ID_QOut, bbox_inches='tight',dpi=300)  
           
def Find_param_position(param_range_mod,Ori_param):   
    param_range_mod['for_cat_abs']=0.00
    param_range_mod['for_cat_rel']=0.00
    for i in range(0,len(param_range_mod)):
        minValue=param_range_mod.iloc[i]['minValue']
        maxValue=param_range_mod.iloc[i]['maxValue']             
        parameter=param_range_mod.index[i]
        if(parameter in 'nash_storage1'):  
            param_range_mod.at['nash_storage1','for_cat_rel']=round((float(Ori_param.loc['nash_storage'][1].split(",")[0])-minValue)/(maxValue-minValue),3)
            param_range_mod.at['nash_storage1','for_cat_abs']=float(Ori_param.loc['nash_storage'][1].split(",")[0])
        elif(parameter in 'nash_storage2'): 
            param_range_mod.at['nash_storage2','for_cat_rel']=round((float(Ori_param.loc['nash_storage'][1].split(",")[1])-minValue)/(maxValue-minValue),3)
            param_range_mod.at['nash_storage2','for_cat_abs']=float(Ori_param.loc['nash_storage'][1].split(",")[1])
        else:
            param_range_mod.at[parameter,'for_cat_rel']=round((float(str(Ori_param.loc[parameter].values[0]).replace("%",""))-minValue)/(maxValue-minValue),3)
            param_range_mod.at[parameter,'for_cat_abs']=float(str(Ori_param.loc[parameter].values[0]).replace("%",""))
            print (parameter)     
            
    param_range_mod=param_range_mod.fillna(0)           
    return param_range_mod

                          
def Table_to_figure(im,param_range_mod,Filename_ID_QOut):
    import df2img
    fig = df2img.plot_dataframe(
        param_range_mod,
        title=dict(
            font_color="darkred",
            font_family="Times New Roman",
            font_size=16,
            text="Parameters used in the Sensitivity analysis - " + im,
        ),
        tbl_header=dict(
            align="right",
            fill_color="blue",
            font_color="white",
            font_size=12,
            line_color="darkslategray",
        ),
        tbl_cells=dict(
            align="right",
            line_color="darkslategray",
        ),
        row_fill_color=("#ffffff", "#d7d8d6"),
        fig_size=(1000, 500),
    )

    df2img.save_dataframe(fig=fig, filename=Filename_ID_QOut)

                
def prepare_data(m_PET,m_runoff,CAMELS_Folder,Working_dir,outfolder,Next_gen,hru_id,basin_id,nexus_id,flag_baseline,param_range_runoff_all,param_range_PET_all,start_time,end_time): 
    import os
    import subprocess
    from glob import glob
    import numpy as np
   
    
    if(os.path.exists(outfolder+"ngen")): 
        str_sub="rm -rf "+outfolder+"ngen"
        out=subprocess.call(str_sub,shell=True)             
    str_sub="ln -s "+Next_gen
    out=subprocess.call(str_sub,shell=True) 
          
    # copy forcing
    #TODO: Crop the forcing based on initial_time and End_time         
    Forcing_In=Working_dir+"/forcing/"+basin_id+".csv"
    if not os.path.exists(Forcing_In): 
        List_forcing=glob(Working_dir+"/forcing/*.csv")
        if(len(List_forcing)==0):
            Forcing_In='/home/west/Projects/CAMELS/PerBasin4/data_CAMELS/02177000/forcing/cat-101.csv'
        else:
            Forcing_In=List_forcing[0]
    outfolder_forcing=outfolder   +"/forcing/"     
    if not os.path.exists(outfolder_forcing): os.mkdir(outfolder_forcing)  
    Forcing_Out=outfolder_forcing+basin_id+".csv"
    str_sub="cp "+Forcing_In+" " +Forcing_Out
    out=subprocess.call(str_sub,shell=True)   
    Real=""
    if(m_runoff=='CFE'):
        if(m_PET=='NOAH-OWP'): Real="/Realization_noahowp_cfe_calib.json"
        elif(m_PET=='PET'): Real="/Realization_pet_cfe_calib.json"
        else: print("Model option not available " + m_PET )
    elif(m_runoff=='Topmodel'):
       if(m_PET=='NOAH-OWP'): Real="/Realization_noahowp_topmodel_calib.json"
       elif(m_PET=='PET'): Real="/Realization_pet_topmodel_calib.json"
       else: print("Model option not available " + m_PET ) 
    elif(m_runoff=='CFE_X'):
        if(m_PET=='NOAH-OWP'): Real="/Realization_noahowp_cfe_X_calib.json"
        elif(m_PET=='PET'): Real="/Realization_pet_cfe_X_calib.json"
        else: print("Model option not available " + m_PET )
    else: print("Model option not available " +m_runoff) 
    Realiz_in=CAMELS_Folder+Real
    Realiz_out=outfolder+Real.replace("calib.","SA.")
    str_sub="cp "+Realiz_in+" " +Realiz_out
    out=subprocess.call(str_sub,shell=True)     
    
    if(m_runoff=='CFE'):
        # Copy CFE config and realization file and modify accordingly
         
        # copy CFE config file
        CFE_Config_In=Working_dir+"/CFE/"+basin_id+"_bmi_config_cfe_pass.txt"
        Runoff_Config_Out=outfolder+basin_id+"_bmi_config_cfe_pass.txt"
        str_sub="cp "+CFE_Config_In+" " +Runoff_Config_Out
        out=subprocess.call(str_sub,shell=True)  
        Ori_param_runoff=pd.read_csv(Runoff_Config_Out,delimiter="=",index_col=0,header=None)        
        Temp=pd.DataFrame(["2[]"],columns=[Ori_param_runoff.columns[0]],index=["N_nash"])
        Ori_param_runoff=pd.concat([Ori_param_runoff,Temp])
        Ori_param_runoff=Ori_param_runoff[1].str.replace('\[.*$','')
        Ori_param_runoff.replace(' ','',regex=True,inplace=True)
        # Need to modify file since we added N_nash
        Ori_param_runoff.to_csv(Runoff_Config_Out,sep="=",header=False)
        Runoff_Config_Ori=CFE_Config_In.replace(".txt","Ori.txt")
        str_sub="cp "+Runoff_Config_Out+" " +Runoff_Config_Ori
        out=subprocess.call(str_sub,shell=True)
        #Ori_param.at['max_gw_storage']=0.11
        #Ori_param.to_csv(Runoff_Config_Out,sep="=")
        # copy Ngen realization file        

        with open(Realiz_in) as f: realiz_ori=f.read()
        
        realiz_ori=realiz_ori.replace("2007-10-01 00:00:00",start_time)
        realiz_ori=realiz_ori.replace("2013-10-01 00:00:00",end_time)
        realiz_ori=realiz_ori.replace("./CFE/{{id}}_bmi_config_cfe_pass.txt","./{{id}}_bmi_config_cfe_pass.txt")
        #realiz_ori=realiz_ori.replace("./forcing/","./")
        
        with open(Realiz_out, "w") as f: f.write(realiz_ori)    
    elif(m_runoff=='CFE_X'):
        # Copy CFE config and realization file and modify accordingly
         
        # copy CFE config file
        CFE_Config_In=Working_dir+"/CFE_X/"+basin_id+"_bmi_config_cfe_pass.txt"
        Runoff_Config_Out=outfolder+basin_id+"_bmi_config_cfe_pass_X.txt"
        str_sub="cp "+CFE_Config_In+" " +Runoff_Config_Out
        out=subprocess.call(str_sub,shell=True)  
        Ori_param_runoff=pd.read_csv(Runoff_Config_Out,delimiter="=",index_col=0,header=None)
        Temp=pd.DataFrame(["2[]"],columns=[Ori_param_runoff.columns[0]],index=["N_nash"])
        Ori_param_runoff=pd.concat([Ori_param_runoff,Temp])
        Ori_param_runoff=Ori_param_runoff[1].str.replace('\[.*$','')
        Ori_param_runoff.replace(' ','',regex=True,inplace=True)
        # Need to modify file since we added N_nash
        Ori_param_runoff.to_csv(Runoff_Config_Out,sep="=",header=False)
        Runoff_Config_Ori=CFE_Config_In.replace(".txt","Ori.txt")
        str_sub="cp "+Runoff_Config_Out+" " +Runoff_Config_Ori
        out=subprocess.call(str_sub,shell=True)
        #Ori_param.at['max_gw_storage']=0.11
        #Ori_param.to_csv(Runoff_Config_Out,sep="=")
        # copy Ngen realization file        

        with open(Realiz_in) as f: realiz_ori=f.read()
        
        realiz_ori=realiz_ori.replace("2007-10-01 00:00:00",start_time)
        realiz_ori=realiz_ori.replace("2013-10-01 00:00:00",end_time)
        realiz_ori=realiz_ori.replace("./CFE_X/{{id}}_bmi_config_cfe_pass.txt","./{{id}}_bmi_config_cfe_pass_X.txt")
        #realiz_ori=realiz_ori.replace("./forcing/","./")
        
        with open(Realiz_out, "w") as f: f.write(realiz_ori)   
    elif(m_runoff=='Topmodel'):
        # copy Topmodel config file
        Topmodel_in_Files=Working_dir+"/Topmodel/*"+basin_id+".*"
        Runoff_Config_Out=outfolder      
        str_sub="cp "+Topmodel_in_Files+" " +Runoff_Config_Out
        out=subprocess.call(str_sub,shell=True)  
        Runoff_Config_Out=Runoff_Config_Out+"params_"+basin_id+".dat"
        Runoff_Config_Ori=Runoff_Config_Out.replace(".dat","Ori.dat")
        str_sub="cp "+Runoff_Config_Out+" " +Runoff_Config_Ori
        out=subprocess.call(str_sub,shell=True)        
        # modify *.run file
        str_sub="sed -i 's/Topmodel//g' " +outfolder+"topmod_" +basin_id+".run"        
        out=subprocess.call(str_sub,shell=True)  
        str_sub="sed -i 's/forcing//g' " +outfolder+"topmod_" +basin_id+".run"        
        out=subprocess.call(str_sub,shell=True)          
        
        Ori_param_runoff=pd.read_csv(Runoff_Config_Out,delimiter=r"\s+",header=None,skiprows=1)
        for i in range(0,len(param_range_runoff_all)):
            Ori_param_runoff=Ori_param_runoff.rename(columns={Ori_param_runoff.columns[i]:param_range_runoff_all.index[i]})
        Ori_param_runoff=Ori_param_runoff.transpose()        
        Ori_param_runoff=Ori_param_runoff[0]
        #Modify NextGen realization file
        with open(Realiz_in) as f: realiz_ori=f.read()
        
        realiz_ori=realiz_ori.replace("2007-10-01 00:00:00",start_time)
        realiz_ori=realiz_ori.replace("2013-10-01 00:00:00",end_time)
        realiz_ori=realiz_ori.replace("./Topmodel/topmod_{{id}}.run","./topmod_{{id}}.run")
        #realiz_ori=realiz_ori.replace("./forcing/","./")
        
        with open(Realiz_out, "w") as f: f.write(realiz_ori) 
    
    else:
        print ("This model is not supported : " +m_runoff)
        exit(0)

    if(m_PET=='NOAH-OWP'):
        # Copy NOAH-OWP config and realization file and modify accordingly
         
        # copy NOAH-OWP config file
        PET_Config_In=Working_dir+"/NOAH/"+basin_id+".input"
        PET_Config_Out=outfolder+basin_id+".input"
        str_sub="cp "+PET_Config_In+" " +PET_Config_Out
        out=subprocess.call(str_sub,shell=True)  
        

        with open(PET_Config_Out) as f: confi_ori=f.read()        
        confi_ori=confi_ori.replace("./NOAH/parameters/","./parameters/")        
        with open(PET_Config_Out, "w") as f: f.write(confi_ori)    
        
        # copy parameters table
        NOAH_OWP_param_In=Working_dir+"/NOAH/parameters"
        NOAH_OWP_param_Out=outfolder+"/parameters"        
        str_sub="cp -rf "+NOAH_OWP_param_In+" " +NOAH_OWP_param_Out
        out=subprocess.call(str_sub,shell=True) 
        
        PET_Config_Out=NOAH_OWP_param_Out+"/MPTABLE.TBL"
        PET_Config_Ori=PET_Config_Out.replace(".TBL","Ori.TBL")
        str_sub="cp "+PET_Config_Out+" " +PET_Config_Ori
        out=subprocess.call(str_sub,shell=True)   
        #Ori_param=pd.read_csv(Config_Out,delimiter="=",index_col=0,header=None)
        #Ori_param.to_csv(Config_Out,sep="=")
        # copy Ngen realization file        
        
        Ori_param_PET=param_range_PET_all['minValue']
        
        with open(Realiz_out) as f: realiz_ori=f.read()        
        realiz_ori=realiz_ori.replace("./NOAH/{{id}}.input","./{{id}}.input")        
        with open(Realiz_out, "w") as f: f.write(realiz_ori)   

        
    elif(m_PET=='PET'):
        # copy Topmodel config file
        #TODO: implement
        print ("TODO: Need to be implemented : " +m_PET)
    else:
        print ("This model is not supported : " +m_runoff)
        exit(0)
        
    # GETTING VALUES FROM CONFIG FILE   
    param_range_runoff_all['for_cat_abs']=0.0
    param_range_runoff_all['for_cat_rel']=0.0
    print (Ori_param_runoff)
    for i in range(0,len(param_range_runoff_all)):
        minValue=param_range_runoff_all.iloc[i]['minValue']
        maxValue=param_range_runoff_all.iloc[i]['maxValue']             
        parameter=param_range_runoff_all.index[i]
        print(parameter)
        if(parameter in 'nash_storage1'):  
            param_range_runoff_all.at['nash_storage1','for_cat_rel']=round((float(Ori_param_runoff.loc['nash_storage'].split(",")[0])-minValue)/(maxValue-minValue),3)
            param_range_runoff_all.at['nash_storage1','for_cat_abs']=float(Ori_param_runoff.loc['nash_storage'].split(",")[0])
        elif(parameter in 'nash_storage2'): 
            param_range_runoff_all.at['nash_storage2','for_cat_rel']=round((float(Ori_param_runoff.loc['nash_storage'].split(",")[1])-minValue)/(maxValue-minValue),3)
            param_range_runoff_all.at['nash_storage2','for_cat_abs']=float(Ori_param_runoff.loc['nash_storage'].split(",")[1])
        elif(parameter in 'giuh_ordinates'):
            param_range_runoff_all.at[parameter,'for_cat_rel']=-9
            param_range_runoff_all.at[parameter,'for_cat_abs']=-9
        else:
            param_range_runoff_all.at[parameter,'for_cat_rel']=round((float(str(Ori_param_runoff.loc[parameter]).replace("%",""))-minValue)/(maxValue-minValue),3)
            param_range_runoff_all.at[parameter,'for_cat_abs']=np.format_float_positional(float(str(Ori_param_runoff.loc[parameter]).replace("%","")))
           
    param_range_runoff_all=param_range_runoff_all.fillna(0)

    # FOR NOW, USING MINIMUM VALUE FOR ALL SITES FOR PET DUE TO THE USE OF TABLES 
    param_range_PET_all['for_cat_abs']=0.0
    param_range_PET_all['for_cat_rel']=0.0
    for i in range(0,len(param_range_PET_all)):
        minValue=param_range_PET_all.iloc[i]['minValue']
        maxValue=param_range_PET_all.iloc[i]['maxValue']             
        parameter=param_range_PET_all.index[i]
        param_range_PET_all.at[parameter,'for_cat_abs']=np.format_float_positional(float(str(minValue)))
        param_range_PET_all.at[parameter,'for_cat_rel']=round(0.01)
            
    param_range_PET_all=param_range_PET_all.fillna(0)    
    Run_nextgen="./ngen/cmake_build/ngen "+ Working_dir+"/spatial/catchment_data.geojson "+basin_id+ " " +Working_dir+"/spatial/nexus_data.geojson "+nexus_id+" "+Realiz_out    
    return Run_nextgen,param_range_runoff_all,param_range_PET_all,[Runoff_Config_Ori,Runoff_Config_Out],[PET_Config_Ori,PET_Config_Out]
                    
def calculate_stats(hru_id,basin_id,parameter,Increment,Modified_Parameter,Variables,output_baseline,output,df_column_all_stats):
    import sys
    sys.path.append("/home/west/git_repositories/ngen-cal-master/ngen-cal/python/ngen_cal/")
    import objectives as OB
    Stats_Site=pd.DataFrame(columns=df_column_all_stats) 
    for iv in range(0,len(Variables)):
        Var=Variables[iv]
        Out=output[Var].copy()
        Out_baseline=output_baseline[Var].copy()    
        
        Value=OB.nash_sutcliffe(Out, Out_baseline)
        Stats_Site_temp=pd.DataFrame([(hru_id,basin_id,Var,'nash_sutcliffe',parameter,Increment,Modified_Parameter,Value)],columns=df_column_all_stats)
        Stats_Site=pd.concat([Stats_Site,Stats_Site_temp]) 
        
        Value=OB.custom(Out, Out_baseline)
        Stats_Site_temp=pd.DataFrame([(hru_id,basin_id,Var,'custom',parameter,Increment,Modified_Parameter,Value)],columns=df_column_all_stats)
        Stats_Site=pd.concat([Stats_Site,Stats_Site_temp])                             
        
        Value=OB.normalized_nash_sutcliffe(Out, Out_baseline)
        Stats_Site_temp=pd.DataFrame([(hru_id,basin_id,Var,'normalized_nash_sutcliffe',parameter,Increment,Modified_Parameter,Value)],columns=df_column_all_stats)
        Stats_Site=pd.concat([Stats_Site,Stats_Site_temp])                             
        
        Value=OB.peak_error_single(Out, Out_baseline)
        Stats_Site_temp=pd.DataFrame([(hru_id,basin_id,Var,'peak_error_single',parameter,Increment,Modified_Parameter,Value)],columns=df_column_all_stats)
        Stats_Site=pd.concat([Stats_Site,Stats_Site_temp])  
        
        Value=OB.volume_error(Out, Out_baseline)
        Stats_Site_temp=pd.DataFrame([(hru_id,basin_id,Var,'volume_error',parameter,Increment,Modified_Parameter,Value)],columns=df_column_all_stats)
        Stats_Site=pd.concat([Stats_Site,Stats_Site_temp])  
        
        if(iv>0):
            Value=output[Variables[iv]].sum()/output[Variables[iv]].sum()
            ratio_str="ratio_"+str(iv)
            Stats_Site_temp=pd.DataFrame([(hru_id,basin_id,Var,ratio_str,parameter,Increment,Modified_Parameter,Value)],columns=df_column_all_stats)
            Stats_Site=pd.concat([Stats_Site,Stats_Site_temp]) 
         # TODO: Create function - Generate plots and add to powerpoint(?)
    
    Stats_Site=Stats_Site.set_index("hru_id")
    
    return Stats_Site