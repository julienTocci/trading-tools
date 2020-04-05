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


tradeDateMinusFiveYears  <- "2015-04-04"
currentTradeDate <- "2020-04-04"
maturityDate <- "2020-05-01"
underlyingStock <- "UBER"
OptionType <- "call"
OptionPrice <- 1.90
optionStrike <- 280.00
# Annualized dividendyield 1.24% exmaple
#dividendYield <- 0.0124
dividendYield <- 0.0124
dte <- round( as.numeric(difftime(maturityDate,currentTradeDate, units = "days")),0)
timeToOptionsMaturity <- dte/365

# Creating or using a directory specific for this Options study and date
# e.g  APPL\\2020-03-29
stockDir = paste("C:\\Users\\julien\\Desktop\\projets\\TRADING\\R\\Options\\RND-data\\",underlyingStock, sep = "")
dir.create(stockDir, showWarnings = FALSE)
setwd(stockDir)
stockDirDate = paste(stockDir,maturityDate,  sep = "\\")
dir.create(stockDirDate, showWarnings = FALSE)
setwd(stockDirDate)


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


# get.point.estimate estimates the risk neutral density by center differentiation.
# It basically does a non parametric estimation of the rnd
point.obj = get.point.estimate(market.calls = callstrikes, call.strikes = putstrikes, r = r , te = te)
y.point   = point.obj


# https://books.google.fr/books?id=JgGhLWbl3hAC&pg=PA393&lpg=PA393&dq=penalty+parameter+martingale+condition&source=bl&ots=4vhYds_gJp&sig=ACfU3U317BfoMIqtdLQOeCrcOCSz51ITmg&hl=fr&sa=X&ved=2ahUKEwi06YXIr67oAhXJzoUKHV6WAkIQ6AEwAHoECAcQAQ#v=onepage&q=penalty%20parameter%20martingale%20condition&f=false
# Necessary for the density to be risk neutral
# https://en.wikipedia.org/wiki/Penalty_method
#martingale_factor = 100
martingale_factor = 1



#################### BSM ESTIMATE ##################
# Estimates using black & scholes
realCallstrikes = callstrikes
realCallPrices = callLast
# European style pricing estimation
ComputedBsmCallsPrices = price.bsm.option(r =r, te = te, s0 = s0,
                                 k = realCallstrikes, sigma = sigma, y = y)$call


realPutstrikes = putstrikes
realPutPrices = putLast
# European style pricing estimation
ComputedBsmPutsPrices = price.bsm.option(r =r, te = te, s0 = s0,
                                k = realPutstrikes, sigma = sigma, y = y)$put

# Estimate RND using BSM model on the value froms the market.
bsm.obj = extract.bsm.density(r = r, y = y, te = te, s0 = s0, market.calls = realCallPrices,
                    call.strikes = realCallstrikes, market.puts = realPutPrices,
                    put.strikes = realPutstrikes, lambda = martingale_factor, hessian.flag = FALSE)

# Extracting computed density parameters of the BSM model on real data
bsm.mu   = bsm.obj$mu
bsm.zeta = bsm.obj$zeta

# Range
min.x = min(realPutstrikes, realCallstrikes)
max.x = max(realPutstrikes, realCallstrikes)

# Creating  the simple log normal distribution from the BSM model(BSM)
x         = seq(from = min.x, to = max.x, length.out = 10000)
y.bsm     = dlnorm(x = x, meanlog = bsm.mu, sdlog = bsm.zeta, log = FALSE)

# Output PDF
pdf(file = paste("densityBSM.pdf",sep=""), width = 7 * 1.6, height = 7)

# Graphical adjustment, not important
max.y = max(y.bsm)*1.05
if ( !is.numeric(max.y) ) max.y = 1
cut.off = (min(x) + max(x))/2 
max.ind = which.max(y.bsm)
if (x[max.ind] > cut.off) legend.location = "topleft" else legend.location = "topright"

# Plot the BSM rnd
par(mar=c(5,5,5,5))
plot(y.bsm ~ x, type="l", col="black", xlab="Strikes", ylab="Density", main="Single LNorm BSM", 
     ylim=c(0,max.y), lwd=2, lty=1, cex.axis = 1.25, cex.lab = 1.25)
abline(v=x[which.max(y.bsm)], col="red")
axis(1, at=x[which.max(y.bsm)],labels=x[which.max(y.bsm)],mgp = c(10, 2, 0))

# Extracting Volatility from the computed BSM model's RND
# Removing the sqrt(te) from the price.bsm.option
bsm.sigma = bsm.zeta/sqrt(te)

