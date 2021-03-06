## Packages
library(dygraphs)
library(data.table)
library(ggplot2)
library(plotly)

## List the files in the folder <---- INSERT THE CORRECT PATH OF THE FILES!
Path <- "/home/yurikleb/Desktop/Experiment_Data/MAIN/2018_05_29/Onur_Images"
(f <- list.files(Path, full.names = TRUE, pattern = "\\.csv"))

## Read all the files into a list
l <- lapply(f, fread)

# Merge all the files into a data.table
DT <- Reduce(function(...) merge(..., by = "V1", all = TRUE), l)
setnames(DT, c("sample", gsub(".*_(.*).csv", "\\1", f)))

## draw dygraph
dygraph(DT) %>%
  dySeries("evt", color = "#c44e39") %>%
  dySeries("lux", color = "#ffa500") %>%
  dySeries("pupil", color = "#3ac44a") %>%
  dyOptions(pointSize = 5) %>%
  dyRangeSelector(height = 20)

# ## Convert to long format for plotting
# DT_long <- melt(DT, id = "sample")
# 
# ## Simple Plot of Values
# myPlot <-
#   ggplot(DT_long, aes(sample, value, color = variable)) +
#   geom_point()
# ## + xlim(400,3500) + ylim(0,17)
# 
# ## Create Interactive Plot
# ggplotly(myPlot)


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


