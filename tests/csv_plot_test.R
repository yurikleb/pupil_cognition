## Packages
library(data.table)
library(ggplot2)
library(plotly)

## List the files in the folder <---- INSERT THE CORRECT PATH OF THE FILES!
(f <- list.files("~/Desktop/Experiment_Data/00_PupilRecordings/2018_04_12/Christian/recorder_data", full.names = TRUE, pattern = "\\.csv"))

## Read all the files into a list
l <- lapply(f, fread)

# Merge all the files into a data.table
DT <- Reduce(function(...) merge(..., by = "V1", all = TRUE), l)


## Convert to long format for plotting
DT_long <- melt(DT, id = "V1")

## Plot
myPlot <- 
  ggplot(DT_long, aes(V1, value, color = variable)) + 
  geom_point()
  ## + xlim(400,3500) + ylim(0,17)

## Create Interactive Plot
ggplotly(myPlot)