# Predict prices using the IV of the BSM pricing model
bsm.predicted.puts  = price.bsm.option(r = r, te = te, s0 = s0, k = realPutstrikes,  sigma = bsm.sigma, y = y)$put
bsm.predicted.calls = price.bsm.option(r = r, te = te, s0 = s0, k = realCallstrikes, sigma = bsm.sigma, y = y)$call   

# Getting the linear regression of the predicted values for calls and strikes
bsm.res.calls = mean(abs(lm(bsm.predicted.calls ~ ComputedBsmCallsPrices)$res))
bsm.res.puts  = mean(abs(lm(bsm.predicted.puts  ~ ComputedBsmPutsPrices)$res))

par(mfrow=c(1,2), mar=c(7,5,7,5))
plot(bsm.predicted.calls ~ ComputedBsmCallsPrices, ylab="Predicted", xlab = "Computed Market Price", main=paste("Single LNorm, Calls, ","mean|res| = ",round(bsm.res.calls,3)),
     cex.axis = 1.25, cex.lab = 1.25)
abline(a=0,b=1, col="red")
plot(bsm.predicted.puts  ~ ComputedBsmPutsPrices,  ylab="Predicted", xlab = "Computed Market Price", main=paste("Single LNorm, Puts, ","mean|res| = ",round(bsm.res.puts,3)),
     cex.axis = 1.25, cex.lab = 1.25)
abline(a=0,b=1, col="red")
par(mfrow=c(1,1))


plot(NA, xlim=c(0,10), ylim=c(0,10), bty='n',
     xaxt='n', yaxt='n', xlab='', ylab='')
text(1,4,"When the points are below the red line: The market price are overpriced else they are underpriced", pos=4)


tmp.data.calls = cbind(realCallPrices,realCallstrikes, bsm.predicted.calls)
colnames(tmp.data.calls) = c("marketcalls","strikes", "bsm")
data.calls = as.data.frame(tmp.data.calls)
write.table(data.calls, file = paste("calls.csv", sep=""), sep = ",", col.names = T, row.names = F)

tmp.data.puts = cbind(realPutPrices,realPutstrikes, bsm.predicted.puts)
colnames(tmp.data.calls) = c("marketputs","strikes", "bsm")
data.puts = as.data.frame(tmp.data.puts)
write.table(data.puts, file = paste("puts.csv", sep=""), sep = ",", col.names = T, row.names = F)




# Calculating Asymetry/skewness Perception
densityMaxX = x[which.max(y.bsm)]
asymetryPerception = mean(x >= densityMaxX)* 100

densityMaxX
asymetryPerception

print("### Asymmetry perception")
print("### It is needed to have a lot of option volume to have meaningfull data")
print("### The asymetryPerceptionDelta is equal to the % difference between |p(x < expected) - p(x>expected)|")
print("### If the asymmetry Perception delta is low: It would reflect a more balanced expected future values by the market actors of the underlying asset value evolution")
print("### If the asymmetry perception delta is high , it means that there is a strong trend to think the underlying is going to be higher or lesser than the most expected value")
print("### More fear = more asym perception = more risk. The fear of asymmetry increases with market volatility")
asymetryPerceptionDelta = asymetryPerception -50
if (asymetryPerception>0){
  print(paste("The market thinks that the stock price will exceed its most expected value: ",densityMaxX,  "the asymetry Perception factor is: ",asymetryPerceptionDelta, "%" ))
  print("The market is biaised over the underlying future value being more than the most expected value")
}else{
  print(paste("The market thinks that the stock price will be less than its most expected value: ",densityMaxX,  "the asymetry Perception factor is: ",asymetryPerceptionDelta, "%" ))
  print("The market is biaised over the underlying future value being less than the most expected value")  
}

# Asymmetry Perception ("Future values")
print("Large change in the asymmetry perception Delta indicates that the expectations shifted due to a fundamental or non-fundamental reason")
futurOptions <- getOptionChain(underlyingStock, NULL)
asymetryPerceptionDeltaArray <- c()
maturityArray <- names(futurOptions)


