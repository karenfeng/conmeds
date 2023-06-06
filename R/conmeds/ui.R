# Author: Karen Feng

if (!require("shiny")) {
  install.packages("shiny", repos='http://cran.us.r-project.org')
}
if (!require("DT")) {
  install.packages("DT", repos='http://cran.us.r-project.org')
}

library(shiny)
library(DT)

# Define UI for application that draws a histogram
fluidPage(

    # Application title
    titlePanel("Concomitant Medications"),
    tabsetPanel(
      type="tabs",
      tabPanel(
        "Summary statistics",
        plotOutput("num_conmeds"),
        dataTableOutput("common_drugs")),
      tabPanel(
        "Classification summary",
        sidebarLayout(
          sidebarPanel(
            radioButtons(
              "hierarchy",
              "Classification",
              c(
                "Contraindicated with" = "DISEASE_ci_with",
                "Pharmacologic action" = "MESHPA",
                "Pharmacokinetics" = "PK_has_pk",
                "Therapeutic role" = "DISEASE_may_treat",
                "Adverse reactions" = "adverse_reactions",
                "Boxed warnings" = "boxed_warnings")),
            width=3
          ),
          mainPanel(
            br(),
            uiOutput("hierarchy_blurb"),
            br(),
            dataTableOutput("cohort_hierarchy"),
            width=9
          )
        )
      ),
      tabPanel(
        "Patient lookup",
        sidebarLayout(
          sidebarPanel(
            dataTableOutput("pt_list"),
            width=4),
          mainPanel(
            br(),
            p("Concomitant medications taken by the patient."),
            dataTableOutput("pt_drugs"),
            br(),
            p(paste0(
              "Boxed warnings from FDA structured product labels extracted ",
              "via OnSides. Ranked by average CTCAE severity.")),
            dataTableOutput("pt_boxed_warnings"),
            br(),
            p(paste0(
              "Adverse reactions from FDA structured product labels extracted ",
              "via OnSides. Ranked by average CTCAE severity.")),
            dataTableOutput("pt_adverse_reactions"),
            width=8
          )
        )
      )
    )
)
