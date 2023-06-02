from itertools import permutations
import numpy as np
import pandas as pd

 
twosides = pd.read_csv(
    '../TWOSIDES_CORRECT_FULL',
    header=0,
    usecols=[
        'drug_1_rxnorn_id',
        'drug_2_rxnorm_id',
        'condition_meddra_id',
        'condition_concept_name',
        'PRR',
        'PRR_error',
        'mean_reporting_frequency'],
    dtype={
        'drug_1_rxnorn_id': str,
        'drug_1_concept_name': str,
        'drug_2_rxnorm_id': str,
        'drug_2_concept_name': str,
        'condition_meddra_id': int,
        'condition_concept_name': str,
        'A': int,
        'B': int,
        'C': int,
        'D': int,
        'PRR': float,
        'PRR_error': float,
        'mean_reporting_frequency': float})

input_df = pd.read_csv(
    '../data/conmed_example_data_with_best_rxcuid.csv',
    index_col=0, encoding = 'unicode_escape', dtype={'Best RxNorm Id': str}).fillna(np.nan).replace([np.nan], [None])

all_drugs = input_df.groupby('ID')['Best RxNorm Id'].apply(set).apply(list)

all_pairs = all_drugs.apply(lambda x: list(permutations([l for l in x if l], 2)))
all_pairs = pd.DataFrame(all_pairs).explode('Best RxNorm Id').reset_index(drop=False)

all_pairs['drug_1_rxnorn_id'] = all_pairs['Best RxNorm Id'].str[0]
all_pairs['drug_2_rxnorm_id'] = all_pairs['Best RxNorm Id'].str[1]

pair_effects = all_pairs.merge(twosides, how='inner', on=['drug_1_rxnorn_id', 'drug_2_rxnorm_id'])
pair_effects = pair_effects[pair_effects['PRR'] - pair_effects['PRR_error'] > 2]

CTCAE = pd.read_csv("../CTCAE_v5.0_2017-11-27.csv")
CTCAE.columns = CTCAE.columns.str.strip()

def get_mean_grade(row):
    grades = [col for col in row.index if col.startswith('Grade')]
    grades = [int(grade.split(" ")[1]) for grade in grades if row[grade] != '-']
    return np.mean(grades)

CTCAE['Mean Grade'] = CTCAE.apply(get_mean_grade, axis=1)
joined_df = pair_effects.merge(CTCAE, how='inner', left_on='condition_meddra_id', right_on='MedDRA Code')
cols = pair_effects.columns.tolist()
cols.append("Mean Grade")
result_df = joined_df[cols]
result_df["Weight"] = result_df["mean_reporting_frequency"] * result_df["Mean Grade"]
output_list = result_df.groupby("ID").Weight.sum().sort_values(ascending=False)
output_list.to_csv("../data/twosides_patient_ranking.csv")
