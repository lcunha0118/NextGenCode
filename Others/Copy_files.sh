
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
while IFS=, read -r id Folder_CAMELS hru_id outlet_id
do
    Folder_CAMELS_ar+=($Folder_CAMELS)
    hru_id_ar+=($hru_id)
    outlet_id+=($outlet_id)
    
    echo "$id $Folder_CAMELS and $hru_id and $outlet_id"
done < <(tail -n +2 ${ListBasins})

len=${#Folder_CAMELS_ar[@]}

gdalinfo --version
for ((i=0; i<$len; i++));
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
	echo cp ${out_dir_giuh}/${Folder}/CFE/${hru}_bmi_config_cfe_pass.txt /home/west/Projects/CAMELS/CAMELS_Files_Ngen/CFE_Config_lumped
	
	cp ${out_dir_giuh}/${Folder}/CFE/${hru}_bmi_config_cfe_pass.txt /home/west/Projects/CAMELS/CAMELS_Files_Ngen/CFE_Config_lumped
	
done
