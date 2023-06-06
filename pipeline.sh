# Author: Karen Feng

INPUT_DATA=$1

# Convert drug names to RxNorm IDs

python python/get_rxnorm_cuid.py \
  --input $INPUT_DATA \
  --output output/rxnorm_cuid.csv
  
# Get all RxClass hierarchies on a per-drug level

python python/get_hierarchy.py \
  --input output/rxnorm_cuid.csv \
  --output output/rxnorm_hierarchy.csv

# Summarize hierarchies on the cohort level

python python/process_annotations.py \
  --annotation output/rxnorm_hierarchy.csv \
  --input output/rxnorm_cuid.csv \
  --output output/rxnorm_cohort

# Get all OnSides black-box warnings and adverse reactions on a per-drug level

python python/get_onsides.py \
  --onsides resources/onsides_20230309 \
  --meddra term \
  --input output/rxnorm_cuid.csv \
  --output output/rxnorm_onsides.csv

python python/get_onsides.py \
  --onsides resources/onsides_20230309 \
  --meddra id \
  --input output/rxnorm_cuid.csv \
  --output output/rxnorm_onsides_id.csv

# Summarize OnSides black-box warnings and adverse reactions on the cohort level

python python/process_annotations.py \
  --annotation output/rxnorm_onsides.csv \
  --input output/rxnorm_cuid.csv \
  --output output/rxnorm_cohort

# Rank adverse effects and boxed warnings by mean CTCAE severity

python python/rank_side_effects.py \
  --ctcae resources/CTCAE_v5.0_2017-11-27.xlsx \
  --onsides resources/onsides_20230309 \
  --input output/rxnorm_onsides_id.csv \
  --output output/side_effects_rank.csv

# Rank patients according to their OnSides warnings, weighted by mean CTCAE severity

python python/rank_patients_onsides.py \
  --rank output/side_effects_rank.csv \
  --input output/rxnorm_onsides.csv \
  --output output/rxnorm_rank.csv

# Run Shiny app

R -e "shiny::runApp('R/conmeds', launch.browser = TRUE)"
