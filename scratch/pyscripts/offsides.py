import numpy as np
import pandas as pd

offsides = pd.read_csv('../OFFSIDES_corrected.csv', low_memory=False, dtype={
        'drug_rxnorn_id': str,
        'condition_meddra_id': int,
        'condition_concept_name': str,
        'PRR': float,
        'PRR_error': float,
        'mean_reporting_frequency': float})[['drug_rxnorn_id','condition_meddra_id','mean_reporting_frequency','condition_concept_name', 'PRR', 'PRR_error']]
offsides = offsides[offsides['PRR'] - offsides['PRR_error'] > 2]

input_df = pd.read_csv('../data/conmed_example_data_with_best_rxcuid.csv', encoding = 'unicode_escape', index_col=0).fillna(np.nan).replace([np.nan], [None])
input_df['Best RxNorm Id'] = [str(int(rxcui)) if rxcui else None for rxcui in input_df['Best RxNorm Id']]
joined_df = input_df.merge(offsides, how='inner', left_on='Best RxNorm Id', right_on='drug_rxnorn_id')

CTCAE = pd.read_csv("../CTCAE_v5.0_2017-11-27.csv")
CTCAE.columns = CTCAE.columns.str.strip()

def get_mean_grade(row):
    grades = [col for col in row.index if col.startswith('Grade')]
    grades = [int(grade.split(" ")[1]) for grade in grades if row[grade] != '-']
    return np.mean(grades)
  
CTCAE['Mean Grade'] = CTCAE.apply(get_mean_grade, axis=1)
merged_df = joined_df.merge(CTCAE, how='inner', left_on='condition_meddra_id', right_on='MedDRA Code')
result_df = merged_df[["ID", "mean_reporting_frequency", "Mean Grade"]]
result_df["Weight"] = result_df["mean_reporting_frequency"] * result_df["Mean Grade"]
output_list = result_df.groupby("ID").Weight.sum().sort_values(ascending=False)
output_list.to_csv("../data/offsides_patient_ranking.csv")

