library(prophet)
library(quantmod)
library(data.table)
library(shiny)



fluidPage(
  titlePanel("Playing with Prophet on Financial Time Series (II)"),
  fluidRow(
    column(3, wellPanel(
      h3("\"Prediction is very difficult, especially about the future.\""), 
      helpText("Prophet is a procedure for forecasting time series data developed by Facebook's Core Data Science team."),
      helpText("Using this app you can compare de Prophet prediction for financial time series (from Yahoo Finance) with the real prices"),
      helpText("You can choose the initial date for the train period (ending December 30th, 2016). We forecast price for June 23rd, 2017 (Green color same direction, red color different)."),
      dateInput("date", "Initial Date:", "2014-01-01", max="2020-02-21"),
      textInput("sym", "Symbol (Yahoo Finance!)", "AAPL"),
      helpText("Nice Examples: TLT (4 years), AMZN (5), BND (3)"),
      helpText("Ugly Examples: XOM (3 years), CVX (4), NKE (5)"),
      checkboxInput("seasonal","Use yearly seasonal factor:", TRUE),
      h3("Links"),
      p(tags$a(href="https://mydata.shinyapps.io/ShinyProphetV2/", "Playing with Prophet on Financial Time Series")),
      p(tags$a(href="https://research.fb.com/prophet-forecasting-at-scale", "Research Facebook Prophet")),
      p(tags$a(href="https://facebookincubator.github.io/prophet", "Github")),
      p(tags$a(href="https://cran.r-project.org/web/packages/prophet/index.html", "Prophet R Package")),
      helpText("Data from Yahoo Finance!")
    )),
    column(6,
           plotOutput("plot1", width = "1217px", height = "800px")
    )
  )
)