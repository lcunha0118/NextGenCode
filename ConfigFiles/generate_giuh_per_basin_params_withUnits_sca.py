"""
Zonal Statistics
Vector-Raster Analysis
Modified by Luciana Cunha from 2013 Matthew Perry and AsgerPetersen:

usage: generate_twi_per_basin.py [-h] [--output flag [--buffer distance] [--nodata value] 
                      catchments twi_raster slope_raster outputfolder_twi
positional arguments:
  namestr                HUC Number
  catchments            hydrofabrics catchment
  time_to_stream_raster Time to stream in minutes - generated with workflow_hand_twi_giuh.sh
  NWM_param_file      CSV file with soil parameters from NWM 2.1 - part of the hydrofabric released in 08/2021
  outputfolder_giuh     Output folder

optional arguments:
  -h, --help            show this help message and exit
  --Xinanjiang_flag     Needs to be defined as 1 to generate files for xinanjiang
  --Xinanjiang_param    Parameter file with Xinanjiang parameters
  --output flag         0-Only generates the param file, 1- generates the cfe config file
  --buffer distance     Buffer geometry by this distance before calculation
  --nodata value        Use this nodata value instead of value from raster
  --preload             Preload entire raster into memory instead of a read
  --output_flag         Output the config file for CFE 
  --preload             Preload entire raster into memory instead of a read
  --flag_discretization If 0 run for all catchments, if 1 run for lumped catchments
"""


from osgeo import gdal, ogr
from osgeo.gdalconst import *
import numpy as np
import sys
import argparse
import pandas as pd
import os
#import json
gdal.PushErrorHandler('CPLQuietErrorHandler')
ogr.UseExceptions()

def bbox_to_pixel_offsets(gt, bbox):
    originX = gt[0]
    originY = gt[3]
    pixel_width = gt[1]
    pixel_height = gt[5]
    x1 = int((bbox[0] - originX) / pixel_width)
    x2 = int((bbox[1] - originX) / pixel_width) 
    #x2 = int((bbox[1] - originX) / pixel_width) + 1
    y1 = int((bbox[3] - originY) / pixel_height)
    y2 = int((bbox[2] - originY) / pixel_height) 
    #y2 = int((bbox[2] - originY) / pixel_height) + 1
     
    xsize = x2 - x1
    ysize = y2 - y1
    return (x1, y1, xsize, ysize)



def generate_giuh_per_basin_withUnits(namestr,catchments, time_to_stream_raster, NWM_param_file, outputfolder_giuh,
                    Xinanjiang_flag=0,  
                    Xinanjiang_param="0",  
                    output_flag=1,
                    nodata_value=None,
                    global_src_extent=False,
                    buffer_distance=0.001,
                    flag_discretization=0):
    
    if not os.path.exists(catchments):  print ("does not exist "  + catchments)
    if not os.path.exists(time_to_stream_raster):  print ("does not exist "  + time_to_stream_raster)
    if not os.path.exists(NWM_param_file):  print ("does not exist "  + NWM_param_file)


    
    # outputfolder_giuh_param_file=outputfolder_giuh+"/CFE_GIUH/"    
    # if not os.path.exists(outputfolder_giuh_param_file): os.mkdir(outputfolder_giuh_param_file)
    # outputfolder_giuh_param_file=outputfolder_giuh_param_file+"/"+namestr+"/"
    # if not os.path.exists(outputfolder_giuh_param_file): os.mkdir(outputfolder_giuh_param_file)
    

    if(output_flag==1): 
        #outputfolder_giuh_config_file=outputfolder_giuh
        if(Xinanjiang_flag==1):
            outputfolder_giuh_config_file=outputfolder_giuh+"/CFE_X/"
        else:
            outputfolder_giuh_config_file=outputfolder_giuh+"/CFE/"
        if not os.path.exists(outputfolder_giuh_config_file): os.mkdir(outputfolder_giuh_config_file)
        # outputfolder_giuh_config_file=outputfolder_giuh_config_file+"/"+namestr+"/"
        # if not os.path.exists(outputfolder_giuh_config_file): os.mkdir(outputfolder_giuh_config_file)


    rds = gdal.Open(time_to_stream_raster, GA_ReadOnly)
    assert rds, "Could not open raster" +time_to_stream_raster
    rb = rds.GetRasterBand(1)
    rgt = rds.GetGeoTransform()
    
    if nodata_value:
        # Override with user specified nodata
        nodata_value = float(nodata_value)
        rb.SetNoDataValue(nodata_value)
    else:
        # Use nodata from band
        nodata_value = float(rb.GetNoDataValue())
    # Warn if nodata is NaN as this will not work with the mask (as NaN != NaN)
    assert nodata_value == nodata_value, "Cannot handle NaN nodata value"

    if buffer_distance:
        buffer_distance = float(buffer_distance)

    print("catchments " + catchments)
    vds = ogr.Open(catchments, GA_ReadOnly)  
    assert(vds)
    print(vds)
    vlyr =   vds.GetLayer(0)
    print(vlyr)
