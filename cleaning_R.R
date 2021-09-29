filename = list.files('/Users/jiahuiwu/Desktop/501/portfolio/cleaned data', pattern=NULL, all.files=FALSE,full.names=FALSE)

library(stringr)
yellow_list = filename[str_detect(filename, "yellow")]
green_list = filename[str_detect(filename, "green")]
fhv_list = filename[str_detect(filename, "fhv")]
HV_list = filename[str_detect(filename, "HV")]
count_length = function(file_name){
  path = paste('/Users/jiahuiwu/Desktop/501/portfolio/cleaned data/',file_name,sep = '')
  Nrow = length(count.fields(path))
  return(Nrow)
}

yellow_length = c()
for(name in yellow_list){
  count = count_length(name)
  yellow_length = c(yellow_length,count)
}

green_length = c()
for(name in green_list){
  count = count_length(name)
  green_length = c(green_length,count)
}

fhv_length = c()
for(name in fhv_list){
  count = count_length(name)
  fhv_length = c(fhv_length,count)
}

HV_length = c()
for(name in HV_list){
  count = count_length(name)
  HV_length = c(HV_length,count)
}

fhv_length = c(rep(0,length(yellow_length)-length(fhv_length)),fhv_length)
fhv_length[(length(fhv_length)-22):length(fhv_length)] = fhv_length[(length(fhv_length)-22):length(fhv_length)] + HV_length

date_list = seq(as.Date("2014-01-01"), as.Date("2020-12-01"), by = "months")
date_list = format(as.Date(date_list), "%Y-%m")


library(ggplot2)
df = data.frame(date_list, yellow_length,green_length,fhv_length)
PLOT = ggplot(data = df, aes(x=1:length(yellow_length), y=yellow_length)) + 
  geom_line(col = 'orange') + 
  scale_x_continuous(name = 'date', breaks = seq(1,length(yellow_length),by = 4), labels = date_list[seq(1,length(yellow_length),by = 4)]) +
  theme(axis.text.x = element_text(color = "#993333", size = 8, angle = 45)) + 
  scale_y_continuous(name = 'Number of Service', breaks = seq(0,80000,by = 10000), labels = c('0','3e+06','6e+06','9e+06','12e+06','15e+06','18e+06','21e+06','24e+06')) + 
  
  geom_line(aes(y = green_length, color = 'green taxi'), col = 'green') +
  
  geom_line(aes(y = fhv_length, color = 'fhv & HV'),col='blue') +
  
  geom_label(
    label='yellow taxi', 
    x=80,
    y=8000,
    label.padding = unit(0.55, "lines"), 
    label.size = 0.35,
    color = "black",
  ) +
  geom_label(
    label='green taxi', 
    x=70,
    y=5000,
    label.padding = unit(0.55, "lines"), 
    label.size = 0.35,
    color = "black",
  ) +
  geom_label(
    label='fhv & HV', 
    x=84,
    y=50000,
    label.padding = unit(0.55, "lines"), 
    label.size = 0.35,
    color = "black",
  ) 
PLOT
  





