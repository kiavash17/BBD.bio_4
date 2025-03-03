library(shiny)

# Define UI
ui <- fluidPage(
  titlePanel("Simple Shiny App"),
  sidebarLayout(
    sidebarPanel(
      sliderInput("num", "Number of bins:",
                  min = 1, max = 50, value = 10)
    ),
    mainPanel(
      plotOutput("histPlot")
    )
  )
)

# Define server logic
server <- function(input, output) {
  output$histPlot <- renderPlot({
    hist(rnorm(100), breaks = input$num, col = 'blue', border = 'white')
  })
}

# Run the application 
shinyApp(ui = ui, server = server)