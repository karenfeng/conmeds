#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)

# Define UI for application that draws a histogram
fluidPage(

    # Application title
    titlePanel("Concomitant Medications"),
    tabsetPanel(
      type="tabs",
      tabPanel(
        "Cohort",
        sidebarLayout(
          sidebarPanel(
            selectInput(
              "hierarchy",
              "Classification",
              c(
                "System action" = "ATC1-4",
                "Contraindicated with" = "DISEASE_ci_with",
                "Pharmacologic action" = "MESHPA")),
          ),
          mainPanel(
            tableOutput("cohort_hierarchy")
          )
        )
      ),
      tabPanel(
        "Patient",
        sidebarLayout(
          sidebarPanel(
            textInput("participant_id", label = "Participant ID", value = "1"),
            textInput("reaction", label = "Reaction", value = "")
          ),
          mainPanel(
            tableOutput("pt_boxed_warnings"),
            tableOutput("pt_adverse_reactions"),
            tableOutput("pt_induced_disease")
          )
        )
      )
    )
)
