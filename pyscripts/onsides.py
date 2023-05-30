import numpy as np
import pandas as pd

onsides_df = pd.read_csv('../data/conmed_example_data_with_onsides.csv', index_col=0).fillna(np.nan).replace([np.nan], [None])

counts = pd.DataFrame(index=onsides_df['ID'].unique())
for colname in ['adverse_reactions', 'boxed_warnings']:
    onsides_df[colname] = onsides_df[colname].apply(lambda x: x.split(';') if x else [''])
    indiv = onsides_df.groupby('ID').agg({colname: sum})
    indiv[colname] = indiv[colname].apply(set)
    pool = indiv[colname].explode()
    pool = pool[pool.str.strip() != '']
    counts[colname] = pool.groupby(pool.index).size()

counts = counts.fillna(0) 
counts['Weight'] = counts['adverse_reactions'] * 0.05 + counts['boxed_warnings'] * 1
counts = counts.rename_axis("ID")
output_list = counts['Weight'].sort_values(ascending=False)
output_list.to_csv("../data/onsides_patient_ranking.csv")
