# Author: Karen Feng

import argparse
import numpy as np
import pandas as pd

argParser = argparse.ArgumentParser()
argParser.add_argument("-i", "--input", help="Input file")
argParser.add_argument("-o", "--output", help="Output file")
argParser.add_argument("--offsides", help="Offsides file")
args = argParser.parse_args()

offsides = pd.read_csv(args.offsides, low_memory=False)[[
    'drug_rxnorn_id', 'condition_concept_name', 'PRR', 'PRR_error']]
offsides = offsides[offsides['PRR'] - offsides['PRR_error'] > 1]
offsides = offsides.groupby(
    'drug_rxnorn_id')['condition_concept_name'].apply(set).apply(';'.join).reset_index()
offsides['drug_rxnorn_id'] = [
    str(int(rxcui)) if rxcui else None for rxcui in offsides['drug_rxnorn_id']]

input_df = pd.read_csv(args.input, index_col=0).fillna(np.nan).replace([np.nan], [None])
input_df['Best RxNorm Id'] = [
    str(int(rxcui)) if rxcui else None for rxcui in input_df['Best RxNorm Id']]

output_df = input_df.merge(
    offsides,
    how='left',
    left_on='Best RxNorm Id',
    right_on='drug_rxnorn_id')
output_df.to_csv(args.output)