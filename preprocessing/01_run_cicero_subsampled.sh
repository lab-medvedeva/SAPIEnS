#!/bin/bash
#SBATCH --partition=comet
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G


sbatch_command=$(sbatch --help)
result=$?

for sample_ratio in $(seq 0.2 0.2 0.8)
do
    point_ratio=$(echo $sample_ratio | sed 's/,/\./')
    if [ $result -eq 0 ] 
    then
	echo "Sbatch found. Running pipeline on cluster"
	sbatch run_cicero_pipeline.sh ../../Datasets/PBMC5K/samples/$point_ratio/output human 50000
    else
	echo "Sbatch not found. Please, notify your users about hard tasks. In 10 seconds it will start"
	sleep 10
    	./run_cicero_pipeline.sh ../../Datasets/PBMC5K/samples/$point_ratio/output human 50000
    fi
done
#python subsample_matrix.py \
#    --input ../../Datasets/PBMC5K/input \          
#    --sample_ratio 0.6 \
#    --mode 10X \
#    --output ../../Datasets/PBMC5K/samples/0.6
