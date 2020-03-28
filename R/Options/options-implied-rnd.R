library(RND)
library(RQuantLib)
library(quantmod)
library(PerformanceAnalytics)
library(magrittr)
library(purrr)

library(tidyverse)
library(timetk)
library(tidyquant)

library(graphics)

# Trading in options with a wide range of exercise prices and a single maturity allows 
# a researcher to extract the market's risk-neutral density (RND) over the underlying price at expiration.
# The RND: (risk neutral density) contains investors beliefs about the true probabilities blended with their risk 
#preferences, both of which are of great interest to academics and practitioners alike

# # https://cran.r-project.org/web/packages/RND/RND.pdf

getwd()
setwd("C:\\Users\\julien\\Desktop\\projets\\TRADING\\R\\Options")


tradeDateMinusFiveYears  <- "2015-03-28"
currentTradeDate <- "2020-03-28"
maturityDate <- "2020-04-03"
underlyingStock <- "AAPL"
OptionType <- "call"
OptionPrice <- 1.90
optionStrike <- 270.00
# Annualized dividendyield 1.24% exmaple
dividendYield <- 0.0124
dte <- round( as.numeric(difftime(maturityDate,currentTradeDate, units = "days")),0)
timeToOptionsMaturity <- dte/365


################# Compute hitorical volatility, riskfree rate, dividend yield,  get Options data, 
stock <- getSymbols.yahoo( underlyingStock, from=tradeDateMinusFiveYears, auto.assign= F)
VolatilitySlide <- 30
daysInaYear <- 262
historicalvol=volatility(stock,n=VolatilitySlide,N=daysInaYear,calc="close")
chartSeries(historicalvol)
LastVolatility <- historicalvol[length(historicalvol)]

options <- getOptionChain(underlyingStock, maturityDate)
calls <- options$calls
callstrikes <- calls$Strike
callVol <- calls$Vol
callOpenInterest <- calls$OI
callLast <- calls$Last

puts <- options$puts
putstrikes <- puts$Strike
putVol <- puts$Vol
putOpenInterest <- puts$OI
putLast <- puts$Last



getSymbols('DGS10',src = 'FRED', from = tradeDateMinusFiveYears)

DGS10 <- to.monthly(DGS10, indexAt = "last", OHLC = FALSE)
lastDGS10RateValue = coredata(DGS10[length(DGS10)])


############################################################################
#### First let's calculate the theorical price of the options ####

# current aapl volatility
sigma = coredata(LastVolatility)
# risk free rate based on 10 years treasury bonds
r = lastDGS10RateValue/100
# dividend yield of AAPL
y = dividendYield
# 5 DTE 
te = timeToOptionsMaturity
# current price of AAPL
s0 = coredata(last(Cl(stock)))


# Estimates using black & scholes

callStrikeBsm = callstrikes
marketcallBsm = price.bsm.option(r =r, te = te, s0 = s0,
                                    k = callStrikeBsm, sigma = sigma, y = y)$call


putStrikeBsm = putstrikes
marketputBsm = price.bsm.option(r =r, te = te, s0 = s0,
                                   k = putStrikeBsm, sigma = sigma, y = y)$put


extract.bsm.density(r = r, y = y, te = te, s0 = s0, market.calls = marketcallBsm,
                    call.strikes = callStrikeBsm, market.puts = marketputBsm,
                    put.strikes = putStrikeBsm, lambda = 1, hessian.flag = FALSE)


# TODO PLOT FROM OUTPUT OF EXTRAT BSM DENSITY
png("density.png") 

x<- seq(0,10,length = 100)
a <- dlnorm(x, meanlog = 0, sdlog = 1, log = FALSE)
plot(x,a, lty=5, col="blue", lwd=3)
print("done")
dev.off()
browseURL("density.png") 




#Use the ouput value to check
# https://homepage.divms.uiowa.edu/~mbognar/applets/lognormal.html


# IV for a specific call price
IV = AmericanOptionImpliedVolatility(type=OptionType, value=OptionPrice, underlying=s0,
                                     strike=optionStrike, dividendYield=y, riskFreeRate=r,
                                     maturity=te, volatility=sigma)


# Estimate using mixutre of lognormals
#extract.am.density(initial.values = rep(NA, 10), r, te, s0, market.calls,
#                   calls = 1, puts, put.weights = 1, strikes, lambda = 1,
#                   hessian.flag = F, cl = list(maxit = 10000))

########################################################################################


##############################################################################################
#### We can extract the rnd based of all models available in the package in a pdf ####
# Get current directory


# MOE function extracts the risk neutral density based on all models and summarizes the results.
# takes few minutes
# See documentation explanation for detail

# https://books.google.fr/books?id=JgGhLWbl3hAC&pg=PA393&lpg=PA393&dq=penalty+parameter+martingale+condition&source=bl&ots=4vhYds_gJp&sig=ACfU3U317BfoMIqtdLQOeCrcOCSz51ITmg&hl=fr&sa=X&ved=2ahUKEwi06YXIr67oAhXJzoUKHV6WAkIQ6AEwAHoECAcQAQ#v=onepage&q=penalty%20parameter%20martingale%20condition&f=false
# Necessary for the density to be risk neutral
# https://en.wikipedia.org/wiki/Penalty_method

#martingale_factor = 100
martingale_factor = 1


callStrikeBsm = seq(from = 200, to = 400, by = 5)
marketcallBsm = price.bsm.option(r =r, te = te, s0 = s0,
                                    k = callStrikeBsm, sigma = sigma, y = y)$call
putStrikeBsm = seq(from = 200, to = 400, by = 5)
marketputBsm = price.bsm.option(r =r, te = te, s0 = s0,
                                   k = putStrikeBsm, sigma = sigma, y = y)$put



# TODO USE 
# https://github.com/cran/RND/blob/master/R/MOE.R

MOE(marketcallBsm, callStrikeBsm, marketputBsm, putStrikeBsm, call.weights = 1,
    put.weights = 1, lambda = martingale_factor, s0=s0, r=r , te=te, y=y, file.name ="summary")
    

##################################################################################################



# The predicted price's difference with actual market calculated by objectives should be very small  (prouving that bsm is working)
r = 0.05
te = 60/365
s0 = 1000
sigma = 0.25
y = 0.01
call.strikes = seq(from = 500, to = 1500, by = 25)
# market calls contains the theorical value of a call actions
market.calls = price.bsm.option(r =r, te = te, s0 = s0,
                                k = call.strikes, sigma = sigma, y = y)$call
put.strikes = seq(from = 510, to = 1500, by = 25)
# market puts contains the theorical value of a put actions
market.puts = price.bsm.option(r =r, te = te, s0 = s0,
                               k = put.strikes, sigma = sigma, y = y)$put
###
### perfect initial values under BSM framework
###
mu.0 = log(s0) + ( r - y - 0.5 * sigma^2) * te
zeta.0 = sigma * sqrt(te)
mu.0
zeta.0
###
### The objective function should be *very* small
###
bsm.obj.val = bsm.objective(theta=c(mu.0, zeta.0), r = r, y=y, te = te, s0 = s0,
                            market.calls = market.calls, call.strikes = call.strikes,
                            market.puts = market.puts, put.strikes = put.strikes, lambda = 1)
bsm.obj.val
