# Author: Karen Feng

import argparse
import numpy as np
import pandas as pd

argParser = argparse.ArgumentParser()
argParser.add_argument("-i", "--input", help="Input file")
argParser.add_argument("-o", "--output", help="Output prefix")
argParser.add_argument("--annotation", help="Annotation file")
args = argParser.parse_args()

input_df = pd.read_csv(args.input, index_col=0).fillna(np.nan).replace([np.nan], [None])
annotation_df = pd.read_csv(args.annotation, index_col=0).fillna(np.nan).replace([np.nan], [None])
annotation_columns = set(annotation_df.columns.tolist()) - set(input_df.columns.tolist())

col_counts = dict()
for colname in annotation_columns:
    annotation_df[colname] = annotation_df[colname].apply(
        lambda x: x.split(';') if x else [''])
    indiv = annotation_df.groupby('ID').agg({colname: sum})
    indiv[colname] = indiv[colname].apply(set)
    pool = indiv[colname].explode()
    pool_counts = pool.value_counts()
    pool_counts = pool_counts.drop('')
    col_counts[colname] = pool_counts

for col, counts in col_counts.items():
    pd.DataFrame.from_dict(counts).to_csv('{}_{}.csv'.format(args.output, col), header=False)