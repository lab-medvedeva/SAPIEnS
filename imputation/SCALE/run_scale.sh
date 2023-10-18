#!/bin/bash

#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --mem=32G
#SBATCH --partition=aurora
#SBATCH --job-name=scale_run
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:2

export LD_LIBRARY_PATH=/mnt/storage/lab2/miniconda3/envs/cicero2/lib:$LD_LIBRARY_PATH
input=$1
labels=$2
output=$3
experiment_name=$4
gpu_id=$5
#num_clusters=$5

export HOME=/mnt/flashgpu/lab2

num_clusters=$(cat $labels | awk '{ print $2 }' | sort | uniq | wc -l)
mkdir -p $output

CUDA_VISIBLE_DEVICES=${gpu_id} python SCALE.py -d $input --latent 10 \
	-o $output --min_peaks 1 -x 0 \
	-r $labels  -k $num_clusters --max_iter 100000 --impute_iteration 10000 \
	--reference_type atlas --peak_save imputed \
	--experiment_name $experiment_name \
    --encode_dim 1600 600 300 100 --lr 0.001
