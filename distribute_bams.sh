input_folder=$1
cell_labels=$2
output=$3

mkdir -p $output

ls ${input_folder}/*.bam | parallel -j 8 --progress python distribute_bams.py --input_bam {} --cell_labels ${cell_labels} --output $output
