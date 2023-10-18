#!/bin/bash
#SBATCH --cpus-per-task=32
#SBATCH --mem=48G
folder=$1
python get_boruta_matrix.py --mode 10X --labels_path ../../Datasets/PBMC5K/input/labels.tsv --input $folder/raw --output_folder $folder/boruta --length_deep 1000 --percentage 60 2>&1