#    vdefn = vlyr.GetLayerDefn()

    # Calculate (potentially buffered) vector layer extent
    vlyr_extent = vlyr.GetExtent()
    if buffer_distance:
        expand_by = [-buffer_distance, buffer_distance, -buffer_distance, buffer_distance]
        vlyr_extent = [a + b for a, b in zip(vlyr_extent, expand_by)]

    src_array = rb.ReadAsArray()
    # create an in-memory numpy array of the source raster data
    # covering the whole extent of the vector layer
    if global_src_extent:
        # use global source extent
        # useful only when disk IO or raster scanning inefficiencies are your limiting factor
        # advantage: reads raster data in one pass
        # disadvantage: large vector extents may have big memory requirements
        src_offset = bbox_to_pixel_offsets(rgt, vlyr_extent)
        #print (str(src_offset))
        src_array = rb.ReadAsArray(*src_offset)
        
        # calculate new geotransform of the layer subset
        new_gt = (
            (rgt[0] + (src_offset[0] * rgt[1])),
            rgt[1],
            0.0,
            (rgt[3] + (src_offset[1] * rgt[5])),
            0.0,
            rgt[5]
        )

    mem_drv = ogr.GetDriverByName('Memory')
    driver = gdal.GetDriverByName('MEM')
 
        # if(output_flag==1):

        
    if(output_flag==1) & (os.path.isfile(NWM_param_file)): 
        soil_params=pd.read_csv(NWM_param_file,index_col=0)
        soil_params = soil_params[~soil_params.index.duplicated(keep='first')]
        #if(not "cat-" in str(soil_params.index[0])): soil_params.index = 'cat-' + soil_params.index.astype(str)
    

        # Remove Nan for the parameters that are used to generate config file
        # Replace with values from the original CFE config file
        #print ("Getting values from table ")
        soil_params['bexp_soil_layers_stag=1_Time=1']= soil_params['bexp_soil_layers_stag=1'].fillna(16)                    
        soil_params['dksat_soil_layers_stag=1_Time=1']= soil_params['dksat_soil_layers_stag=1'].fillna(0.00000338)
        soil_params['psisat_soil_layers_stag=1_Time=1']= soil_params['psisat_soil_layers_stag=1'].fillna(0.355)  
        soil_params['slope_Time=1']= soil_params['slope'].replace(np.nan,1.0)
        soil_params['smcmax_soil_layers_stag=1_Time=1']= soil_params['smcmax_soil_layers_stag=1'].fillna(0.439)
        soil_params['smcwlt_soil_layers_stag=1_Time=1']= soil_params['smcwlt_soil_layers_stag=1'].fillna(0.066)
        soil_params['ISLTYP']= soil_params['ISLTYP'].fillna(1)
        #soil_params['fd_LKSATFAC']= soil_params['fd_LKSATFAC'].fillna(1000)
        if('refkdt' in soil_params): soil_params['refkdt_Time=1']= soil_params['refkdt'].fillna(3.0)
        else: soil_params['refkdt_time=1']=3.0
        
        soil_params['Zmax'] = soil_params['gw_Zmax'].fillna(16.0)/1000.
        soil_params['Coeff'] = soil_params['gw_Coeff'].fillna(0.5)*3600*pow(10,-6)
        soil_params['Expon'] = soil_params['gw_Expon'].fillna(6.0)
        #soil_params['mult'] = soil_params['fd_LKSATFAC'].fillna(6.0)
    else:
        
        skippednulgeoms = False
        total = vlyr.GetFeatureCount(force = 0)
        print("Total " + total)
        vlyr.ResetReading()
        count = 0
        feat = vlyr.GetNextFeature()
        IDAr=[]
        while feat is not None:
            cat = feat.GetField('ID')
            IDAr.append(cat)
            feat = vlyr.GetNextFeature()        
        soil_params=pd.DataFrame(index=IDAr)
        GW_params=pd.DataFrame(index=IDAr)
        soil_params['bexp_soil_layers_stag=1_Time=1']= 16.0                    
        soil_params['dksat_soil_layers_stag=1_Time=1']= 0.00000338
        soil_params['psisat_soil_layers_stag=1_Time=1']= 0.355
        #soil_params['fd_LKSATFAC']= 1000
        soil_params['slope_Time=1']= 1.0
        soil_params['smcmax_soil_layers_stag=1_Time=1']= 0.439
        soil_params['smcwlt_soil_layers_stag=1_Time=1']= 0.066
        soil_params['refkdt_Time=1']=3.0
        soil_params['Zmax']= 0.01
        soil_params['Coeff'] = 1.8e-05
        soil_params['Expon'] = 6.0
        soil_params['ISLTYP'] = 1
        
    if(Xinanjiang_flag == 1): 
        print ("Xinanjiang_flag = "+str(Xinanjiang_flag))
        Xin_param=pd.read_csv(Xinanjiang_param,index_col=0)
        soil_params['AXAJ']=Xin_param.loc[soil_params['ISLTYP'].values]['AXAJ'].values
        soil_params['BXAJ']=Xin_param.loc[soil_params['ISLTYP'].values]['BXAJ'].values
        soil_params['XXAJ']=Xin_param.loc[soil_params['ISLTYP'].values]['XXAJ'].values
    # soil_params_depth=2.0;soil_params_b_st=4.05;soil_params_mult_st=1000.0;soil_params_satdk_st=0.00000338; soil_params_satpsi_st=0.355    
    # soil_params_slop_st=1.0; soil_params_smcmax_st=0.439; soil_params_wltsmc_st=0.066;
    # max_gw_storage_st=16.0; Cgw_st=0.01; expon_st=6.0;
    # gw_storage_st=50;alpha_fc_st=0.33; soil_storage_st=66.7
    # K_nash_st=0.03;K_lf_st=0.01
    # nash_storage_st='0.0,0.0'; giuh_ordinates_st='0.06,0.51,0.28,0.12,0.03'

    #CREATE GIUH for the whole catchment
    if(flag_discretization==1):
        maskedArray=np.ma.filled(src_array.astype(float), np.nan).flatten()
        maskedArray2=maskedArray[(maskedArray!=nodata_value) & (~np.isnan(maskedArray)) & (maskedArray>=0)] # Values covered by the polygon
        sorted_array = np.sort(maskedArray2)        
        sorted_array=(sorted_array-min(sorted_array))/60.    
        AllData = pd.DataFrame(columns=['TravelTimeHour'], data=sorted_array)                
        max_Nclasses=min(24*5,max(AllData['TravelTimeHour']))
        max_Nclasses=max(3,max_Nclasses)
        classes=np.arange(0,max_Nclasses, 1)    
        hist=np.histogram(AllData['TravelTimeHour'].values, bins=classes)
        
        CDF=pd.DataFrame({'Nelem':hist[0].T, 'TravelTimeHour':hist[1][1:].T}).sort_values(by=['TravelTimeHour'], ascending=True)
        CDF['Freq']=np.round(CDF['Nelem']/sum(CDF['Nelem']),2)
        dif=1.0-CDF['Freq'].sum()
        CDF.at[CDF['Freq'].idxmax(),'Freq']=CDF['Freq'].iloc[CDF['Freq'].idxmax()]+dif     
        if((CDF['Freq'].sum()>1.002) | (CDF['Freq'].sum()<0.998)):
            print ("ERROR IN CDF - ALL " + str(CDF['Freq'].sum()))
        CDF['AccumFreq']=CDF['Freq'].cumsum()             
        DatFile=os.path.join(outputfolder_giuh_config_file,namestr+"_bmi_config_cfe_pass.txt")
        f= open(DatFile, "w")
        
        f.write("%s" %("forcing_file=BMI\n"))
        f.write("%s" %("surface_partitioning_scheme=Schaake\n"))
        f.write("%s" %("soil_params.depth=2.0[m]\n"))
        if(soil_params['bexp_soil_layers_stag=1_Time=1'].mean()==1.0):
            f.write("%s" %("soil_params.b=1.1[]\n"))
        else:    
            f.write("%s" %("soil_params.b="+str(soil_params['bexp_soil_layers_stag=1_Time=1'].mean())+"[]\n"))
        f.write("%s" %("soil_params.satdk="+str(soil_params['dksat_soil_layers_stag=1_Time=1'].mean())+"[m s-1]\n"))
        f.write("%s" %("soil_params.satpsi="+str(soil_params['psisat_soil_layers_stag=1_Time=1'].mean())+"[m]\n"))
        f.write("%s" %("soil_params.slop="+str(soil_params['slope_Time=1'].mean())+"[m/m]\n"))
        f.write("%s" %("soil_params.smcmax="+str(soil_params['smcmax_soil_layers_stag=1_Time=1'].mean())+"[m/m]\n"))
        f.write("%s" %("soil_params.wltsmc="+str(soil_params['smcwlt_soil_layers_stag=1_Time=1'].mean())+"[m/m]\n"))
        f.write("%s" %("soil_params.expon=1.0[]\n"))
        f.write("%s" %("soil_params.expon_secondary=1.0[]\n"))
        f.write("%s" %("refkdt="+str(soil_params['refkdt_Time=1'].mean())+"\n"))
        f.write("%s" %("max_gw_storage="+str(soil_params['Zmax'].mean())+"[m]\n"))                   
        f.write("%s" %("Cgw="+str(soil_params['Coeff'].mean())+"[m h-1]\n"))
        f.write("%s" %("expon="+str(soil_params['Expon'].mean())+"[]\n"))
        f.write("%s" %("gw_storage=0.05[m/m]\n"))
        f.write("%s" %("alpha_fc=0.33\n"))
        f.write("%s" %("soil_storage=0.05[m/m]\n"))
        f.write("%s" %("K_nash=0.03[]\n"))
        f.write("%s" %("K_lf=0.01[]\n"))
        f.write("%s" %("nash_storage=0.0,0.0\n"))
        f.write("%s" %("num_timesteps=1\n"))
        if(Xinanjiang_flag == 1): 
            f.write("%s" %("surface_partitioning_scheme=Xinanjiang\n"))
            f.write("%s" %("a_Xinanjiang_inflection_point_parameter="+str(soil_params['AXAJ'].mean())+"\n"))
            f.write("%s" %("b_Xinanjiang_shape_parameter="+str(soil_params['BXAJ'].mean())+"\n"))
            f.write("%s" %("x_Xinanjiang_shape_parameter="+str(soil_params['XXAJ'].mean())  +"\n"))                     
        f.write("%s" %("verbosity=1\n"))
        f.write("%s" %("DEBUG=0\n"))
        TotalFreq=round(CDF['Freq'].iloc[0],2)
        giuh="giuh_ordinates="+"{0:.2f}".format((round(CDF['Freq'].iloc[0],2)))
        for icdf in range(1,len(CDF)):
            giuh=giuh+","+"{0:.2f}".format((round(CDF['Freq'].iloc[icdf],2)))
            TotalFreq=TotalFreq+round(CDF['Freq'].iloc[icdf],2)
        giuh =giuh+"\n"  
        f.write("%s" %(giuh))
        f.close()    
    else:
            
        # if(output_flag==1):
        
        skippednulgeoms = False
        total = vlyr.GetFeatureCount(force = 0)
        
        print ("total "+ str(total))
        vlyr.ResetReading()
        count = 0
        feat = vlyr.GetNextFeature()
        no_coverage=0
        while feat is not None:
            cat = feat.GetField('ID')
            catstr=str(cat)
            if("e" in catstr):
                print (catstr)
                nc=int(float(catstr.split("-")[1]))
                catstr="cat-"+nc
                
            if("--" in catstr):
                catstr=catstr.replace("--","")                
                print (" -- issue " + catstr)
            #if(isinstance(cat, float)): catstr=str(int(cat))
            #if(not "cat" in catstr): catstr="cat-"+catstr
    
            count = count + 1
            if count % 100 == 0:
                sys.stdout.write("\r{0} of {1}".format(count, total))
                sys.stdout.flush()
            if feat.GetGeometryRef() is None:
                # Null geometry. Write to dst and continue
                if not skippednulgeoms:
                    print ("\nWarning: Skipping nullgeoms\n")
                    skippednulgeoms = True
                feat = vlyr.GetNextFeature()
                continue
            mem_feat = feat.Clone()
            mem_type = mem_feat.GetGeometryRef().GetGeometryType()
            if buffer_distance:
                mem_type = ogr.wkbPolygon
                mem_feat.SetGeometryDirectly( mem_feat.GetGeometryRef().Buffer(buffer_distance) )
    
            if not global_src_extent:
                # use local source extent
                # fastest option when you have fast disks and well indexed raster (ie tiled Geotiff)
                # advantage: each feature uses the smallest raster chunk
                # disadvantage: lots of reads on the source raster
                src_offset = bbox_to_pixel_offsets(rgt, mem_feat.geometry().GetEnvelope())
                #print (str(src_offset))
                src_array = rb.ReadAsArray(*src_offset)
                
                # calculate new geotransform of the feature subset
                new_gt = (
                    (rgt[0] + (src_offset[0] * rgt[1])),
                    rgt[1],
                    0.0,
                    (rgt[3] + (src_offset[1] * rgt[5])),
                    0.0,
                    rgt[5]
                )

            if not src_array is None:
                #print ("src_array")   
                #print (src_array)
                # Create a temporary vector layer in memory
                mem_ds = mem_drv.CreateDataSource('out')
                mem_layer = mem_ds.CreateLayer('mem_lyr', None, mem_type)
                mem_layer.CreateFeature(mem_feat)
        
                # Rasterize it
                rvds = driver.Create('', src_offset[2], src_offset[3], 1, gdal.GDT_Byte)
                rvds.SetGeoTransform(new_gt)
                gdal.RasterizeLayer(rvds, [1], mem_layer, burn_values=[1])
                rv_array = rvds.ReadAsArray()
    
                # Mask basin area
                masked_basin = np.ma.MaskedArray(
                    src_array,
                    mask=np.logical_not(rv_array) 
                    )
                all_values_in_basin=((masked_basin.mask==False)).sum() # False where the basin is, not sure why. So counting pixels in the basin
                    
                # Also remove missing data - keep only valid values
                masked = np.ma.MaskedArray(
                    src_array,
                    mask=np.logical_or(
                        src_array == nodata_value,
                        np.logical_not(rv_array) # remove this since it was creating issues with 1
                    )
                )
                all_valid_values_in_basin=((masked.mask==False)).sum()
                Check=100*all_valid_values_in_basin/all_values_in_basin # Porcentage of valid numbers in the polygone
    
                if(Check>50):   
                    
           
                    #Create a 1-d array - include nan for points outside of the polygone
                    maskedArray=np.ma.filled(masked.astype(float), np.nan).flatten()
                    
                    #remove all values outside of the polygone which are marked as nan
                    maskedArray2=maskedArray[(maskedArray!=nodata_value) & (~np.isnan(maskedArray)) & (maskedArray>=0)] # Values covered by the polygon
                    # Due to incompatibilities with hydrofabrics
                    
                    sorted_array = np.sort(maskedArray2)    
                      
                    if(len(np.unique(sorted_array))>5): 
                        Per5=np.percentile(sorted_array,10)
                        Per95=np.percentile(sorted_array,95)
                        sorted_array=sorted_array[(sorted_array>=Per5) & (sorted_array<=Per95)]
                        sorted_array=(sorted_array-min(sorted_array))
                    else:
                        sorted_array=np.zeros(20)+3600.
                    Per5=np.percentile(sorted_array,5)
                    Per95=np.percentile(sorted_array,95)
                    if(len(np.unique(sorted_array))>10): sorted_array=sorted_array[(sorted_array>=Per5) & (sorted_array<=Per95)]
                    sorted_array=(sorted_array-min(sorted_array))/60.
                    
                    AllData = pd.DataFrame(columns=['TravelTimeHour'], data=sorted_array)                
                    max_Nclasses=min(15,max(AllData['TravelTimeHour']))
                    max_Nclasses=max(3,max_Nclasses)
                    classes=np.arange(0,max_Nclasses, 1)
                    
                    hist=np.histogram(AllData['TravelTimeHour'].values, bins=classes)
                    
                    CDF=pd.DataFrame({'Nelem':hist[0].T, 'TravelTimeHour':hist[1][1:].T}).sort_values(by=['TravelTimeHour'], ascending=True)
                    
                    CDF['Freq']=np.round(CDF['Nelem']/sum(CDF['Nelem']),2)
                    dif=1.0-CDF['Freq'].sum()
                    CDF.at[CDF['Freq'].idxmax(),'Freq']=CDF['Freq'].iloc[CDF['Freq'].idxmax()]+dif        
                    if((CDF['Freq'].sum()>1.002) | (CDF['Freq'].sum()<0.998)):
                        print ("ERROR IN CDF - " + catstr+ " " +str(CDF['Freq'].sum()))
                    #DatFile=os.path.join(outputfolder_giuh_param_file,"cat-"+str(cat)+"_giuh.csv")
                    #DatFile=DatFile.replace("cat-cat-","cat-")
                    #CDF.to_csv(DatFile)       
                else:
                    no_coverage=no_coverage+1
                    CDF=pd.DataFrame({'Nelem':[100,250,300,250,100], 'TravelTimeHour':[1.0,2.0,3.0,4.0,5.0]}).sort_values(by=['TravelTimeHour'], ascending=True)
                    CDF['Freq']=np.round(CDF['Nelem']/sum(CDF['Nelem']),2)
                if(output_flag==1):
                    
                    DatFile=os.path.join(outputfolder_giuh_config_file,catstr+"_bmi_config_cfe_pass.txt")
                    f= open(DatFile, "w")
                    
                    f.write("%s" %("forcing_file=BMI\n"))
                    f.write("%s" %("surface_partitioning_scheme=Schaake\n"))
                    f.write("%s" %("soil_params.depth=2.0[m]\n"))
                    if(soil_params.loc[cat]['bexp_soil_layers_stag=1_Time=1']==1.0):
                        f.write("%s" %("soil_params.b=1.1[]\n"))
                    else:    
                        f.write("%s" %("soil_params.b="+str(soil_params.loc[cat]['bexp_soil_layers_stag=1_Time=1'])+"[]\n"))
                    f.write("%s" %("soil_params.satdk="+str(soil_params.loc[cat]['dksat_soil_layers_stag=1_Time=1'])+"[m s-1]\n"))
                    f.write("%s" %("soil_params.satpsi="+str(soil_params.loc[cat]['psisat_soil_layers_stag=1_Time=1'])+"[m]\n"))
                    f.write("%s" %("soil_params.slop="+str(soil_params.loc[cat]['slope_Time=1'])+"[m/m]\n"))
                    f.write("%s" %("soil_params.smcmax="+str(soil_params.loc[cat]['smcmax_soil_layers_stag=1_Time=1'])+"[m/m]\n"))
                    f.write("%s" %("soil_params.wltsmc="+str(soil_params.loc[cat]['smcwlt_soil_layers_stag=1_Time=1'])+"[m/m]\n"))
                    f.write("%s" %("soil_params.expon=1.0[]\n"))
                    f.write("%s" %("soil_params.expon_secondary=1.0[]\n"))
                    f.write("%s" %("refkdt="+str(soil_params.loc[cat]['refkdt_Time=1'])+"\n"))
                    f.write("%s" %("max_gw_storage="+str(soil_params.loc[cat]['Zmax'])+"[m]\n"))                   
                    f.write("%s" %("Cgw="+str(soil_params.loc[cat]['Coeff'])+"[m h-1]\n"))
                    f.write("%s" %("expon="+str(soil_params.loc[cat]['Expon'])+"[]\n"))
                    f.write("%s" %("gw_storage=0.05[m/m]\n"))
                    f.write("%s" %("alpha_fc=0.33\n"))
                    f.write("%s" %("soil_storage=0.05[m/m]\n"))
                    f.write("%s" %("K_nash=0.03[]\n"))
                    f.write("%s" %("K_lf=0.01[]\n"))
                    f.write("%s" %("nash_storage=0.0,0.0\n"))
                    f.write("%s" %("num_timesteps=1\n"))
                    if(Xinanjiang_flag == 1): 
                        f.write("%s" %("surface_partitioning_scheme=Xinanjiang\n"))
                        f.write("%s" %("a_Xinanjiang_inflection_point_parameter="+str(soil_params.loc[cat]['AXAJ'])+"\n"))
                        f.write("%s" %("b_Xinanjiang_shape_parameter="+str(soil_params.loc[cat]['BXAJ'])+"\n"))
                        f.write("%s" %("x_Xinanjiang_shape_parameter="+str(soil_params.loc[cat]['XXAJ'])  +"\n"))                     
                    f.write("%s" %("verbosity=1\n"))
                    f.write("%s" %("DEBUG=0\n"))
                    TotalFreq=round(CDF['Freq'].iloc[0],2)
                    giuh="giuh_ordinates="+"{0:.2f}".format((round(CDF['Freq'].iloc[0],2)))
                    for icdf in range(1,len(CDF)):
                        giuh=giuh+","+"{0:.2f}".format((round(CDF['Freq'].iloc[icdf],2)))
                        TotalFreq=TotalFreq+round(CDF['Freq'].iloc[icdf],2)
                    giuh =giuh+"\n"  
                    f.write("%s" %(giuh))
                    f.close()
                    
            else:
                print ("NOT GENERATING CFE FILE " + catstr)
            # 07/30/2021 Commented because it can overwrite a good file when the selected polygon is in the raster area, but not in the HUC 
                # 
                # else:
                #     print (LU)
                #     #DatFile=os.path.join(outputfolder_giuh_param_file,"cat-"+str(cat)+"_giuh.csv")
                #     #CDF.to_csv(DatFile)
                #     if(output_flag==1):                   
                #         DatFile=os.path.join(outputfolder_giuh_config_file,"cat-"+str(cat)+"_bmi_config_cfe_pass.txt")
                #         f= open(DatFile, "w")
                #         string="forcing_file=BMI\nsoil_params.depth=2.0\nsoil_params.b=4.05\nsoil_params.mult=1000.0\nsoil_params.satdk=0.00000338\nsoil_params.satpsi=0.355\nsoil_params.slop=1.0\nsoil_params.smcmax=0.439\nsoil_params.wltsmc=0.066\nmax_gw_storage=16.0\nCgw=0.01\nexpon=6.0\ngw_storage=50%\nalpha_fc=0.33\nsoil_storage=66.7%\nK_nash=0.03\nK_lf=0.01\nnash_storage=0.0,0.0\n"
                #         f.write("%s" %(string))
                #         giuh="giuh_ordinates=1.0,0.0\n"
                #         f.write("%s" %(giuh))
                #         f.close()                   
    
            src_array = None
            rvds = None
            mem_ds = None
            feat = vlyr.GetNextFeature()
    
        print(" NO COVERAGE for " + str(100.*(no_coverage/total)) + "%")
        print(DatFile)
        vds = None
        rds = None


