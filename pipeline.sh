python python/get_rxnorm_cuid.py \
  --input data/conmed_example_data.csv \
  --output output/rxnorm_cuid.csv

python python/get_hierarchy.py \
  --input output/rxnorm_cuid.csv \
  --output output/rxnorm_hierarchy.csv

python python/process_annotations.py \
  --input output/rxnorm_cuid.csv \
  --annotation output/rxnorm_hierarchy.csv \
  --output output/rxnorm_cohort

python python/get_onsides.py \
  --onsides resources/onsides_20230309 \
  --meddra term \
  --input output/rxnorm_cuid.csv \
  --output output/rxnorm_onsides.csv

python python/process_annotations.py \
  --input output/rxnorm_cuid.csv \
  --annotation output/rxnorm_onsides.csv \
  --output output/rxnorm_cohort