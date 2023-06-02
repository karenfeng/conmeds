import argparse
import numpy as np
import pandas as pd
import requests

argParser = argparse.ArgumentParser()
argParser.add_argument("-i", "--input", help="Input file")
argParser.add_argument("-o", "--output", help="Output prefix")
argParser.add_argument("--ctcae", help="CTCAE file")
args = argParser.parse_args()

def get_mean_grade(row):
    grades = [col for col in row.index if col.startswith('Grade')]
    grades = [int(grade.split(" ")[1]) for grade in grades if row[grade] != '-']
    return np.mean(grades)

CTCAE = pd.read_excel(args.ctcae, sheet_name=0)
CTCAE.columns = CTCAE.columns.str.strip()
CTCAE['Mean Grade'] = CTCAE.apply(get_mean_grade, axis=1)

onsides_df = pd.read_csv(args.input, index_col=0).fillna(np.nan).replace([np.nan], [None])
MPS_dict = {}
counts = pd.DataFrame(index=onsides_df['ID'].unique())
for colname in ['adverse_reactions', 'boxed_warnings']:
    onsides_df[colname] = onsides_df[colname].apply(lambda x: x.split(';') if x else [''])
    indiv = onsides_df.groupby('ID').agg({colname: sum})
    indiv[colname] = indiv[colname].apply(set)
    pool = indiv[colname].explode()
    pool = pool[pool.str.strip() != ''].astype(int)
    pool_df = pool.reset_index()
    i = 0
    print("Processing {} IDs".format(len(pool_df[colname].unique())))
    for num in pool_df[colname].unique():
        if i % 20 == 0:
            print("Processed {} IDs".format(i))
        i += 1
        if not num in MPS_dict and num in set(CTCAE['MedDRA Code']):
            MPS_dict[num] = num
        elif not num in MPS_dict:
            url = "https://api-evsrest.nci.nih.gov/api/v1/concept/mdr/" + str(num)
            response = requests.get(url, timeout=1)
            data = response.json()
            primary_soc = None
            for prop in data["properties"]:
                if prop["type"] == "PRIMARY_SOC":
                    primary_soc = prop["value"]
                    MPS_dict[num] = int(primary_soc)
    new_col = colname + '_MPS'
    pool_df[new_col] = pool_df[colname].map(MPS_dict)
    merged_df = CTCAE.merge(pool_df, right_on=new_col, left_on='MedDRA Code', how='inner')
    counts[colname] = merged_df.groupby("ID")['Mean Grade'].agg(sum)
counts = counts.fillna(0) 
counts['Weight'] = counts['adverse_reactions'] * 0.02 + counts['boxed_warnings'] * 1
counts = counts.rename_axis("ID")

output_list = counts['Weight'].sort_values(ascending=False)
output_list.to_csv(args.output)
