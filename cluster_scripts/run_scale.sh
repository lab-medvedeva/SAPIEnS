#!/bin/bash

#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --mem=48G
#SBATCH --partition=titan_X
#SBATCH --gres=gpu:1
#SBATCH --job-name=scale_run
#SBATCH --cpus-per-task=16
#SBATCH --output=logs/scale_out.log
#SBATCH --error=logs/scale_err.log
input=$1
#mode=$2
output=$2

mkdir -p $output

python ~/Repos/SCABFA-feature-selection/SCALE.py -d $input --latent 10 -o $output --min_peaks 1 -x 0 -r $input/labels.tsv -k 12 --max_iter 100000 --impute_iteration 10000 --reference_type atlas --peak_save imputed --experiment_name CiceroGSE96769_correct_unique_cicero_100000 --encode_dim 3200 1200 600 200 --lr 0.001

#scopen --input $input --input_format $mode --output_dir $output --output_prefix scOpen --output_format 10X --verbose 1  --estimate_rank --nc 16 --binary
