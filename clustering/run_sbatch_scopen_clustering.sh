#!/bin/bash

folder=$1
output_folder=$2
labels=$3
mkdir -p $output_folder
for file in $(ls $folder)
do
	echo $file

	output_metrics_folder=$output_folder/$file
	input_folder=$folder/$file
	mkdir -p $output_metrics_folder

	echo $input_folder $output_metrics_folder/metrics.json
	sbatch run_clustering.sh $input_folder $labels  $output_metrics_folder/metrics.json  dense matrix.csv	
done
