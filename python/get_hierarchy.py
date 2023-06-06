# Author: Karen Feng

import argparse
from backoff import on_exception, expo
from collections import defaultdict
import numpy as np
import pandas as pd
import requests
from ratelimit import limits, sleep_and_retry

argParser = argparse.ArgumentParser()
argParser.add_argument("-i", "--input", help="Input file")
argParser.add_argument("-o", "--output", help="Output file")
args = argParser.parse_args()

base_api_url = 'https://rxnav.nlm.nih.gov/REST'

@sleep_and_retry
@on_exception(expo, ConnectionError, max_tries=10)
@limits(calls=20, period=2)
def call_class_api(cui):
    api_url = '{}/rxclass/class/byRxcui.json?rxcui={}'.format(
        base_api_url, rxcui)
    response = requests.get(api_url)
    if response.status_code == 403:
        raise ConnectionError('API response: {}'.format(response.status_code))
    response_json = response.json()
    return response_json

@sleep_and_retry
@on_exception(expo, ConnectionError, max_tries=10)
@limits(calls=20, period=2)
def call_class_graph_api(clz_id, src):
    api_url = '{}/rxclass/classGraph.json?classId={}&source={}'.format(
        base_api_url, clz_id, src)
    response = requests.get(api_url)
    if response.status_code == 403:
        raise ConnectionError('API response: {}'.format(response.status_code))
    response_json = response.json()
    return response_json

def get_new_relationship(rxcui):
    all_clz = call_class_api(rxcui)
    if all_clz:
        rx_class_info = all_clz['rxclassDrugInfoList']['rxclassDrugInfo']

        src_clz_relationship = dict()
        for concept in rx_class_info:
            if concept['rxclassMinConceptItem']['classType'] not in src_clz_relationship:
                src_clz_relationship[concept['rxclassMinConceptItem']['classType']] = dict()
            if concept['rela'] not in src_clz_relationship[concept['rxclassMinConceptItem']['classType']]:
                src_clz_relationship[concept['rxclassMinConceptItem']['classType']][concept['rela']] = set()
            src_clz_relationship[concept['rxclassMinConceptItem']['classType']][concept['rela']].add(
                concept['rxclassMinConceptItem']['classId'])

        src_relationship = dict()
        for src, rela_ids in src_clz_relationship.items():
            if src not in src_relationship:
                src_relationship[src] = dict()
            for rela, clz_ids in rela_ids.items():
                for clz_id in clz_ids:
                    response_json = call_class_graph_api(clz_id, src)
                    if response_json['rxclassGraph']:
                        if rela not in src_relationship[src]:
                            src_relationship[src][rela] = set()
                        src_relationship[src][rela].add(
                            response_json['rxclassGraph']['rxclassMinConceptItem'][0]['className'])
                        if len(response_json['rxclassGraph']['rxclassMinConceptItem']) > 1:
                            for concept in response_json['rxclassGraph']['rxclassMinConceptItem'][1:]:
                                concept_name = concept['className']
                                src_relationship[src][rela].add(concept_name)

        src_relationship_lists = dict()
        for src, relas in src_relationship.items():
            for rela, concept in relas.items():
                if not rela:
                    comb_src = src
                else:
                    comb_src = '_'.join([src, rela])
                src_relationship_lists[comb_src] = ';'.join(concept)

        new_relationship = pd.DataFrame(src_relationship_lists, index=[0])
    else:
        new_relationship = pd.DataFrame()
    new_relationship['Best RxNorm Id'] = rxcui
    return new_relationship

input_df = pd.read_csv(args.input, index_col=0).fillna(np.nan).replace([np.nan], [None])
input_df['Best RxNorm Id'] = [
    str(int(rxcui)) if rxcui else None for rxcui in input_df['Best RxNorm Id'] ]

relationship_df = pd.DataFrame()  
for rxcui in set(input_df['Best RxNorm Id']):
    if rxcui:
        new_relationship = get_new_relationship(rxcui)
        relationship_df = pd.concat([relationship_df, new_relationship], ignore_index=True)

output_df = input_df.merge(relationship_df, how='outer', on='Best RxNorm Id')
output_df.to_csv(args.output)