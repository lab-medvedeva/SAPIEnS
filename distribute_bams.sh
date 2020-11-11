input_folder=$1
cell_labels=$2
output=$3

mkdir -p $output

for filename in ${input_folder}/*.bam
do
    echo $filename
    python distribute_bams.py --input_bam $filename --cell_labels ${cell_labels} --output $output
done
