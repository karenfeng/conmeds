import argparse
import numpy as np
import pandas as pd
import requests

def get_normalized_rxnorm_id(term, active_concept=True, exact_match=True, approximate_match=True):
    allsrc = 0 if active_concept else 1
    if exact_match and approximate_match:
        search = 2 # best match
    elif approximate_match:
        search = 1
    elif exact_match:
        search = 0
    else:
        raise Exception('Must use exact and/or approximate match')
    api_url = 'https://rxnav.nlm.nih.gov/REST/rxcui.json?name={}&allsrc={}&search={}'.format(
        term, allsrc, search)
    response = requests.get(api_url)
    response_json = response.json()
    rxnorm_id_list = response_json['idGroup'].get('rxnormId')
    rxnorm_id = rxnorm_id_list[0] if rxnorm_id_list else None
    return rxnorm_id

def get_approximate_rxnorm_id(term, active_concept=True):
    option = 1 if active_concept else 0
    api_url = 'https://rxnav.nlm.nih.gov/REST/approximateTerm.json?term={}&maxEntries=1&option={}'.format(
        term, option)
    response = requests.get(api_url)
    response_json = response.json()
    candidate_opt = response_json['approximateGroup'].get('candidate')
    rxnorm_id = candidate_opt[0]['rxcui'] if candidate_opt else None
    return rxnorm_id

argParser = argparse.ArgumentParser()
argParser.add_argument("-i", "--input", help="Input file")
argParser.add_argument("-o", "--output", help="Output file")
args = argParser.parse_args()

df = pd.read_csv(args.input).fillna(np.nan).replace([np.nan], [None])
df['RXCUI'] = [str(int(rxcui)) if rxcui else None for rxcui in df['RXCUI'] ]
df['Normalized RxNorm Id'] = df['Verbatim Term'].apply(get_normalized_rxnorm_id)
df['Approximate RxNorm Id'] = df['Verbatim Term'].apply(get_approximate_rxnorm_id)
df['Best RxNorm Id'] = df['Normalized RxNorm Id'].combine_first(df['Approximate RxNorm Id'])
df['Requires Review'] = df['Normalized RxNorm Id'] != df['Approximate RxNorm Id']

df.to_csv(args.output)

