#!/bin/bash
#SBATCH --partition=comet
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G


for sample_ratio in $(seq 0.2 0.2 0.8)
do
    point_ratio=$(echo $sample_ratio | sed 's/,/\./')
    echo $point_ratio
    python subsample_matrix.py \
       --input ../../Datasets/PBMC5K/input \
       --sample_ratio $point_ratio \
       --mode 10X \
       --output ../../Datasets/PBMC5K/samples/$point_ratio/output/raw

    python subset_matrix.py \
      --input ../../Datasets/PBMC5K/samples/$point_ratio/output/raw \
      --remain 50000 \
      --mode 10X \
      --output ../../Datasets/PBMC5K/samples/$point_ratio/output/threshold
done
#python subsample_matrix.py \
#    --input ../../Datasets/PBMC5K/input \          
#    --sample_ratio 0.6 \
#    --mode 10X \
#    --output ../../Datasets/PBMC5K/samples/0.6