if __name__ == "__main__":


    parser = argparse.ArgumentParser()

    parser.add_argument("namestr",
                        help="HUC name")
    parser.add_argument("catchments",
                        help="Vector source - json")
    parser.add_argument("time_to_stream_raster",
                        help="Time to stream (minutes) raster - tif file")
    parser.add_argument("NWM_param_file",
                        help="CSV file with NWM 2.1 soil params")
    parser.add_argument("outputfolder_giuh",
                        help="Output folder")
    parser.add_argument("--Xinanjiang_flag", type=int, default=0,
                        help="equal to 1 if using Xinanjiang")
    parser.add_argument("--Xinanjiang_param", type=str, default="0",
                        help="CSV table containing parameters for Xinanjiang")    
    parser.add_argument("--buffer", type=float, default=0, metavar="distance",
                        help="Buffer geometry by this distance before calculation")
    parser.add_argument("--nodata", type=float, default=None, metavar="value",
                        help="Use this nodata value instead of value from raster")
    parser.add_argument("--output", type=int, default=1, metavar="flag",
                        help="Write CFE file containing GIUH parameters")
    parser.add_argument("--preload", action="store_true",
                        help="Preload entire raster into memory instead of a read per vector feature")
    parser.add_argument("--flag_discretization", type=int, default=0, metavar="flag",
                        help="If 0 run for all catchments, if 1 run for lumped catchments")


    args = parser.parse_args()
    
    generate_giuh_per_basin_withUnits(args.namestr,args.catchments, args.time_to_stream_raster, args.NWM_param_file,args.outputfolder_giuh,                    
                    Xinanjiang_flag =  args.Xinanjiang_flag,
                    Xinanjiang_param =  args.Xinanjiang_param,
                    nodata_value = args.nodata,
                    global_src_extent = args.preload,
                    buffer_distance = args.buffer,
                    output_flag = args.output,   
                    flag_discretization = args.flag_discretization, 
                    )