for(i in futurOptions){
  # Estimates using black & scholes
  realCallstrikesI = i$calls$Strike
  realCallPricesI = i$calls$Last
  # European style pricing estimation
  ComputedBsmCallsPricesI = price.bsm.option(r =r, te = te, s0 = s0,
                                            k = realCallstrikesI, sigma = sigma, y = y)$call
  
  
  realPutstrikesI = i$puts$Strike
  realPutPricesI = i$puts$Last
  # European style pricing estimation
  ComputedBsmPutsPricesI = price.bsm.option(r =r, te = te, s0 = s0,
                                           k = realPutstrikesI, sigma = sigma, y = y)$put
  
  # Estimate RND using BSM model on the value froms the market.
  bsm.objI = extract.bsm.density(r = r, y = y, te = te, s0 = s0, market.calls = realCallPricesI,
                                call.strikes = realCallstrikesI, market.puts = realPutPricesI,
                                put.strikes = realPutstrikesI, lambda = martingale_factor, hessian.flag = FALSE)
  
  # Extracting computed density parameters of the BSM model on real data
  bsm.muI   = bsm.objI$mu
  bsm.zetaI = bsm.objI$zeta
  
  # Range
  min.xI = min(realPutstrikesI, realCallstrikesI)
  max.xI = max(realPutstrikesI, realCallstrikesI)
  
  # Creating  the simple log normal distribution from the BSM model(BSM)
  xI         = seq(from = min.xI, to = max.xI, length.out = 10000)
  y.bsmI     = dlnorm(x = xI, meanlog = bsm.muI, sdlog = bsm.zetaI, log = FALSE)
  
  
  densityMaxXI = xI[which.max(y.bsmI)]
  asymetryPerceptionI = mean(xI > densityMaxXI)* 100
  
  # Extracting computed density parameters of the BSM model on real data
  asymetryPerceptionDeltaI = asymetryPerceptionI -50
  
  asymetryPerceptionDeltaArray[length(asymetryPerceptionDeltaArray)+1] = asymetryPerceptionDeltaI
}
par(cex.axis=0.5, cex.lab=1, cex.main=1.2, cex.sub=2)
plot(asymetryPerceptionDeltaArray, type="l", xaxt='n', col="black", xlab="Maturity", ylab="Asym Perc Delta", main="Future Asym Perc Delta",)
axis(1, at=c(1:length(maturityArray)), labels=maturityArray)


plot(NA, xlim=c(0,10), ylim=c(0,10), bty='n',
     xaxt='n', yaxt='n', xlab='', ylab='')
text(1,4,"The Future Asym Perception delta graph shows for every futur maturity: 
the asymmetry perception delta. A positive value 
indicates that the market believe that the underlyingstock price will be greater than
the most expected value (see redline first graph). A negative value means 
that the market believe that the underlying value will be less than the 
most expected value.Large change in the asymmetry perception Delta indicates 
that the expectations shifted due to a fundamental or non-fundamental reason. 
It is needed to have a big option volume to have meaningful data. 
The asymetryPerceptionDelta is equal to the % difference between
|p(x < expected) - p(x>expected)|. 
Generally, More fear = more asym perception = more risk = higher premium. 
The fear of asymmetry increases with market volatility.
Asymetry Delta seems to be more positive the farthest the maturity. Meaning investors are 
in general SEEMS confident that the underlying will surpass the expected values.
The belief factor explains more variation in the risk-neutral skewness than the risk-based factor", pos=4)
#########################################" ########


dev.off()

# IV for a specific call price
#IV = AmericanOptionImpliedVolatility(type=OptionType, value=OptionPrice, underlying=s0,
#                                     strike=optionStrike, dividendYield=y, riskFreeRate=r,
#                                     maturity=te, volatility=sigma)



# The predicted price's difference with actual market calculated by objectives should be very small  (prouving that bsm is working)
#r = 0.05
#te = 60/365
#s0 = 1000
#sigma = 0.25
#y = 0.01
#call.strikes = seq(from = 500, to = 1500, by = 25)
# market calls contains the theorical value of a call actions
#market.calls = price.bsm.option(r =r, te = te, s0 = s0,
#                                k = call.strikes, sigma = sigma, y = y)$call
#put.strikes = seq(from = 510, to = 1500, by = 25)
# market puts contains the theorical value of a put actions
#market.puts = price.bsm.option(r =r, te = te, s0 = s0,
#                               k = put.strikes, sigma = sigma, y = y)$put
###
### perfect initial values under BSM framework
###
#mu.0 = log(s0) + ( r - y - 0.5 * sigma^2) * te
#zeta.0 = sigma * sqrt(te)
#mu.0
#zeta.0
###
### The objective function should be *very* small
###
#bsm.obj.val = bsm.objective(theta=c(mu.0, zeta.0), r = r, y=y, te = te, s0 = s0,
#                            market.calls = market.calls, call.strikes = call.strikes,
#                            market.puts = market.puts, put.strikes = put.strikes, lambda = 1)
#bsm.obj.val
