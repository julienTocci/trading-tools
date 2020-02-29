library(prophet)
library(quantmod)
library(data.table)
library(ggplot2)
library(dplyr)

# Used for backtesting Prophet prediction strategy (comparing what prophet says and the actual data)

function(input, output) {
  output$plot1 <- renderPlot({
    
    endtraining <- "2019-02-20"
    Sys.setenv(TZ='GMT')
    lastdatapoint <- Sys.Date() 
    
    # "to" end of the training period
    mydf <- getSymbols(input$sym, src = "yahoo",  to = endtraining,  from = input$date,  auto.assign = FALSE)
    
    mydf <- data.frame(mydf[,6])
    setDT(mydf, keep.rownames = TRUE)
    colnames(mydf) <- c("ds", "y")
    
    # Train from starting date to endtraining
    m <- prophet(mydf, yearly.seasonality = input$seasonal, weekly.seasonality = FALSE)
    future <- make_future_dataframe(m, periods = difftime(lastdatapoint ,endtraining , units = c("days"))
)
    forecast <- predict(m, future)
    
    
    # This can be used to compare forecast with the real data 
    mydf2 <- getSymbols(input$sym, src = "yahoo",  from = input$date,  auto.assign = FALSE)
    
    mydf2 <- data.frame(mydf2[,6])
    colnames(mydf2) <- "Price"
    mydf2$ds <- rownames(mydf2)
    rownames(mydf2) <- NULL
    mydf2$ds <- as.Date(as.POSIXct(mydf2$ds, tz='GMT'))
    forecast$ds <- as.Date(forecast$ds)

    perry = left_join(mydf2, forecast, by="ds")
    rownames(perry) <- perry$ds
    perry$PriceX <- perry$Price
    
    # Date from which we start forecasting
    perry$Price[perry$ds > endtraining] = NA
    
    perry$PriceX[perry$ds < endtraining] = NA
    
    dput(perry$yhat)
    # Last price of the training period
    priceref = perry$Price[perry$ds == endtraining]
    yhatend = tail(perry$yhat,1)
    priceend = tail(perry$PriceX,1)
    
    dput(priceref)
    dput(yhatend)
    dput(priceend)
    theme_set(theme_gray(base_size = 18))
    
    
    # Change last price of the training period here
    if (((yhatend>priceref) && (priceend>priceref)) | ((yhatend<priceref) && (priceend<priceref))) {
      ggplot(perry, aes(x=ds)) + geom_point(aes(y=Price)) + geom_point(aes(y=PriceX), col="forestgreen", size=3) +
        geom_line(aes(y=yhat)) + geom_ribbon(aes(ymin=yhat_lower, ymax=yhat_upper), fill="deepskyblue", alpha=0.5) +
        geom_line(aes(y=priceref), cex=0.8, col="steelblue4") +
        geom_vline(aes(xintercept=as.numeric(as.Date(endtraining))), cex=0.8, col="steelblue4")}
    else {
      ggplot(perry, aes(x=ds)) + geom_point(aes(y=Price)) + geom_point(aes(y=PriceX), col="firebrick1", size=3) +
        geom_line(aes(y=yhat)) + geom_ribbon(aes(ymin=yhat_lower, ymax=yhat_upper), fill="deepskyblue", alpha=0.5) +
        geom_line(aes(y=priceref), cex=0.8, col="steelblue4") +
        geom_vline(aes(xintercept=as.numeric(as.Date(endtraining))), cex=0.8, col="steelblue4")}
    
  })
}