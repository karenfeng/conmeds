# Author: Karen Feng

import argparse
import numpy as np
import pandas as pd

argParser = argparse.ArgumentParser()
argParser.add_argument("-i", "--input", help="Input file")
argParser.add_argument("-o", "--output", help="Output file")
argParser.add_argument("--onsides", help="Onsides directory")
argParser.add_argument("--meddra", help="One of [term, id]")
args = argParser.parse_args()

if args.meddra == 'term':
    pt_meddra_col = 'pt_meddra_term'
elif args.meddra == 'id':
    pt_meddra_col = 'pt_meddra_id'
else:
    raise Exception("MedDRA must be term or id")

onsides_adverse_reactions = pd.read_csv(
    '{}/adverse_reactions_active_labels.csv'.format(args.onsides))[[
    'ingredients_rxcuis', pt_meddra_col]].astype('str')
onsides_adverse_reactions = onsides_adverse_reactions.groupby(
    'ingredients_rxcuis')[pt_meddra_col].apply(set).apply(';'.join).reset_index()
onsides_adverse_reactions = onsides_adverse_reactions.rename(columns={pt_meddra_col: 'adverse_reactions'})

onsides_boxed_warnings = pd.read_csv(
    '{}/boxed_warnings_active_labels.csv'.format(args.onsides))[[
    'ingredients_rxcuis', pt_meddra_col]].astype('str')
onsides_boxed_warnings = onsides_boxed_warnings.groupby(
    'ingredients_rxcuis')[pt_meddra_col].apply(set).apply(';'.join).reset_index()
onsides_boxed_warnings = onsides_boxed_warnings.rename(columns={pt_meddra_col: 'boxed_warnings'})

onsides = onsides_adverse_reactions.merge(
    onsides_boxed_warnings,
    how='outer',
    on='ingredients_rxcuis')
onsides = onsides.rename(columns={'ingredients_rxcuis': 'Best RxNorm Id'})

input_df = pd.read_csv(
    args.input, index_col=0, encoding='latin-1').fillna(np.nan).replace([np.nan], [None])
input_df['Best RxNorm Id'] = [
    str(int(rxcui)) if rxcui else None for rxcui in input_df['Best RxNorm Id']]

output_df = input_df.merge(
    onsides,
    how='left',
    on='Best RxNorm Id')
output_df.to_csv(args.output)