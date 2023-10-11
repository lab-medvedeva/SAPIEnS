#!/bin/bash

DEFAULT_FOLDER=$1
ORGANISM=${2:-human}

CICERO_FOLDER=${DEFAULT_FOLDER}/cicero

mkdir -p $CICERO_FOLDER

python extract_cicero_regions_original.py \
    --folder $DEFAULT_FOLDER/raw --output $CICERO_FOLDER/peaks_dumped.tsv

./split_dataset.sh $CICERO_FOLDER/peaks_dumped.tsv $CICERO_FOLDER/peaks $ORGANISM

mkdir -p $CICERO_FOLDER/filtered

./run_cicero.sh ${CICERO_FOLDER}/peaks_ $CICERO_FOLDER/filtered/peaks_ ../../data/hg38.chrom.sizes

#python filter_cells_by_coaccess_count_mtx.py --folder ../../Datasets/Splenocyte/output/raw --prefix ../../Datasets/Splenocyte/output/cicero/filtered/peaks_ --organism mouse --output ../../Datasets/Splenocyte/output/cicero/matrix --threshold 0.8375
