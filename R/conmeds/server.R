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
setwd("../../data")

hierarchy <- read.csv('conmed_example_data_with_hierarchy.csv')
on_sides <- read.csv('conmed_example_data_with_onsides.csv')

filter_pt_reaction_df <- function(pt_df, reaction_col_name, input) {
  pt_reaction_df <- pt_df %>%
    filter(ID == input$pt_id) %>%
    select(as.symbol(reaction_col_name)) %>%
    separate_rows(as.symbol(reaction_col_name), sep=';') %>%
    filter(as.symbol(reaction_col_name) != "") %>%
    unique()
  
  if (input$pt_search != '') {
    pt_relevant <- sapply(pt_reaction_df[,reaction_col_name], function(x) {
      str_detect(x, regex(input$pt_search, ignore_case=T))})
    pt_reaction_df <- pt_reaction_df[pt_relevant,]
  }
  pt_reaction_df
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
      'conmed_example_data_by_patient_', input$hierarchy, '.csv', sep='')
    df <- read.csv(hierarchy_file, header=F)
    names(df) <- c("Classification", "Frequency")
    if (input$cohort_search != '') {
      cohort_relevant <- sapply(df[,"Classification"], function(x) {
        str_detect(x, regex(input$cohort_search, ignore_case=T))})
      df <- df[cohort_relevant,]
    }
    df
  })
}
