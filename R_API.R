library("httr")
library("jsonlite")
library("xml2")

base <- "https://www.airnowapi.org/aq/forecast/zipCode/"

format<-"text/csv"
zipCode="10005"
datelist = seq.Date(from = as.Date("2015/01/01",format = "%Y/%m/%d"), by = "day", length.out = 500)
API_KEY="C215BB18-B06D-4E3C-B273-08AFA3D6A51B"
distance="25"

AirDF = data.frame()
for(i in c(1:length(datelist))){
  date = datelist[i]
  call1 <- paste(base,"?",
                 "format", "=", format, "&",
                 "zipCode", "=", zipCode, "&",
                 "date", "=", date,"&",
                 "distance", "=", distance,"&",
                 "API_KEY", "=", API_KEY, 
                 sep="")
  AirNowAPI_Call<-httr::GET(call1)
  MYDF<-httr::content(AirNowAPI_Call)
  AirDF = rbind(AirDF,MYDF)
}

## Print to a file
AirName = "AirFileExample.csv"
## Start the file
AirFile <- file(AirName)
## Write Tweets to file
write.csv(AirDF,AirFile, row.names = FALSE)