#
# This is the server logic of a Shiny web application. You can run the
# application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(tidyverse)
library(here)

set_here()
pwd <- getwd()
setwd("../../output")

rxnorm <- read.csv('rxnorm_cuid.csv')
hierarchy <- read.csv('rxnorm_hierarchy.csv')
on_sides <- read.csv('rxnorm_onsides.csv')

filter_pt_reaction_df <- function(pt_df, reaction_col_name, input) {
  if (!is.null(input$pt_id)) {
    pt_df <- pt_df %>%
      filter(as.character(ID) == as.character(input$pt_id))
  }

  pt_df <- pt_df %>%
    select(as.symbol(reaction_col_name)) %>%
    separate_longer_delim(as.symbol(reaction_col_name), delim=';') %>%
    mutate_all(list(~na_if(.,""))) %>%
    drop_na() %>%
    unique()

  if (input$pt_search != "") {
    pt_reaction <- pt_df[,1]
    pt_relevant <- str_detect(
      pt_reaction, regex(input$pt_search, ignore_case=T)) %>%
      which()
    pt_df <- pt_df %>%
      slice(pt_relevant)
  }

  pt_df
}

function(input, output, session) {
  
  output$pt_boxed_warnings <- renderTable({
    df <- filter_pt_reaction_df(on_sides, "boxed_warnings", input)
    names(df) <- c("Boxed warnings")
    df
  })

  output$pt_adverse_reactions <- renderTable({
    df <- filter_pt_reaction_df(on_sides, "adverse_reactions", input)
    names(df) <- c("Adverse reactions")
    df
  })
  
  output$pt_induced_disease <- renderTable({
    df <- filter_pt_reaction_df(hierarchy, "DISEASE_induces", input)
    names(df) <- c("Induces")
    df
  })
  
  output$cohort_hierarchy <- renderTable({
    hierarchy_file <- paste(
      'rxnorm_cohort_', input$hierarchy, '.csv', sep='')
    df <- read.csv(hierarchy_file, header=F)
    names(df) <- c("Classification", "Frequency")
    if (input$cohort_search != '') {
      cohort_relevant <- sapply(df[,"Classification"], function(x) {
        str_detect(x, regex(input$cohort_search, ignore_case=T))})
      df <- df[cohort_relevant,]
    }
    df
  })
  
  output$pt_select <- renderUI({
    ranking_df <- read.csv('../data/onsides_patient_ranking.csv', header=T)
    selectInput(
      "pt_id",
      "Patient ID",
      ranking_df$ID,
      selectize=F)
  })
  
  output$num_conmeds <- renderPlot({
    num_conmeds <- rxnorm %>%
      group_by(ID) %>%
      summarize(num_conmeds=n()) %>%
      group_by(num_conmeds) %>%
      summarize(num_patients=n())
    ggplot(num_conmeds, aes(x=factor(num_conmeds), y=num_patients, fill=num_conmeds)) +
      geom_bar(stat="identity", show.legend = FALSE) +
      labs(x="Number of concomitant medications", y="Number of patients") +
      theme_minimal()
  })
}
