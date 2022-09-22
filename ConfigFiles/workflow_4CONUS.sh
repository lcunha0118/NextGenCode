## workflow_hand_twi_giuh: 
## Uses TauDEM to extract topmodel TWI and/or the parameters needed to generate CFE GIUH
## Data: Uses Pre-process DEM for each CAMELS basin
## 	 for other basins see https://github.com/NOAA-OWP/topmodel/tree/master/params or 
##       	              https://github.com/NOAA-OWP/cfe/tree/master/params

## version: v0
## Author: Luciana Cunha <luciana.kindl.da.cunha at noaa.gov>
## Date: 10/07/2021

# This code was tested in linux

# Requirements:
# 	TauDEM (which requires gdal, mpiexec,... see https://github.com/dtarb/TauDEM)
# 	python if the TWI histogram per basin will be created
# 	curl to download the data

# Data Requirements:
# 	hydrofabrics if the TWI histogram per basin will be created

# Use:
# 	Edit the workflow_hand_twi_giuh_CAMELS.env file
# 	Run source workflow_hand_twi_giuh_CAMELS.sh 


source ./workflow_4CONUS.env

declare -a array
declare -a vpu_id_ar hru_id_ar outlet_id_ar test
temp="$(pwd)" 
Dir=${temp//src/}
echo ${Dir}

#mkdir ${Dir}${dem_dir}
#mkdir ${Dir}${out_dir_taudem}
#while IFS=, read -r id Folder_CAMELS hru_id outlet_id
#do
#    Folder_CAMELS_ar+=($Folder_CAMELS)
#    hru_id_ar+=($hru_id)
#    outlet_id+=($outlet_id)
#    
#    echo "$id $Folder_CAMELS and $hru_id and $outlet_id"
#done < <(tail -n +2 ${ListBasins})



while IFS=, read -r vpu	HUC
do

	vpu_id_ar+=($vpu)
	huc_id_ar+=($HUC)
	echo $HUC
        
done < <(tail -n +2 ${ListBasins})

gdalinfo --version

len=${#hru_id_ar[@]}
for ((i=0; i<1; i++));
do 
  
	START_TIME=$(date +%s)
	
	Outdir=${DEM}/
	
	ext=""	
	
	file_name=huc${huc_id_ar[$i]}-res-1
	FelPath=${Outdir}${file_name}fel.tif		
	
	if [[ "$Resolution" -eq 90 ]];then

		ext="90"
		if test -f ${Outdir}${file_name}$ext.tif; then
			echo "${Outdir}${file_name}$ext.tif exists"
		else
			gdalwarp -overwrite ${Outdir}${file_name}.tif ${Outdir}${file_name}$ext.tif -tr 0.0008333 0.0008333 -r max
		fi
		file_name=huc${hru_id_ar[$i]}-res-1$ext
		FelPath=${Outdir}${file_name}fel.tif
	fi
	
	
	# Crop to HUC 
	gdalwarp -cutline --config GDALWARP_IGNORE_BAD_CUTLINE YES ${Outdir}/HUC_${hru_id_ar[$i]}.shp -dstalpha ${Outdir}${file_name}.tif -dstnodata "-999.0" ${Outdir}${file_name}cp.tif 
	file_name=huc${hru_id_ar[$i]}-res-1${ext}cp
	FelPath=${Outdir}${file_name}fel.tif
	#-----------------------------------------------
	# pitremove  
	echo "Process DEM"
	if test -f ${FelPath}; then
		echo "${FelPath} exists"
	else
		mpiexec -np $nproc pitremove -z ${Outdir}${file_name}.tif -fel ${FelPath}
		echo mpiexec -np $nproc pitremove -z ${Outdir}${file_name}.tif -fel ${FelPath}
	fi 	
	
	#-----------------------------------------------
	# dinfflowdir  
	if test -f ${Outdir}${file_name}ang.tif; then
		echo "${Outdir}${file_name}ang.tif exists\n"
	else
		mpiexec -np $nproc dinfflowdir -ang ${Outdir}${file_name}ang.tif -slp ${Outdir}${file_name}slp.tif -fel ${FelPath}
	fi
	
	rm ${Outdir}${file_name}hf.tif
	echo gdal_translate  -scale 0  40000000000000 0 0 ${FelPath} ${Outdir}${file_name}hf.tif	
	gdal_translate  -scale 0  40000000000000 0 0 ${FelPath} ${Outdir}${file_name}hf.tif
	#gdal_translate -a_srs EPSG:5070 -scale 0  40000000000000 0 0 ${Outdir}${file_name}fel.tif ${Outdir}${file_name}hf.tif
	echo gdal_rasterize -b 1 -burn 1  ${Hydrof_dir}/${huc_id_ar[$i]}/flowpaths_4269.geojson ${Outdir}${file_name}hf.tif	
	gdal_rasterize -b 1 -burn 1  ${Hydrof_dir}/${huc_id_ar[$i]}/flowpaths_4269.geojson ${Outdir}${file_name}hf.tif	 			
	
	#-----------------------------------------------
	# Only if we want to extract the river network
	#if test -f ${Outdir}${file_name}sca.tif; then
	#	echo "${Outdir}${file_name}sca.tif exists"
	#else
#		mpiexec -np $nproc  areadinf -ang ${Outdir}${file_name}ang.tif -sca ${Outdir}${file_name}sca.tif 
	#fi		

		
	#if test -f ${Outdir}${file_name}sa.tif; then
	#	echo "${Outdir}${file_name}sa.tif exists"
	#else
	#	mpiexec -np $nproc slopearea ${Outdir}${file_name}.tif
	#fi
	#if test -f ${Outdir}${file_name}p.tif; then
	#echo "${Outdir}${file_name}p.tif exists"
	#else
	#	mpiexec -np $nproc d8flowdir ${Outdir}${file_name}.tif
	#fi
	#if test -f ${Outdir}${file_name}ad8.tif; then
	#	echo "${Outdir}${file_name}ad8.tif exists"
	#	echo mpiexec -np $nproc aread8 ${Outdir}${file_name}.tif
	#else
#		mpiexec -np $nproc aread8 ${Outdir}${file_name}.tif
		
	#fi	
	#if test -f ${Outdir}${file_name}ssa.tif; then
	#	echo "${Outdir}${file_name}ssa.tif exists"
	#else		
	#	mpiexec -np $nproc d8flowpathextremeup ${Outdir}${file_name}.tif
	#fi
#
	#if test -f ${Outdir}${file_name}src.tif; then
	#	echo "${Outdir}${file_name}src.tif exists"
	#else
	#	mpiexec -np $nproc threshold -ssa ${Outdir}${file_name}ssa.tif -src ${Outdir}${file_name}src.tif -thresh 300
	#fi
		
	#python generate_travel_time_by_pixel.py ${file_name} ${Outdir} ${Outdir} --method=${method} --manning=${Dir}${manning}


	if test -f ${Outdir}${file_name}dsave_test.tif; then
		echo "${Outdir}${file_name}dsave${method}.tif exists"
	else	
		mpiexec -np $nproc dinfdistdown -ang ${Outdir}${file_name}ang.tif -fel ${FelPath} -src ${Outdir}${file_name}hf.tif -dd ${Outdir}${file_name}dsave_test.tif -m ave s
	fi			
	
	#if test -f ${Outdir}${file_name}dsave${method}.tif; then
	#	echo "${Outdir}${file_name}dsave${method}.tif exists"
	#else	
	#	mpiexec -np $nproc dinfdistdown -ang ${Outdir}${file_name}ang.tif -fel ${FelPath} -src ${Outdir}${file_name}hf.tif -wg ${Outdir}${file_name}wg${method}.tif -dd ${Outdir}${file_name}dsave${method}.tif -m ave s
	#fi			
done
