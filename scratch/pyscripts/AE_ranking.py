import requests
import json
import numpy as np
import pandas as pd

#Replace these
CTCAE = pd.read_csv("../../CTCAE_v5.0_2017-11-27.csv")
onsides_df = pd.read_csv('../data/conmed_example_data_with_onsides_ids.csv', index_col=0).fillna(np.nan).replace([np.nan], [None])
onsides_ar = pd.read_csv('../../data/onsides_20230309/adverse_reactions_active_labels.csv')
onsides_bw = pd.read_csv('../../data/onsides_20230309/boxed_warnings_active_labels.csv')

CTCAE.columns = CTCAE.columns.str.strip()

def get_mean_grade(row):
    grades = [col for col in row.index if col.startswith('Grade')]
    grades = [int(grade.split(" ")[1]) for grade in grades if row[grade] != '-']
    return np.mean(grades)
  
CTCAE['Mean Grade'] = CTCAE.apply(get_mean_grade, axis=1)

ar_dict =dict(zip(onsides_ar['pt_meddra_id'], onsides_ar['pt_meddra_term']))
bw_dict =dict(zip(onsides_bw['pt_meddra_id'], onsides_bw['pt_meddra_term']))
MPS_dict = {}
SE = {}
for colname in ['adverse_reactions', 'boxed_warnings']:
    onsides_df[colname] = onsides_df[colname].apply(lambda x: x.split(';') if x else [''])
    indiv = onsides_df.groupby('ID').agg({colname: sum})
    indiv[colname] = indiv[colname].apply(set)
    pool = indiv[colname].explode()
    pool = pool[pool.str.strip() != ''].astype(int)
    pool_df = pool.reset_index()
    session = requests.Session()
    for num in pool_df[colname].unique():
        if num in set(CTCAE['MedDRA Code']):
            MPS_dict[num] = num
        elif not num in MPS_dict:
            url = "https://api-evsrest.nci.nih.gov/api/v1/concept/mdr/" + str(num)
            response = session.get(url)
            data = response.json()
            primary_soc = None
            for prop in data["properties"]:
                if prop["type"] == "PRIMARY_SOC":
                    primary_soc = prop["value"]
                    MPS_dict[num] = int(primary_soc)
    new_col = colname + '_MPS'
    pool_df[new_col] = pool_df[colname].map(MPS_dict)
    merged_df = CTCAE.merge(pool_df, right_on=new_col, left_on='MedDRA Code', how='inner')
    if colname == 'adverse_reactions':
        merged_df['pt_meddra_term'] = merged_df[colname].map(ar_dict)
    elif colname == 'boxed_warnings':
        merged_df['pt_meddra_term'] = merged_df[colname].map(bw_dict)
    for index, row in merged_df.iterrows():
        term = row['pt_meddra_term']
        grade = row['Mean Grade']
        SE[term] = grade

series = pd.Series(SE)
df = pd.DataFrame(series, columns=['Mean CTCAE'])
sorted_df = df.sort_values(by='Mean CTCAE', ascending = False)
sorted_df.to_csv('../data/side_effects_CTCAE_ranked.csv')
