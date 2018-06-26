## Packages
library(dygraphs)
library(data.table)
library(ggplot2)
library(plotly)

options(digits=12)

mainFilesPath = "/media/yurikleb/Yuri_IDE_07477204021/DesignLab/CV/ExperimentData/MAIN/openDay/2018_06_09/subject_33_good_fast/"

multimerge = function(mypath, keycol, selcol){
  
  ##List the files in the folder
  Path <- mypath
  (f <- list.files(Path, full.names = TRUE, pattern = "\\.csv"))
  
  ## Read all the files into a list
  l <- lapply(f, fread, select = selcol)

  # Merge all the files into a data.table
  Reduce(function(...) merge(..., by = keycol, all = TRUE), l)

}

# Add Column Titles inside recorder_data - CSVs
myPath <- "/media/yurikleb/Yuri_IDE_07477204021/DesignLab/CV/ExperimentData/MAIN/2018_04_12_Sunny/Christian/recorder_data"
fl <- list.files(myPath, full.names = TRUE, pattern = "\\.csv")
fl

f <- fread(fl[[1]])
setnames(f, c("sample","evt"))
fwrite(f, file = fl[[1]])

f <- fread(fl[[2]])
setnames(f, c("sample","lux"))
fwrite(f, file = fl[[2]])

f <- fread(fl[[3]])
setnames(f, c("sample","pupil_size"))
fwrite(f, file = fl[[3]])

######## Merge all "Recorder App Data" tables
folderPath <- myPath #paste(mainFilesPath, "recorder_data/", sep = "")
colsFilter <- c("sample", "evt", "lux", "pupil_size")
DT1 = multimerge(folderPath, "sample", colsFilter)

# DT1
# fwrite(DT1, file = file.path(folderPath, "Fused_Data.csv"))


######## Merge all "Pupil Player Data" exported Tables
# Prepare the files to merge
# Copy pupil_positions.csv to "selected" folder
# Adjust fixation.csv column names and copy to "selected" folder 
if (!file.exists(file.path(mainFilesPath, "exports/selected/"))){
  dir.create(file.path(mainFilesPath, "exports/selected/"))
}

file.copy(paste0(mainFilesPath, "exports/pupil_positions.csv"),paste0(mainFilesPath, "exports/selected/pupil_positions.csv"))

cols <- c("id", "start_timestamp", "duration")
f <- fread(paste0(mainFilesPath, "exports/fixations.csv"), select = cols)
setnames(f, cols, c("fp_id", "timestamp", "fp_duration"))
fwrite(f, file = paste0(mainFilesPath, "exports/selected/fixations.csv"))         

# Merge the "selected" files
folderPath <- paste0(mainFilesPath, "exports/selected/")
colsFilter <- c("timestamp", "start_timestamp", "fp_id", "fp_duration", "diameter_3d", "index", 
                "circle_3d_center_x", "circle_3d_center_y", "circle_3d_center_z",
                "circle_3d_normal_x", "circle_3d_normal_y", "circle_3d_normal_z")
DT2 = multimerge(folderPath, "timestamp", colsFilter)
DT2


# Trim the top extra values from "Pupil Player Data"
# So "Recorder_Data" and "Pupil Player Data" start from the same point in time.
initialPupil <- DT1[1,pupil_size]
indx <-  which.max(DT2$diameter_3d == initialPupil) - 1
DT2 = tail(DT2, -indx)

# Merge DT1 and DT2
indx <-  min(nrow(DT1), nrow(DT2))
DT3 = cbind(head(DT1, indx), head(DT2, indx))
DT3
# view(DT3)

#Save as a  SCV 
fwrite(DT3, file = file.path(mainFilesPath, "Fused_Data.csv"))


# Analyze Fixation Points
# DT3[fp_id > 0, .(fp_id,pupil_size,fp_duration)]
# Get samples around fixation point 

