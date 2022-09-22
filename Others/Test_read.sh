
source ./workflow_hand_twi_giuh_CAMEL_v2.env

while IFS=, read -r id Folder_CAMELS hru_id outlet_id
do
    Folder_CAMELS_ar+=($Folder_CAMELS)
    hru_id_ar+=($hru_id)
    outlet_id+=($outlet_id)
    
    echo "$id $Folder_CAMELS and $hru_id and $outlet_id"
done < <(tail -n +2 ${ListBasins})

len=${#Folder_CAMELS_ar[@]}

for ((i=0; i<$len; i++));do echo "${Folder_CAMELS_ar[$i]}"; done
