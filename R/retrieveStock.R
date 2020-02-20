# CTRL+SHIFT+ENTER to execute whole script

library(quantmod)
library(PerformanceAnalytics)

dt <- "2017-2-1"

aapl <- getSymbols.yahoo("AAPL", from=dt, auto.assign= F)
aaplClose <- aapl[,6]



chartSeries(aapl)


