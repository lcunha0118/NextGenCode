import os
import geopandas as gpd
import subprocess
import pandas as pd



Hydrofabrics_folder="/home/west/Projects/CAMELS/CAMELS_Files_Ngen/"
Selected_calibration=pd.read_csv(Hydrofabrics_folder+"Select_calibration_HLR.csv",dtype={'hru_id_CAMELS': str})
Selected_calibration=Selected_calibration.set_index(['hru_id_CAMELS'])

calib_config = calib_directory+'calib_config_CAMELS_CFE_calib2.yaml'

for i in range(0,40):


    Folder=Selected_calibration.iloc[i]['Folder_CAMELS']
    hru_id=Selected_calibration.index[i]
    Base_directory = Hydrofabrics_folder+"/"+Folder+"/"
    calib_directory = Base_directory+calib_folder+"/"    




    catchments = Base_directory/'spatial/catchment_data.geojson'
    NWM_param_file=Base_directory+'/parameters/cfe.csv'
    calib_config_file = calib_directory+'calib_config_CAMELS_CFE.yaml'


    if(Selected_calibration.iloc[i]['N_Nexus']>=2):
        
        try:
            Folder_CAMELS=Selected_calibration.iloc[i]['Folder_CAMELS']
            hru_id=Selected_calibration.index[i]
            word_dir=Hydrofabrics_folder+Folder_CAMELS+"/"
            os.chdir(word_dir)
            
            catchments='/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//HUC01//spatial/catchment_data.geojson'
            time_to_stream_raster='/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//HUC01/HUC01dsave1.tif'
            

# GW_params_file='../PerBasin2//'+namestr+'/gwbucket-params-fullrouting.csv'
outputfolder_giuh='/home/west/Projects/CAMELS/CAMELS_Files_Ngen//HUC01/'

nodata_value = -999
buffer_distance = 0.001
output_flag = 1
global_src_extent=False
Xinanjiang_flag=0
Xinanjiang_param="/home/west/Projects/CAMELS/params_code/Xinanj_params.csv"

#python generate_giuh_per_basin_params_withUnits.py 1 /media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//1//spatial/catchment_data.geojson /media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//1/1dsave1.tif /media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//1///parameters/cfe.csv /home/west/Projects/CAMELS/CAMELS_Files_Ngen//Watershed3/ --output 1 --Xinanjiang_flag 1 --Xinanjiang_param /home/west/Projects/CAMELS/params_code/Xinanj_params.csv --buffer 0.001 --nodata -999 --flag_discretization 0

namestr=1
catchments='/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//1//spatial/catchment_data.geojson'
time_to_stream_raster='/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//1/1dsave1.tif'
NWM_param_file='/media/west/Expansion/Backup/Projects/CAMELS/PerBasin4//1///parameters/cfe.csv'

# GW_params_file='../PerBasin2//'+namestr+'/gwbucket-params-fullrouting.csv'
outputfolder_giuh='/home/west/Projects/CAMELS/CAMELS_Files_Ngen//Watershed3/'

nodata_value = -999
buffer_distance = 0.001
output_flag = 1
global_src_extent=False
Xinanjiang_flag=0
Xinanjiang_param="/home/west/Projects/CAMELS/params_code/Xinanj_params.csv"


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


vds = ogr.Open(catchments, GA_ReadOnly)  
assert(vds)
vlyr =   vds.GetLayer(0)
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
    #if(not "cat-" in str(soil_params.index[0])): soil_params.index = 'cat-' + soil_params.index.astype(str)


    # Remove Nan for the parameters that are used to generate config file
    # Replace with values from the original CFE config file
    #print ("Getting values from table ")
    soil_params['bexp_soil_layers_stag=1_Time=1']= soil_params['sp_bexp_soil_layers_stag=1'].fillna(16)                    
    soil_params['dksat_soil_layers_stag=1_Time=1']= soil_params['sp_dksat_soil_layers_stag=1'].fillna(0.00000338)
    soil_params['psisat_soil_layers_stag=1_Time=1']= soil_params['sp_psisat_soil_layers_stag=1'].fillna(0.355)  
    soil_params['slope_Time=1']= soil_params['sp_slope'].replace(np.nan,1.0)
    soil_params['smcmax_soil_layers_stag=1_Time=1']= soil_params['sp_smcmax_soil_layers_stag=1'].fillna(0.439)
    soil_params['smcwlt_soil_layers_stag=1_Time=1']= soil_params['sp_smcwlt_soil_layers_stag=1'].fillna(0.066)
    soil_params['wf_ISLTYP']= soil_params['wf_ISLTYP'].fillna(1)
    #soil_params['fd_LKSATFAC']= soil_params['fd_LKSATFAC'].fillna(1000)
    if('sp_refkdt' in soil_params): soil_params['refkdt_Time=1']= soil_params['sp_refkdt'].fillna(3.0)
    else: soil_params['refkdt_time=1']=3.0
    
    soil_params['Zmax'] = soil_params['gw_Zmax'].fillna(16.0)/1000.
    soil_params['Coeff'] = soil_params['gw_Coeff'].fillna(0.5)*3600*pow(10,-6)
    soil_params['Expon'] = soil_params['gw_Expon'].fillna(6.0)
    #soil_params['mult'] = soil_params['fd_LKSATFAC'].fillna(6.0)
else:
    
    skippednulgeoms = False
    total = vlyr.GetFeatureCount(force = 0)
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
    soil_params['wf_ISLTYP'] = 1
    
if(Xinanjiang_flag == 1): 
    print ("Xinanjiang_flag = "+str(Xinanjiang_flag))
    Xin_param=pd.read_csv(Xinanjiang_param,index_col=0)
    soil_params['AXAJ']=Xin_param.loc[soil_params['wf_ISLTYP'].values]['AXAJ'].values
    soil_params['BXAJ']=Xin_param.loc[soil_params['wf_ISLTYP'].values]['BXAJ'].values
    soil_params['XXAJ']=Xin_param.loc[soil_params['wf_ISLTYP'].values]['XXAJ'].values
# soil_params_depth=2.0;soil_params_b_st=4.05;soil_params_mult_st=1000.0;soil_params_satdk_st=0.00000338; soil_params_satpsi_st=0.355    
# soil_params_slop_st=1.0; soil_params_smcmax_st=0.439; soil_params_wltsmc_st=0.066;
# max_gw_storage_st=16.0; Cgw_st=0.01; expon_st=6.0;
# gw_storage_st=50;alpha_fc_st=0.33; soil_storage_st=66.7
# K_nash_st=0.03;K_lf_st=0.01
# nash_storage_st='0.0,0.0'; giuh_ordinates_st='0.06,0.51,0.28,0.12,0.03'

#CREATE GIUH for the whole catchment
