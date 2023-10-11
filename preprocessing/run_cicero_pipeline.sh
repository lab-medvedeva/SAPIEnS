#!/bin/bash

DEFAULT_FOLDER=$1
ORGANISM=${2:-human}
NUM_REMAIN=${3:-50000}

CICERO_FOLDER=${DEFAULT_FOLDER}/cicero

mkdir -p $CICERO_FOLDER

#python extract_cicero_regions_original.py \
#    --folder $DEFAULT_FOLDER/raw --output $CICERO_FOLDER/peaks_dumped.tsv

#./split_dataset.sh $CICERO_FOLDER/peaks_dumped.tsv $CICERO_FOLDER/peaks $ORGANISM

mkdir -p $CICERO_FOLDER/filtered

#./run_cicero.sh ${CICERO_FOLDER}/peaks_ $CICERO_FOLDER/filtered/peaks_ ../../data/hg38.chrom.sizes

python filter_cells_by_coaccess_count_mtx.py --input $DEFAULT_FOLDER/raw --prefix $CICERO_FOLDER/filtered/peaks_ --organism human --output $CICERO_FOLDER --remain $NUM_REMAIN
