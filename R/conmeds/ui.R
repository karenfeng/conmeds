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
        "Summary statistics",
        plotOutput("num_conmeds")),
      tabPanel(
        "Classification summary",
        sidebarLayout(
          sidebarPanel(
            selectInput(
              "hierarchy",
              "Classification",
              c(
                "System action" = "ATC1-4",
                "Contraindicated with" = "DISEASE_ci_with",
                "Pharmacologic action" = "MESHPA",
                "Mechanism of action" = "MOA_has_moa",
                "Established pharmaceutical class" = "EPC_has_epc",
                "Adverse reactions" = "adverse_reactions",
                "Boxed warnings" = "boxed_warnings")),
            textInput("cohort_search", label = "Search", value = "")
          ),
          mainPanel(
            tableOutput("cohort_hierarchy")
          )
        )
      ),
      tabPanel(
        "Patient lookup",
        sidebarLayout(
          sidebarPanel(
            uiOutput("pt_select"),
            textInput("pt_search", label = "Search", value = "")
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
