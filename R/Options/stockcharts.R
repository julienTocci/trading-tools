# CTRL+SHIFT+ENTER to execute whole script

library(quantmod)
library(PerformanceAnalytics)



dt <- "2017-03-1"

x <- getSymbols.yahoo("AAPL", from=dt, auto.assign= F)
xopen <- x[,1]
xhigh <- x[,2]
xlow <- x[,3]
xvolume <- x[,5]
xclose <- x[,6]

# https://www.quantmod.com/examples/charting/
# addTRIX(12,26);



chartSeries(x3, TA="addVo();
            addRSI(14);
            addLines(h=c(30,70), on=3);
            addSMA(50,col='blue');
            addSMA(200, col='red');
            addBBands(20);
            addMACD(12, 26, 9);
            addROC(n=31);
            addLines(h=c(0.00), on=5);"
            , type="candles")





