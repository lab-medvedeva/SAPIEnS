#!/bin/bash
#SBATCH --partition=comet
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G


sbatch_command=$(sbatch --help)
result=$?

dataset=PBMC5K
DEFAULT_FOLDER=../../Datasets/$dataset/samples/$point_ratio/output
for sample_ratio in $(seq 0.2 0.2 0.8)
do
    point_ratio=$(echo $sample_ratio | sed 's/,/\./')
    echo $point_ratio
    if [ $result -eq 0 ] 
    then
	echo "Sbatch found. Running pipeline on cluster"
	sbatch run_scopen.sh $DEFAULT_FOLDER/cicero 10X $DEFAULT/scopen_cicero
	sbatch run_scopen.sh $DEFAULT_FOLDER/threshold 10X $DEFAULT_FOLDER/scopen_threshold
    else
	echo "Sbatch not found. Please, notify your users about hard tasks. In 10 seconds it will start"
	sleep 10
	bash run_scopen.sh $DEFAULT_FOLDER/cicero 10X $DEFAULT_FOLDER/scopen_cicero
	bash run_scopen.sh $DEFAULT_FOLDER/threshold 10X $DEFAULT_FOLDER/scopen_threshold
    fi
done
