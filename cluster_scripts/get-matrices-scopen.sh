#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --mem=96G
#SBATCH --partition=titan_X
#SBATCH --gres=gpu:1
#SBATCH --job-name=get_matrices_Scopen
#SBATCH --cpus-per-task=1

input=$1
output=$2

echo $input, $output
python get_matrices.py --peaks $input/scOpen_peaks.txt --barcodes $input/scOpen_barcodes.txt --format 10x --output_folder $output
