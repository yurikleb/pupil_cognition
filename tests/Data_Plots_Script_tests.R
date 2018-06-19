## Packages
library(dygraphs)
library(data.table)
library(ggplot2)
library(plotly)

options(digits=12)

mainFilesPath = "/home/yurikleb/Desktop/test_merge/"

multimerge = function(mypath, keycol, selcol){
  
  ##List the files in the folder
  Path <- mypath
  (f <- list.files(Path, full.names = TRUE, pattern = "\\.csv"))
  
  ## Read all the files into a list
  l <- lapply(f, fread, select = selcol)

  # Merge all the files into a data.table
  Reduce(function(...) merge(..., by = keycol, all = TRUE), l)

}


######## Merge all "Recorder App Data" tables
folderPath <- paste(mainFilesPath, "recorder_data/", sep = "")
colsFilter <- c("sample", "evt", "lux", "pupil_size")
DT1 = multimerge(folderPath, "sample", colsFilter)
DT1


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
colsFilter <- c("timestamp", "start_timestamp", "fp_id", "fp_duration", "diameter_3d", "index")
DT2 = multimerge(folderPath, "timestamp", colsFilter)
DT2


# Trim the top extra values from "Pupil Player Data"
# So "Recorder_Data" and "Pupil Player Data" start from the same point in time.
initialPupil <- DT1[1,pupil_size]
indx <-  which.max(DT2$diameter_3d == initialPupil) - 1
DT2 <- tail(DT2, -indx)

# Merge DT1 and DT2
indx <-  min(nrow(DT1), nrow(DT2))
DT3 <- cbind(head(DT1, indx), head(DT2, indx))
DT3

#Save as a  SCV 
fwrite(DT3, file = file.path(mainFilesPath, "Fused_Data.csv"))


## draw dygraph
dygraph(DT1) %>%
  # dySeries("pupilPosX", color = "#ff9999") %>%
  # dySeries("pupilPosY", color = "#99fff3") %>%
  # dySeries("pupilPosZ", color = "#ad99ff") %>%
  dySeries("evt", color = "#c44e39") %>%
  dySeries("lux", color = "#ffa500") %>%
  dySeries("pupil_size", color = "#3ac44a") %>%
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


## Converting to groups
range_var <- 600

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
long_mat[, pupil := DT[long_mat$value, pupil]]

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

#plotting
myPlot2 <- 
  ggplot(long_mat, aes(sample, pupil, color = evt)) + 
  geom_point(alpha = 0.5) +
  geom_smooth()

ggplotly(myPlot2)


