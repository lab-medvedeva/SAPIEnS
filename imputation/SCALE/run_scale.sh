#!/bin/bash

#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --mem=32G
#SBATCH --partition=titan_X
#SBATCH --job-name=scopen_run
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:1
#SBATCH --output=logs/scale_out.log
#SBATCH --error=logs/scale_err.log

input=$1
labels=$2
output=$3
experiment_name=$4
#num_clusters=$5

num_clusters=$(cat $labels | awk '{ print $2 }' | sort | uniq | wc -l)
mkdir -p $output

python SCALE.py -d $input --latent 10 \
	-o $output --min_peaks 1 -x 0 \
	-r $labels  -k $num_clusters --max_iter 100000 --impute_iteration 10000 \
	--reference_type atlas --peak_save imputed \
	--experiment_name $experiment_name \
     	--encode_dim 1600 600 300 100 --lr 0.001
