import pandas as pd

onsides = pd.read_csv("../data/onsides_patient_ranking.csv")
onsides = onsides.rename(columns={'Weight': 'onsides'})
offsides = pd.read_csv("../data/offsides_patient_ranking.csv")
offsides = offsides.rename(columns={'Weight': 'offsides'})
twosides = pd.read_csv("../data/twosides_patient_ranking.csv")
twosides = twosides.rename(columns={'Weight': 'twosides'})
merged_df = onsides.merge(offsides, on='ID', how='outer').merge(twosides, on='ID', how='outer')
merged_df.fillna(0, inplace=True)
merged_df = merged_df.set_index('ID')
nonzero_means = merged_df.replace(0, np.nan).mean()
merged_df = merged_df.divide(nonzero_means)
merged_df['full_weight'] = merged_df['onsides'] + (merged_df['twosides'] + merged_df['offsides'])/2
ranked_df = merged_df.sort_values(by='full_weight', ascending=False)['full_weight']
ranked_df.to_csv("../data/patient_ranking_off_on_two.csv")
