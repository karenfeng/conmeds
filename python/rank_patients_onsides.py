# Author: Holly McCann

import argparse
import numpy as np
import pandas as pd
import requests

argParser = argparse.ArgumentParser()
argParser.add_argument("-i", "--input", help="Input file")
argParser.add_argument("-o", "--output", help="Output prefix")
argParser.add_argument("--rank", help="Side effects ranking file")
args = argParser.parse_args()

onsides_df = pd.read_csv(args.input, index_col=0).fillna(np.nan).replace([np.nan], [None])
rank_df = pd.read_csv(args.rank).fillna(np.nan).replace([np.nan], [None])
rank_df.columns = ["SE", "Mean Grade"]
counts = pd.DataFrame(index=onsides_df['ID'].unique())

for colname in ['adverse_reactions', 'boxed_warnings']:
    onsides_df[colname] = onsides_df[colname].apply(lambda x: x.split(';') if x else [''])
    indiv = onsides_df.groupby('ID').agg({colname: sum})
    pool = indiv[colname].explode()
    pool_df = pool.reset_index()
    merged_df = pool_df.merge(rank_df, left_on=colname, right_on='SE', how='inner')
    counts[colname] = merged_df.groupby("ID")['Mean Grade'].agg(sum)

counts = counts.fillna(0) 
counts['Weight'] = counts['adverse_reactions'] * 0.02 + counts['boxed_warnings'] * 1
counts = counts.rename_axis("ID")

output_list = counts['Weight'].sort_values(ascending=False)
output_list.to_csv(args.output)
