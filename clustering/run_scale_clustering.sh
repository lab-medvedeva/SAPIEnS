#!/bin/bash

folder=$1
output_folder=$2
labels=$3
num_features=$4
mkdir -p $output_folder
#ls -d $folder
#ls $folder
for file in $(ls -d $folder/*/)
do
	filename=$(basename $file)
	echo $filename
	output_metrics_folder=$output_folder/$filename/
	mkdir -p $output_metrics_folder
	sbatch run_clustering.sh $file $labels $output_metrics_folder/metrics.json  10X count.mtx peak.txt barcode.txt $num_features
done
