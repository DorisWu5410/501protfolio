install.packages("arulesViz")
library(arules)
install.packages("devtools")
devtools::install_github("mhahsler/arulesViz")
install.packages("arulesViz")
library(arulesViz)

library(igraph)
library(visNetwork)
library(networkD3)
#data(MisLinks, MisNodes)
library(igraph)
#https://dplyr.tidyverse.org/reference/mutate.html
library(dplyr)
## for pipes %>%
library(magrittr)


detach("package:arulesViz", unload=TRUE)
detach("package:arules", unload=TRUE)
library(arules)
library(arulesViz) 

library(plotly)
ARM_data = read.transactions('/Users/jiahuiwu/Desktop/501/portfolio/ARM.csv',format = "basket",header = FALSE, sep = ',')
inspect(ARM_data[1:100])

ARM = arules::apriori(ARM_data, parameter = list(supp=0.01, conf=0.1, 
                                                 maxlen=30, 
                                                 minlen=2,
                                                 target= "rules"),
                      appearance = list(lhs = grep("00:00", itemLabels(ARM_data), value = TRUE),
                                        rhs = itemLabels(ARM_data)[! itemLabels(ARM_data)  %in% grep("00:00", itemLabels(ARM_data),value = TRUE)]))

summary(ARM)

ARM = sort(ARM,by = 'confidence')
inspect(ARM)

plot(ARM, method = 'graph',engine = "htmlwidget", 
     control=list(itemLabels = TRUE, recorder = TRUE, max = 1000), 
     measure = "confidence", arrowSize = 0.2, measureLabels = TRUE,
      cex = 0.5)

plot(ARM, method = 'graph',engine = "igraph", 
     control=list(itemLabels = TRUE, recorder = TRUE, max = 50,measure = 'confidence'), 
     arrowSize = 0.2, size = .1, measure = 'confidence', alpha = .4, col = FALSE,
     cex = 0.7)

plot(ARM)

df = DATAFRAME(ARM)
write.csv(df,'ARM_rule.csv')
