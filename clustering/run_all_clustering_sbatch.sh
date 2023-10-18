#!/bin/bash


sample_folder=$1
labels=$2
dataset_folder=$sample_folder/output
output=$sample_folder/clustering
export MPLCONFIGDIR=$PWD/.cache
methods=("threshold" "cicero" "boruta")
for method in ${methods[@]}
do
    echo $method
    method_folder=${dataset_folder}/scopen_${method}/matrices
    output_folder=${output}/scopen_${method}
    ./run_sbatch_scopen_clustering.sh ${method_folder} ${output_folder} $labels

    method_folder=${dataset_folder}/scale_${method}/
    output_folder=${output}/scale_${method}
    ./run_scale_clustering.sh ${method_folder} ${output_folder} $labels
done

./run_no_imputation_clustering.sh ${dataset_folder} ${output} ${labels}


