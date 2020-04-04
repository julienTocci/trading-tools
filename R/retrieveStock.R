# CTRL+SHIFT+ENTER to execute whole script
# CTRL + SHIFT + S to execute without verbose debug

library(quantmod)
library(PerformanceAnalytics)

dt <- "2017-2-1"

aapl <- getSymbols.yahoo("AAPL", from=dt, auto.assign= F)
aaplClose <- aapl[,6]


# Current AAPL volatility over 30 days period
vClose <- volatility(aapl[,6], n = 30, calc="close")


chartSeries(aapl)


