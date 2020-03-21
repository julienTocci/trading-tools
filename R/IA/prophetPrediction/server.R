library(prophet)
library(quantmod)
library(data.table)
function(input, output) {
  output$plot1 <- renderPlot({
    mydf <- getSymbols(input$sym, src = "yahoo", from = Sys.Date()-(input$lookback*30), to = Sys.Date(), auto.assign = FALSE)
    mydf <- data.frame(mydf[,6])
    mydf <- copy(mydf)
    setDT(mydf, keep.rownames = TRUE)
    colnames(mydf)<- c("ds", "y")
    m <- prophet(mydf,yearly.seasonality = input$seasonal, weekly.seasonality = FALSE)
    future <- make_future_dataframe(m, periods = input$forward*30)
    forecast <- predict(m, future)
    plot(m, forecast)
  })
}