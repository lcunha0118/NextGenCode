#
if(!require(data.table)){
    install.packages("data.table")
    library(data.table)
}

library(data.table)

load("/media/west/Expansion/Streamflow/obsStrData_ALL_GAGES_UV_topOfHour_2007_2019-002.Rdata")
basins <- commandArgs(TRUE)

for (b1 in basins) {

message(paste0("processing ",b1," ..."))
obsDt <- subset(obsStrData,site_no == b1)
write.csv(obsDt,file=paste0("usgs_hourly_flow_2007-2019_",b1,".csv"),quote=FALSE,row.names=FALSE)
}  
