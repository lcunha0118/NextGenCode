## generate validation data: 

CAMELS_directory=../PerBasin4/                          					# Folder with data for each CAMELS basin 	
#declare -a hru_id=("2427250") # List CAMELS basin to process
ListBasins=/home/west/Projects/CAMELS/camels_basin_list_516NoHeader.txt			# camels_basin_list_516.txt or Test_1basin.txt

echo "${ListBasins}"

while read -r line; do
	array+=("$(echo "$line")")
done <"${ListBasins}"

echo "$ListBasins"

Rscript extract_usgs_flow_by_basin.R "${array[@]}"

for val in  "${array[@]}"; do
    	hru="$val"	
    	mkdir $CAMELS_directory/data_CAMELS/$hru/Validation/
    	mv usgs_*$val*.csv $CAMELS_directory/data_CAMELS/$hru/Validation/
	#Rscript extract_usgs_flow_by_basin.R $hru
done

