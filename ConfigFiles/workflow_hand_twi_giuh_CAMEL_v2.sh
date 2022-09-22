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


source ./workflow_hand_twi_giuh_CAMEL_v2.env

declare -a array
declare -a Folder_CAMELS_ar hru_id_ar outlet_id_ar
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



while IFS=, read -r hru_id Folder_CAMELS outlet_id RunPET NCat SA aridity p_sea snow_fra Snow10_arid15
do
    echo  "$Flag_SA"
    if [[ "$Flag_SA" -eq 0 ]];then
	Folder_CAMELS_ar+=($Folder_CAMELS)
	hru_id_ar+=($hru_id)
	outlet_id_ar+=($outlet_id)
	RunPET_ar+=($RunPET)
	NCat_ar+=($NCat)
	SA_ar+=($SA)
    else
    	if [[ $SA -eq 1 ]]; then 
		Folder_CAMELS_ar+=($Folder_CAMELS)
		hru_id_ar+=($hru_id)
		outlet_id_ar+=($outlet_id)
		RunPET_ar+=($RunPET)
		NCat_ar+=($NCat)
		SA_ar+=($SA)
    	fi
    	echo "$Folder_CAMELS and $hru_id and $outlet_id and $RunPET  and $NCat  and $SA"
    fi
        
