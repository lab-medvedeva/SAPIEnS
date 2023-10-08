#!/bin/bash
input_file=$1
peaks_prefix=$2
organism=$3

if [[ $organism == "mouse" ]]
then
	for i in $(seq 1 19)
	do
	    cat $input_file | grep "chr${i}_" > ${peaks_prefix}_chr${i}.tsv
	done
	cat $input_file | grep "chrX_" > ${peaks_prefix}_chrX.tsv

	cat $input_file | grep "chrY_" > ${peaks_prefix}_chrY.tsv
else
	for i in $(seq 1 22)
        do
            cat $input_file | grep "chr${i}_" > ${peaks_prefix}_chr${i}.tsv
        done
        cat $input_file | grep "chrX_" > ${peaks_prefix}_chrX.tsv

        cat $input_file | grep "chrY_" > ${peaks_prefix}_chrY.tsv
fi
