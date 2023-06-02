#
# This is the server logic of a Shiny web application. You can run the
# application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

if (!require("shiny")) {
  install.packages("shiny", repos='http://cran.us.r-project.org')
}
if (!require("tidyverse")) {
  install.packages("tidyverse", repos='http://cran.us.r-project.org')
}
if (!require("here")) {
  install.packages("here", repos='http://cran.us.r-project.org')
}
if (!require("DT")) {
  install.packages("DT", repos='http://cran.us.r-project.org')
}

library(shiny)
library(tidyverse)
library(here)
library(DT)

set_here()
pwd <- getwd()
setwd("../../output")

rxnorm <- read.csv('rxnorm_cuid.csv')
hierarchy <- read.csv('rxnorm_hierarchy.csv')
on_sides <- read.csv('rxnorm_onsides.csv')
patient_ranking <- read.csv('rxnorm_rank.csv')

get_pt_id <- function(input) {
  if (!is.null(input$pt_list_rows_selected)) {
    patient_ranking[input$pt_list_rows_selected,]$ID
  } else {
    NULL
  }
}

filter_pt_reaction_df <- function(pt_df, reaction_col_name, input) {
  if (!is.null(get_pt_id(input))) {
    pt_df <- pt_df %>%
      filter(as.character(ID) == get_pt_id(input))
  }

  pt_df %>%
    select(as.symbol(reaction_col_name)) %>%
    separate_longer_delim(as.symbol(reaction_col_name), delim=';') %>%
    mutate_all(list(~na_if(.,""))) %>%
    drop_na() %>%
    unique()
}

function(input, output, session) {
  
  output$pt_drugs <- renderDataTable({
    pt_df <- rxnorm
    if (!is.null(get_pt_id(input))) {
      pt_df <- pt_df %>%
        filter(as.character(ID) == get_pt_id(input))
    }
    pt_df %>%
      select("Verbatim.Term", "Requires.Review") %>%
      mutate(
        Medication = Verbatim.Term,
        Confident = ifelse(
          Requires.Review == "False",
          as.character(icon("ok", lib = "glyphicon")),
          as.character(icon("remove", lib = "glyphicon")))) %>%
      select(Medication, Confident) %>%
      datatable(
        options = list(pageLength = 5),
        escape = FALSE,
        rownames = FALSE,
        selection = 'none')
  })
  
  output$pt_boxed_warnings <- renderDataTable({
    df <- filter_pt_reaction_df(on_sides, "boxed_warnings", input)
    names(df) <- c("Boxed warnings")
    df %>%
      datatable(
        options = list(pageLength = 5),
        rownames = FALSE,
        selection = 'none')
  })

  output$pt_adverse_reactions <- renderDataTable({
    df <- filter_pt_reaction_df(on_sides, "adverse_reactions", input)
    names(df) <- c("Adverse reactions")
    df %>%
      datatable(
        options = list(pageLength = 5),
        rownames = FALSE,
        selection = 'none')
  })
  
  output$common_drugs <- renderDataTable({
    rxnorm %>%
      group_by(`Best.RxNorm.Id`) %>%
      summarize(Medication=first(`Verbatim.Term`), Frequency=n()) %>%
      arrange(desc(Frequency)) %>%
      select(Medication, Frequency) %>%
      datatable(
        options = list(pageLength = 5),
        rownames = FALSE,
        selection = 'none')
  })
  
  output$hierarchy_blurb <- renderUI({
    case_match(
      input$hierarchy,
      "DISEASE_ci_with" ~ HTML(paste0(
        'Drugs that are contraindicated with a disease, as found in ',
        '<a href = "https://evs.nci.nih.gov/ftp1/MED-RT/MED-RT%20Documentation.pdf">',
        'MED-RT</a>.')),
      "MESHPA" ~ HTML(paste0(
        '<a href = "https://www.nlm.nih.gov/mesh/pa_abt.html">',
        'Medical Subject Headings (MeSH) pharmacological actions</a>. ',
        'These actions include the alteration of normal body functions ',
        'and the effects of chemicals on the environment.')),
      "THERAP_isa_therapeutic" ~ HTML(paste0(
        'Drug classification from ',
        '<a href = "https://www.nlm.nih.gov/healthit/snomedct/index.html">',
        'SNOMED CT</a> based on the therapeutic role of medicinal products ',
        'and medicinal product forms.')),
      "adverse_reactions" ~ HTML(paste0(
        'Adverse reactions from FDA structured product labels extracted via ',
        '<a href = "https://github.com/tatonetti-lab/onsides">OnSIDES</a>.')),
      "boxed_warnings" ~ HTML(paste0(
        'Boxed warnings from FDA structured product labels extracted via ',
        '<a href = "https://github.com/tatonetti-lab/onsides">OnSIDES</a>.')),
      .default = HTML(input$hierarchy)
    )
  })
  
  output$cohort_hierarchy <- renderDataTable({
    hierarchy_file <- paste(
      'rxnorm_cohort_', input$hierarchy, '.csv', sep='')
    df <- read.csv(hierarchy_file, header=F)
    names(df) <- c("Classification", "Frequency")
    df %>%
      datatable(
        options = list(pageLength = 10),
        rownames = FALSE,
        selection = 'none')
  })
  
  output$pt_list <- renderDataTable({
    patient_ranking %>%
      rename(
        "Patient ID" = "ID",
        "Risk" = "Weight") %>%
      datatable(
        options = list(pageLength = 15),
        rownames = FALSE,
        selection = 'single')
  })
  
  output$num_conmeds <- renderPlot({
    num_conmeds <- rxnorm %>%
      group_by(ID) %>%
      summarize(num_conmeds=n()) %>%
      group_by(num_conmeds) %>%
      summarize(num_patients=n())
    ggplot(num_conmeds, aes(x=factor(num_conmeds), y=factor(num_patients), fill=num_conmeds)) +
      geom_bar(stat="identity", show.legend = FALSE) +
      labs(x="Number of concomitant medications", y="Number of patients") +
      theme_minimal() +
      theme(text = element_text(size = 14))
  })
}