python python/get_rxnorm_cuid.py \
  --input data/conmed_example_data.csv \
  --output output/rxnorm_cuid.csv

python python/get_hierarchy.py \
  --input output/rxnorm_cuid.csv \
  --output output/rxnorm_hierarchy.csv