done < <(tail -n +2 ${ListBasins})
len=${#Folder_CAMELS_ar[@]}
gdalinfo --version
for ((i=2; i<3; i++));
do 
    	hru=${hru_id_ar[$i]}
    	Folder=${Folder_CAMELS_ar[$i]}
    	outlet=${outlet_id_ar[$i]}
	mkdir ${out_dir_twi}/${Folder}
	mkdir ${out_dir_giuh}/${Folder}
    	echo "running ${hru}, for ${Variable}, at ${Resolution} m resolution" 
	file_name=${hru}

	START_TIME=$(date +%s)
	

	Outdir=${CAMELS_directory}/${hru}/

	if [[ "$Resolution" -eq 30 ]];then
		
		file_name=${hru}
		
		FelPath=${Outdir}${file_name}fel.tif

		#-----------------------------------------------
		# pitremove  
		echo "Process DEM"
		if test -f ${Outdir}${file_name}fel.tif; then
			echo "${Outdir}${file_name}fel.tif exists"
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
	else 
		echo "Only 30 meter resolution is available"
	fi

	#-----------------------------------------------
	# areadinf - sca 
	if test -f ${Outdir}${file_name}sca.tif; then
		echo "${Outdir}${file_name}sca.tif exists"
	else
		mpiexec -np $nproc  areadinf -ang ${Outdir}${file_name}ang.tif -sca ${Outdir}${file_name}sca.tif 
	fi
		
	if test -f ${Outdir}${file_name}hf.tif; then
		rm ${Outdir}${file_name}hf.tif
	fi
	rm ${Outdir}/spatial/flowpath_data_4269.json
	ogr2ogr -f "GeoJSON" ${Outdir}/spatial/flowpath_data_4269.json ${Outdir}/spatial/flowpath_data.geojson  -s_srs EPSG:4269 -t_srs EPSG:4269
	echo ogr2ogr -f "GeoJSON" ${Outdir}/spatial/flowpath_data_4269.json ${Outdir}/spatial/flowpath_data.geojson  -s_srs EPSG:4269 -t_srs EPSG:4269
	echo gdal_translate  -scale 0  40000000000000 0 0 ${Outdir}${file_name}fel.tif ${Outdir}${file_name}hf.tif	
	gdal_translate -scale 0  40000000000000 0 0 ${Outdir}${file_name}fel.tif ${Outdir}${file_name}hf.tif
	#gdal_translate -a_srs EPSG:5070 -scale 0  40000000000000 0 0 ${Outdir}${file_name}fel.tif ${Outdir}${file_name}hf.tif
	echo gdal_rasterize -b 1 -burn 1  ${Outdir}/spatial/flowpath_data_4269.json ${Outdir}${file_name}hf.tif	
	gdal_rasterize -b 1 -burn 1  ${Outdir}/spatial/flowpath_data_4269.json ${Outdir}${file_name}hf.tif 			
	
	if [[ $Variable == *"TWI"* ]]; then

		#-----------------------------------------------
		# twi
		echo "Generate Topographic Wetness Index"
		if test -f ${Outdir}${file_name}twi.tif; then
			echo "${Outdir}${file_name}twi.tif exists"
		else
		mpiexec -np $nproc twi -slp ${Outdir}${file_name}slp.tif -sca ${Outdir}${file_name}sca.tif -twi ${Outdir}${file_name}twi.tif
		fi

		#-----------------------------------------------
		# Crop TWI and slope
#		echo "Crop DEM to the area of interest based on Shapefile"
#		if test -f ${Outdir}${file_name}twi_cr.tif; then
#			echo "${Outdir}${file_name}twi_cr.tif exists"
#		else
		
#			gdalwarp -cutline --config GDALWARP_IGNORE_BAD_CUTLINE YES ${Outdir}/${hru}.shp -dstalpha ${Outdir}${file_name}twi.tif -dstnodata "-999.0" ${Outdir}${file_name}twi_cr.tif
#			gdalwarp -cutline --config GDALWARP_IGNORE_BAD_CUTLINE YES ${Outdir}/${hru}.shp -dstalpha ${Outdir}${file_name}slp.tif -dstnodata "-999.0" ${Outdir}${file_name}slp_cr.tif
#		fi
		
		# LKC: Comment since hydrofabrics is in 4326
		#if test -f  ${Outdir}catchments_wgs84.json; then
			#echo "catchments_wgs84.json exists"
		#else
		 	#echo "Reproject hydrofabrics file catchments_wgs84.json"

			#ogr2ogr -f "GeoJSON" ${Outdir}catchments_wgs84.json ${Outdir}aggregated_catchments.geojson  -s_srs EPSG:5070 -t_srs EPSG:4326
			#ogr2ogr -f "GeoJSON" ${Outdir}flowpaths_wgs84.json ${Outdir}aggregated_flowpaths.geojson -s_srs EPSG:5070 -t_srs EPSG:4326
			
		#fi


	fi


	#-----------------------------------------------
	# Extract the river network
	# TODO: This can be improved with the DropAnalysis method, but it requires the Outlet of the basin
		
	if test -f ${Outdir}${file_name}sa.tif; then
		echo "${Outdir}${file_name}sa.tif exists"
	else
		mpiexec -np $nproc slopearea ${Outdir}${file_name}.tif
	fi
	if test -f ${Outdir}${file_name}p.tif; then
		echo "${Outdir}${file_name}p.tif exists"
	else
		mpiexec -np $nproc d8flowdir ${Outdir}${file_name}.tif
	fi
	if test -f ${Outdir}${file_name}ad8.tif; then
		echo "${Outdir}${file_name}ad8.tif exists"
		echo mpiexec -np $nproc aread8 ${Outdir}${file_name}.tif
	else
		mpiexec -np $nproc aread8 ${Outdir}${file_name}.tif
		
	fi
	if test -f ${Outdir}${file_name}ssa.tif; then
		echo "${Outdir}${file_name}ssa.tif exists"
	else		
		mpiexec -np $nproc d8flowpathextremeup ${Outdir}${file_name}.tif
	fi
	# This will eventually provided by the hydrofabrics, so I am not worrying about this for now		
	if test -f ${Outdir}${file_name}fake_src.tif; then
		echo "${Outdir}${file_name}fake_src.tif exists"
	else	
		mpiexec -np $nproc threshold -ssa ${Outdir}${file_name}ssa.tif -src ${Outdir}${file_name}fake_src.tif -thresh 3000
		
	fi
	# This will latter be modified when the hydrofabrics include the outlet of HUC06 basins. DropAnalysis will be used to define the best threshold for different areas in USA

	if test -f ${Outdir}${file_name}src.tif; then
		echo "${Outdir}${file_name}src.tif exists"
	else
		mpiexec -np $nproc threshold -ssa ${Outdir}${file_name}ssa.tif -src ${Outdir}${file_name}src.tif -thresh 300
	fi


	if [[ $Variable == *"GIUH"* ]]; then

		#Generate travel time in minutes/meter per pixel

		python generate_travel_time_by_pixel.py ${file_name} ${Outdir} ${Outdir} --method=${method} --manning=${Dir}${manning}

		#Generate travel time in minutes accumulated over the network
		#7/30/2021 - Change from "-m ave h" to "-m ave s" - calculate distance based on the The along the surface difference in elevation between grid cells (s=h*sqrt(1+slope2)
		if test -f ${Outdir}${file_name}dsave${method}.tif; then
			echo "${Outdir}${file_name}dsave${method}.tif exists"
		else	
			echo mpiexec -np $nproc dinfdistdown -ang ${Outdir}${file_name}ang.tif -fel ${FelPath} -src ${Outdir}${file_name}hf.tif -wg ${Outdir}${file_name}wg${method}.tif -dd ${Outdir}${file_name}dsave${method}.tif -m ave s
			mpiexec -np $nproc dinfdistdown -ang ${Outdir}${file_name}ang.tif -fel ${FelPath} -src ${Outdir}${file_name}hf.tif -wg ${Outdir}${file_name}wg${method}.tif -dd ${Outdir}${file_name}dsave${method}.tif -m ave s
			
			#crop the hydrofabrics
#			gdalwarp -cutline --config GDALWARP_IGNORE_BAD_CUTLINE YES ${Outdir}/${hru}.shp -dstalpha ${Outdir}${file_name}dsave${method}.tif -dstnodata "-999.0" ${Outdir}${file_name}dsave${method}_cr.tifcd 
		fi
				
		#generate GIUH per basin for CFE
		echo python generate_giuh_per_basin_params_withUnits.py ${hru} ${Outdir}/spatial/catchment_data.geojson ${Outdir}${file_name}dsave${method}.tif ${Outdir}/${NWM_file} ${out_dir_giuh}/${Folder}/ --output 1 --buffer 0.001 --nodata -999 --flag_discretization 0
		python generate_giuh_per_basin_params_withUnits.py ${hru} ${Outdir}/spatial/catchment_data.geojson ${Outdir}${file_name}dsave${method}.tif ${Outdir}/${NWM_file} ${out_dir_giuh}/${Folder}/ --output 1 --buffer 0.001 --nodata -999 --flag_discretization 0
		#generate GIUH per basin for CFE_X
		echo python generate_giuh_per_basin_params_withUnits.py ${hru} ${Outdir}/spatial/catchment_data.geojson ${Outdir}${file_name}dsave${method}.tif ${Outdir}/${NWM_file} ${out_dir_giuh}/${Folder}/ --output 1 --Xinanjiang_flag 1 --Xinanjiang_param ${Xin_param} --buffer 0.001 --nodata -999 --flag_discretization 0
		python generate_giuh_per_basin_params_withUnits.py ${hru} ${Outdir}/spatial/catchment_data.geojson ${Outdir}${file_name}dsave${method}.tif ${Outdir}/${NWM_file} ${out_dir_giuh}/${Folder}/ --output 1 --Xinanjiang_flag 1 --Xinanjiang_param ${Xin_param} --buffer 0.001 --nodata -999 --flag_discretization 0
		#generate GIUH as lumpled basin for CFE
		echo python generate_giuh_per_basin_params_withUnits.py ${hru} ${Outdir}/spatial/catchment_data.geojson ${Outdir}${file_name}dsave${method}.tif ${Outdir}/${NWM_file} ${out_dir_giuh}/${Folder}/ --output 1 --buffer 0.001 --nodata -999 --flag_discretization 1
		python generate_giuh_per_basin_params_withUnits.py ${hru} ${Outdir}/spatial/catchment_data.geojson ${Outdir}${file_name}dsave${method}.tif ${Outdir}/${NWM_file} ${out_dir_giuh}/${Folder}/ --output 1 --buffer 0.001 --nodata -999 --flag_discretization 1
		
		
	fi

	if [[ $Variable == *"TWI"* ]]; then

		if test -f ${Outdir}${file_name}dsave_noweight_cr.tif; then
			echo "${Outdir}${file_name}dsave_noweight.tif exists"
		else
			echo "Change this when I get hydrofabrics"
		#7/30/2021 - Calculate the distance downstream - used to generate the width function for topmodel
			# LKC: Uncomment when get hydrofabrics
			mpiexec -np $nproc dinfdistdown -ang ${Outdir}${file_name}ang.tif -slp ${Outdir}${file_name}slp.tif -fel ${FelPath} -src ${Outdir}${file_name}hf.tif -dd ${Outdir}${file_name}dsave_noweight.tif -m ave s	 
#			gdalwarp -cutline --config GDALWARP_IGNORE_BAD_CUTLINE YES ${Outdir}/spatial/catchment_data.json -dstalpha ${Outdir}${file_name}dsave_noweight.tif -dstnodata "-999.0" ${Outdir}${file_name}dsave_noweight_cr.tif	
		
		fi	

		echo "Generating histogram"						
		#conda activate $python_env
		#generate TWI per basin - need to modify to also generate width function
		
		echo python generate_twi_per_basin.py ${hru} ${Outdir}/spatial/catchment_data.geojson ${Outdir}${file_name}twi.tif ${Outdir}${file_name}slp.tif ${Outdir}${file_name}dsave_noweight.tif ${Outdir}/$NWM_file ${out_dir_twi}/${Folder}/ --output 1 --buffer 0.001 --nodata -999
		python generate_twi_per_basin.py ${hru} ${Outdir}/spatial/catchment_data.geojson ${Outdir}${file_name}twi.tif ${Outdir}${file_name}slp.tif ${Outdir}${file_name}dsave_noweight.tif  ${Outdir}/$NWM_file ${out_dir_twi}/${Folder}/ --output 1 --buffer 0.001 --nodata -999
		
	fi	

	END_TIME=$(date +%s)
	echo "It took $(($END_TIME-$START_TIME)) seconds to process ${file_name}" 
done
