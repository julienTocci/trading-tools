fluidPage(
  titlePanel("Playing with Prophet on Financial Time Series"),
  fluidRow(
    column(3, wellPanel(
      h3("Prophet: Automatic Forecasting Procedure"), 
      sliderInput("lookback", "Train window size (months):", min = 12, max = 60, value = 36, step = 1),
      sliderInput("forward", "Forecast window size (months):", min = 1, max = 12, value = 6, step = 1),
      textInput("sym", "Symbol (Yahoo Finance!)", "FB"),
      checkboxInput("seasonal","Add yearly seasonal factor:", FALSE)
    )),
    column(6,
           plotOutput("plot1", width = 1200, height = 900)
    )
  )
)