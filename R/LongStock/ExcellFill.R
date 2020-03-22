args <- commandArgs(trailingOnly = TRUE)
symbol <- args[1]
start <- args[2]

print(symbol)

library(quantmod)
df <- getSymbols(symbol, from=start, auto.assign = FALSE)
write.csv(df, paste("C:/Users/julien/Desktop/projets/TRADING/R/excellStocks/",symbol,".csv", sep=""))