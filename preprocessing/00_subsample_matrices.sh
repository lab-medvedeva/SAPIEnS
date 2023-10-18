#!/bin/bash
#SBATCH --partition=comet
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G

dataset_folder=$1

for sample_ratio in $(seq 0.2 0.2 0.8)
do
    point_ratio=$(echo $sample_ratio | sed 's/,/\./')
    echo $point_ratio
    python subsample_matrix.py \
       --input $dataset_folder/input \
       --sample_ratio $point_ratio \
       --mode 10X \
       --output $dataset_folder/samples/$point_ratio/output/raw

    python subset_matrix.py \
      --input $dataset_folder/samples/$point_ratio/output/raw \
      --remain 50000 \
      --mode 10X \
      --output $dataset_folder/samples/$point_ratio/output/threshold
done

mkdir -p $dataset_folder/samples/1.0/output
ln -s $dataset_folder/input $dataset_folder/samples/1.0/output/raw

python subset_matrix.py \
      --input $dataset_folder/samples/1.0/output/raw \
      --remain 50000 \
      --mode 10X \
      --output $dataset_folder/samples/1.0/output/threshold