# Get the row index of a specifix fixation point
# fp <- 4
# fpIdx <- DT3[fp_id == fp, which = TRUE]
# fpIdx

range = 6

fpPaddingData = function(fpNum){
  fpIdx <- DT3[fp_id == fpNum, which = TRUE]
  DT3[(fpIdx - range / 2):(fpIdx+ range / 2), .(sample, evt,lux,pupil_size, fp_id)]
}

# Get a List of all fixation points
fp_list <- DT3[fp_id>0, fp_id]
# Create a list of padding data around all fixations points
FP_DATA <- lapply(fp_list, fpPaddingData)
FP_DATA

fpToPlot <- 6
dygraph(FP_DATA[[fpToPlot]]) %>%
  dySeries("evt", color = "#c44e39") %>%
  dySeries("lux", color = "#ffa500") %>%
  dySeries("pupil_size", color = "#3ac44a") %>%
  dySeries("fp_id", color = "#5c5c5c") %>%
  dyOptions(pointSize = 5) %>%
  dyRangeSelector(height = 20)


#################
#PLOT DATA
#################
# Convert fixation poitn IDs to fives (5)
DT3[fp_id > 0, fp_id := 5]
## draw dygraph
DT_Plot <- DT3[,.(sample,evt,lux,pupil_size,fp_id)]
dygraph(DT_Plot) %>%
  # dySeries("pupilPosX", color = "#ff9999") %>%
  # dySeries("pupilPosY", color = "#99fff3") %>%
  # dySeries("pupilPosZ", color = "#ad99ff") %>%
  dySeries("evt", color = "#c44e39") %>%
  dySeries("lux", color = "#ffa500") %>%
  dySeries("pupil_size", color = "#3ac44a") %>%
  dySeries("fp_id", color = "#5c5c5c") %>%
  dyOptions(pointSize = 5) %>%
  dyRangeSelector(height = 20)

## Convert to long format for plotting
DT_long <- melt(DT, id = "sample")

## Simple Plot of Values
myPlot <-
  ggplot(DT_long, aes(sample, value, color = variable)) +
  geom_point()
## + xlim(400,3500) + ylim(0,17)

## Create Interactive Plot
ggplotly(myPlot)


fileToPlot = "/media/yurikleb/Yuri_IDE_07477204021/DesignLab/CV/ExperimentData/MAIN/2018_04_12_Sunny/Christian/recorder_data/Fused_Data.csv"
DT = fread(fileToPlot)

########### PART2 #############
## Converting to groups
range_var <- 10

## find all non-NA evt
indx <- DT[!is.na(evt), .(sample = sample - 1, evt)]

## matrix of indx + range_var
mat <- data.table(mapply(`:`, indx$sample, indx$sample + range_var - 1))
# setnames(mat, as.character(indx$evt))
setnames(mat, paste0(as.character(indx$evt), "_", seq_along(indx$evt)))
mat[, indx := .I] 

# melting
# long_mat <- melt(mat, variable.factor = FALSE)
long_mat <- melt(mat, variable.factor = FALSE, id = "indx")[, `:=`(indx = NULL, variable = sub("_.*", "", variable))]
#levels(long_mat$variable) <- levels(long_mat$variable)

# Adding pupil
long_mat[, pupil_size := DT[long_mat$value, pupil_size]]

# validating
long_mat[, .N, by = variable]

# creating groups of range_var
long_mat[, grp := (0:(.N - 1)) %/% range_var]

#validating
long_mat[, .N, by = .(variable, grp)]

# Assiging sample range
long_mat[, sample := 1:range_var]

#renaming variable to evt
names(long_mat)[1] <- "evt"

wide_mat <- dcast(long_mat)

#plotting
myPlot2 <- 
  ggplot(long_mat, aes(sample, pupil_size, color = evt)) + 
  geom_point(alpha = 0.5) +
  geom_smooth()

ggplotly(myPlot2)


