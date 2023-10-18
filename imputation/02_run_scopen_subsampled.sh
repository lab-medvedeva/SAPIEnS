#!/bin/bash
#SBATCH --partition=comet
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G


sbatch_command=$(sbatch --help)
result=$?

dataset_path=$1
for sample_ratio in $(seq 0.2 0.2 1.0)
do
    point_ratio=$(echo $sample_ratio | sed 's/,/\./')

    DEFAULT_FOLDER=${dataset_path}/samples/$point_ratio/output
    echo $point_ratio
    if [ $result -eq 0 ] 
    then
	echo "Sbatch found. Running pipeline on cluster"
	#sbatch run_scopen.sh $DEFAULT_FOLDER/cicero 10X $DEFAULT_FOLDER/scopen_cicero
	#sbatch run_scopen.sh $DEFAULT_FOLDER/threshold 10X $DEFAULT_FOLDER/scopen_threshold
	sbatch run_scopen.sh $DEFAULT_FOLDER/boruta 10X $DEFAULT_FOLDER/scopen_boruta
    else
	echo "Sbatch not found. Please, notify your users about hard tasks. In 10 seconds it will start"
	sleep 10
	#bash run_scopen.sh $DEFAULT_FOLDER/cicero 10X $DEFAULT_FOLDER/scopen_cicero
	#bash run_scopen.sh $DEFAULT_FOLDER/threshold 10X $DEFAULT_FOLDER/scopen_threshold
	bash run_scopen.sh $DEFAULT_FOLDER/boruta 10X $DEFAULT_FOLDER/scopen_boruta
    fi
done
