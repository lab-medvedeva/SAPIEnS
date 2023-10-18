#!/bin/bash

folder=$1
output_folder=$2
labels=$3
num_features=$4
echo $folder $output_folder $labels $num_features
mkdir -p $output_folder

have_sbatch=$(sbatch --help)
response=$?

if [ $response -eq 0 ]
then
    echo "Sbatch installed"
    RUN_COMMAND=sbatch
else
    echo "Sbatch not installed. You have 10 seconds to stop this job!"
    RUN_COMMAND=bash
    sleep 10
fi

cicero_folder=$output_folder/cicero
mkdir -p $cicero_folder
$RUN_COMMAND run_clustering.sh $folder/cicero $labels $cicero_folder/metrics.json 10X counts.mtx peaks.txt barcodes.txt $num_features

threshold_folder=$output_folder/threshold
mkdir -p $threshold_folder
$RUN_COMMAND run_clustering.sh $folder/threshold $labels $threshold_folder/metrics.json 10X matrix.mtx peaks.txt barcodes.txt $num_features

boruta_folder=$output_folder/boruta
mkdir -p $boruta_folder
$RUN_COMMAND run_clustering.sh $folder/boruta $labels $boruta_folder/metrics.json 10X matrix.mtx peaks.txt barcodes.txt $num_features