#
#namestr='HUC01'
#catchments='/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//HUC01//spatial/catchment_data.geojson'
#time_to_stream_raster='/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//HUC01/HUC01dsave1.tif'
#NWM_param_file='/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//HUC01///parameters/cfe.csv'
#
## GW_params_file='../PerBasin2//'+namestr+'/gwbucket-params-fullrouting.csv'
#outputfolder_giuh='/home/west/Projects/CAMELS/CAMELS_Files_Ngen//HUC01/'
#
#nodata_value = -999
#buffer_distance = 0.001
#output_flag = 1
#global_src_extent=False
#Xinanjiang_flag=0
#Xinanjiang_param="/home/west/Projects/CAMELS/params_code/Xinanj_params.csv"
#
##python generate_giuh_per_basin_params_withUnits.py 1 /media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//1//spatial/catchment_data.geojson /media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//1/1dsave1.tif /media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//1///parameters/cfe.csv /home/west/Projects/CAMELS/CAMELS_Files_Ngen//Watershed3/ --output 1 --Xinanjiang_flag 1 --Xinanjiang_param /home/west/Projects/CAMELS/params_code/Xinanj_params.csv --buffer 0.001 --nodata -999 --flag_discretization 0
#
#namestr=1
#catchments='/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//1//spatial/catchment_data.geojson'
#time_to_stream_raster='/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//1/1dsave1.tif'
#NWM_param_file='/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//1///parameters/cfe.csv'
#
## GW_params_file='../PerBasin2//'+namestr+'/gwbucket-params-fullrouting.csv'
#outputfolder_giuh='/home/west/Projects/CAMELS/CAMELS_Files_Ngen//Watershed3/'
#
#nodata_value = -999
#buffer_distance = 0.001
#output_flag = 1
#global_src_extent=False
#Xinanjiang_flag=0
#Xinanjiang_param="/home/west/Projects/CAMELS/params_code/Xinanj_params.csv"
#
#generate_giuh_per_basin_withUnits(namestr,catchments, time_to_stream_raster,NWM_param_file, outputfolder_giuh,
#                         Xinanjiang_flag=Xinanjiang_flag,Xinanjiang_param=Xinanjiang_param,nodata_value = nodata_value,buffer_distance = buffer_distance,output_flag = output_flag,flag_discretization=0)    

