#!/bin/bash
#SBATCH --mem=96G
#SBATCH --cpus-per-task=12
#SBATCH --partition=titan_X
#SBATCH --gres=gpu:1
#SBATCH --job-name=run_boruta
matrix=$1
labels=$2
output=$3
mode=$4
count_name=${5:-matrix.mtx}
peak_name=${6:-peaks.txt}
barcode_name=${7:-barcodes.txt}
python get_boruta_matrix.py --input $matrix --labels_path $labels --output_folder $output --count_matrix_file $count_name --mode $mode --peaks_file $peak_name --barcodes_file $barcode_name --count_matrix_file $count_name
