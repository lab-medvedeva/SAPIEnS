#!/bin/bash
#SBATCH --partition=comet
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G


sbatch_command=$(sbatch --help)
result=$?

for sample_ratio in $(seq 0.2 0.2 1.0)
do
    point_ratio=$(echo $sample_ratio | sed 's/,/\./')
    echo $point_ratio
    if [ $result -eq 0 ] 
    then
	echo "Sbatch found. Running pipeline on cluster"
	sbatch run_boruta.sh $dataset/samples/$point_ratio/output
    else
	echo "Sbatch not found. Please, notify your users about hard tasks. In 10 seconds it will start"
	sleep 10
    	./run_boruta.sh $dataset/samples/$point_ratio/output
    fi
done
