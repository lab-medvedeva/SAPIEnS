#!/bin/bash
#SBATCH --mem=64G
#SBATCH --cpus-per-task=12
#SBATCH --partition=comet
matrix=$1
labels=$2
output=$3
mode=$4
count_name=${5:-matrix.mtx}
peak_name=${6:-peaks.txt}
barcode_name=${7:-barcodes.txt}
num_features=${8:-150}

echo $matrix, $labels, $output, $mode, $count_name, $peak_name, $barcode_name, $num_features
python make_clustering.py --input $matrix --labels_path $labels --output $output --count_matrix_file $count_name --mode $mode --peaks_file $peak_name --barcodes_file $barcode_name --count_matrix_file $count_name --num_features ${num_features}
