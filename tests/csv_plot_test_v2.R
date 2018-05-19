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
setnames(DT, c("date", gsub(".*_(.*).csv", "\\1", f)))

## Convert to long format for plotting
DT_long <- melt(DT, id = "V1")

## Plot
myPlot <- 
  ggplot(DT_long, aes(V1, value, color = variable)) + 
  geom_point()
## + xlim(400,3500) + ylim(0,17)

## Create Interactive Plot
ggplotly(myPlot)


## Converting to groups


range_var <- 600

## find all non-NA evt
indx <- DT[!is.na(evt), .(date = date - 1, evt)]


## matrix of indx + range_var
mat <- data.table(mapply(`:`, indx$date, indx$date + range_var - 1))
setnames(mat, as.character(indx$evt))

# melting
long_mat <- melt(mat)

# Adding pupil
long_mat[, pupil := DT[long_mat$value, pupil]]

# validating
long_mat[, .N, by = variable]

# creating groups of range_var
long_mat[, grp := (0:(.N - 1)) %/% range_var]

#validating
long_mat[, .N, by = .(variable, grp)]

# Assiging date range
long_mat[, date := 1:range_var]

#renaming variable to evt
names(long_mat)[1] <- "evt"

#plotting
ggplot(long_mat, aes(date, pupil, color = evt)) + 
  geom_point(alpha = 1) +
  geom_smooth()



