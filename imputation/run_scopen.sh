#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --mem=64G
#SBATCH --partition=comet
#SBATCH --job-name=scopen_run
#SBATCH --cpus-per-task=1
input=$1
mode=$2
output=$3

mkdir -p $output

scopen --input $input --input_format $mode --output_dir $output --output_prefix scOpen --output_format 10X --verbose 1  --estimate_rank --nc 1
bash get-matrices-scopen.sh $output $output/matrices
