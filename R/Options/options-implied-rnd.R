library(RND)
library(RQuantLib)

# Trading in options with a wide range of exercise prices and a single maturity allows 
# a researcher to extract the market's risk-neutral density (RND) over the underlying price at expiration.
# The RND: (risk neutral density) contains investors’ beliefs about the true probabilities blended with their risk 
#preferences, both of which are of great interest to academics and practitioners alike


# I Printed a document talking about  one's expectations to the true value of RND
# https://www.annualreviews.org/doi/pdf/10.1146/annurev-financial-110217-022944

# # https://cran.r-project.org/web/packages/RND/RND.pdf


###
### You should see that all methods extract the same density!
###

############################################################################
#### First let's calculate the theorical price of options in the range 200-400 ####

# current aapl volatility
sigma = 0.99
# AAPL risk-free rate is 0,92%
r = 0.092
# dividend yield of AAPL
y = 0.01
# 5 DTE 
te = 5/365
# current price of AAPL
s0 = 229.24
# Strike price of the call
k = 250.00	

# Estimates using black & scholes

call.strikes.bsm = seq(from = 200, to = 400, by = 5)
market.calls.bsm = price.bsm.option(r =r, te = te, s0 = s0,
                                    k = call.strikes.bsm, sigma = sigma, y = y)$call
put.strikes.bsm = seq(from = 200, to = 400, by = 5)
market.puts.bsm = price.bsm.option(r =r, te = te, s0 = s0,
                                   k = put.strikes.bsm, sigma = sigma, y = y)$put


# IV for a specific call price
IV = AmericanOptionImpliedVolatility(type="call", value=3.70, underlying=s0,
                                     strike=k, dividendYield=y, riskFreeRate=r,
                                     maturity=te, volatility=sigma)

# IV = 99%

k = 200
# IV for a specific call price
IV = AmericanOptionImpliedVolatility(type="call", value=33, underlying=s0,
                                     strike=k, dividendYield=y, riskFreeRate=r,
                                     maturity=te, volatility=sigma)

# IV = 134%: indeed the premium is very high and indicates that the stock needs consequential movement in order to be ITM


#market.puts.bsm and market.calls.bsm should output the estimated price for every strike price in range 200-400
########################################################################################


##############################################################################################
#### We can extract the rnd based of all models available in the package in a pdf ####
# Get current directory
getwd()
setwd("C:\\Users\\julien\\Desktop\\projets\\TRADING\\R\\Options")

# MOE function extracts the risk neutral density based on all models and summarizes the results.
# takes few minutes
# See documentation explanation for detail

# https://books.google.fr/books?id=JgGhLWbl3hAC&pg=PA393&lpg=PA393&dq=penalty+parameter+martingale+condition&source=bl&ots=4vhYds_gJp&sig=ACfU3U317BfoMIqtdLQOeCrcOCSz51ITmg&hl=fr&sa=X&ved=2ahUKEwi06YXIr67oAhXJzoUKHV6WAkIQ6AEwAHoECAcQAQ#v=onepage&q=penalty%20parameter%20martingale%20condition&f=false
# Necessary for the density to be risk neutral
# https://en.wikipedia.org/wiki/Penalty_method

#martingale_factor = 1
martingale_factor = 100

MOE(market.calls.bsm, call.strikes.bsm, market.puts.bsm, put.strikes.bsm, call.weights = 1,
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
