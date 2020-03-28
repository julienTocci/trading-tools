library(RND)
library(RQuantLib)
library(quantmod)
library(PerformanceAnalytics)
library(magrittr)
library(purrr)

library(tidyverse)
library(timetk)
library(tidyquant)

# CAPM
tradeDateMinusFiveYears  <- "2015-03-28"
currentTradeDate <- "2020-03-28"
underlyingStock<- "AAPL"


#Our stock rate
# from https://rviews.rstudio.com/2018/02/08/capm-beta/
prices <- 
  getSymbols(underlyingStock, src = 'yahoo', 
             from=tradeDateMinusFiveYears,
             auto.assign = TRUE, warnings = FALSE) %>% 
  map(~Ad(get(.))) %>%
  reduce(merge) %>% 
  `colnames<-`(underlyingStock)
prices_monthly <- to.monthly(prices, indexAt = "last", OHLC = FALSE)
#prices_daily <- to.monthly(prices, indexAt = "last", OHLC = FALSE)


asset_returns_xts <- na.omit(Return.calculate(prices_monthly, method = "log"))

# S&P500 rate
#mkt <- getSymbols("^GSPC",auto.assign = FALSE, from = "1980-01-01")
spy_monthly_xts <- 
  getSymbols("SPY", 
             src = 'yahoo', 
             from = tradeDateMinusFiveYears,
             auto.assign = TRUE, 
             warnings = FALSE) %>% 
  map(~Ad(get(.))) %>% 
  reduce(merge) %>%
  'colnames<-'("SPY") %>% 
  to.monthly(indexAt = "last", OHLC = FALSE)

market_returns_xts <-
  Return.calculate(spy_monthly_xts, method = "log") %>% 
  na.omit()


# CAPM
#getSymbols('DGS3MO',src = 'FRED')
# 10 Year US treasury bond rate

getSymbols('DGS10',src = 'FRED', from = tradeDateMinusFiveYears)

DGS10 <- to.monthly(DGS10, indexAt = "last", OHLC = FALSE)


beta <- CAPM.beta(asset_returns_xts, market_returns_xts)


lastDGS10RateValue = coredata(DGS10[length(DGS10)])
lastMarketRateValue = coredata(market_returns_xts[length(market_returns_xts)])

print("Make sure that the last data of both currentMarketRate and DGS10 have the samedate and that the date is not too far!!!")
print ("If this is thecase, consider changing the tradingdate")

marketRiskpremium = lastMarketRateValue-lastDGS10RateValue

stockExpectedReturn = lastDGS10RateValue + beta*(marketRiskpremium)
