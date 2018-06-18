## Packages
library(dygraphs)
library(data.table)
library(ggplot2)
library(plotly)

options(digits=12)

multimerge = function(mypath, keycol, selcol){
  
  ## List the files in the folder <---- INSERT THE CORRECT PATH OF THE FILES!
  Path <- mypath
  (f <- list.files(Path, full.names = TRUE, pattern = "\\.csv"))
  
  ## Read all the files into a list
  l <- lapply(f, fread, select = selcol)
  # invisible(mapply(function(x, y) setnames(x, 2, y), l, paste0("V", (1:length(l) + 1))))
  
  # Merge all the files into a data.table
  Reduce(function(...) merge(..., by = keycol, all = TRUE), l)
  # setnames(DT, c("sample", gsub(".*_(.*).csv", "\\1", f)))
}

colsFilter <- c("sample", "evt", "lux", "pupil_size")
DT1 = multimerge("/home/yurikleb/Desktop/test_merge/recorder_data", "sample", colsFilter)

colsFilter <- c("timestamp", "fp_id", "fp_duration", "diameter_3d", "index")
DT2 = multimerge("/home/yurikleb/Desktop/test_merge/exports/0-7042/selected", "timestamp", colsFilter)


initialPupil <- DT1[1,pupil_size]
indx <-  which.max(DT2$diameter_3d == initialPupil) - 1
DT2 <- tail(DT2, -indx)

# DT3 <- merge(DT1,DT2, by = "row.names", all=TRUE)
indx <-  min(nrow(DT1), nrow(DT2))
DT3 <- cbind(head(DT1, indx), head(DT2, indx))
DT3
# write.csv(DT1, file = "/home/yurikleb/Desktop/test_merge/recorder_data/merged.csv",row.names=FALSE, na="")



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


