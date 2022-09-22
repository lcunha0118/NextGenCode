
rm(list=ls())

library(data.table)
library(ggplot2)
library(scales)
library(gridExtra)
library(dplyr)


# load data
load("statAll_24sites.Rdata")


# plot maps

# set clean background (no need this if lat and lon axes needed for the map)
theme_clean <- function(base_size = 11) {
  require(grid) # Needed for unit() function
  theme_grey(base_size) %+replace%
    theme(
      axis.title = element_blank(),
      axis.text = element_blank(),
      panel.background = element_blank(),
      panel.grid = element_blank(),
      axis.ticks.length = unit(0, "cm"),
      complete = TRUE
    )
}



# adding the state map to the plots
  usPoly <- ggplot2::map_data("state")


#sebset data for plots
statm1 <- subset(statAll, 
          select=c("Nse", "Bias", "modRun", "hru_id_CAMELS","lat","lon"))


form1 <- c("NOAH_CFE", "NOAH_CFE_X", "NOAH_Topmodel")
form2 <- c("PET_1_CFE", "PET_1_CFE_X", "PET_1_Topmodel")
form3 <- c("PET_2_CFE", "PET_2_CFE_X", "PET_2_Topmodel")
form4 <- c("PET_3_CFE", "PET_3_CFE_X", "PET_3_Topmodel") 
form5 <- c("PET_4_CFE", "PET_4_CFE_X", "PET_4_Topmodel")
form6 <- c("PET_5_CFE", "PET_5_CFE_X", "PET_5_Topmodel") 
form7 <- c("NOAH_CFE_GWIC8", "NOAH_CFE_KNash", "NOAH_CFE_klNash")

# formulation group list
formList <- list(form1, form2, form3, form4, form5, form6, form7)
formList


for (ii in 1:7) {
form <- formList[[ii]] #Note: need double [[]]

#subset formulation group
statm <- subset(statm1, modRun %in% form)
dim(statm)


# plot nse map
gNse <- ggplot(statm, aes(lon, lat, fill=Nse, size=meanObs), alpha=0.8) +
  geom_point(shape = 21, stroke = 1) + # change the thickness of the boarder with stroke
  ggplot2::scale_size("meanObs (m/d)", range=c(2, 8)) +
  facet_wrap( ~ modRun, ncol=3) +
  scale_fill_continuous("NSE",  low='#b3cde3', high='#810f7c', na.value="transparent", 
                        breaks=c(0, 0.2, 0.4, 0.6, 0.8), limits=c(0,0.8)) +
ggplot2::guides(fill = guide_colourbar(order=1), size = guide_legend(order=2))+
#ggplot2::guides(fill=guide_legend(override.aes=list(size=3),order=1), size=guide_legend(order=2))+
  theme_clean() +
ggplot2::geom_polygon(data=usPoly, ggplot2::aes(x=long, y=lat, group=group), color="grey", size=0.1, fill = NA)+



# plot bias map
gBias <- ggplot(statm, aes(lon, lat, fill=Bias, size=meanObs), alpha=0.8) +
  geom_point(shape = 21, stroke = 1) + # change the thickness of the boarder with stroke
  ggplot2::scale_size("meanObs (m/d)", range=c(2, 8)) +
  facet_wrap( ~ modRun, ncol=3) +
  scale_fill_gradient2("Bias (m/d)", midpoint=0, low='red',mid='white',high='blue',
                       breaks=c(-0.002, -0.001, 0, 0.001, 0.002),limits=c(-0.0025,0.0025)) +
ggplot2::guides(fill = guide_colourbar(order=1), size = guide_legend(order=2)) +
  theme_clean() +
ggplot2::geom_polygon(data=usPoly, ggplot2::aes(x=long, y=lat, group=group), color="grey", size=0.1, fill = NA)+


}

