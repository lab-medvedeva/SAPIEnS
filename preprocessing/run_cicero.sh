prefix=$1
output=$2
genome_path=$3

for i in $(seq 1 22)
do
    echo $i
    genome_path=${genome_path} chromosome=chr$i prefix=${prefix} output=${output} Rscript detect_cis_regions.R
done
genome_path=${genome_path} chromosome=chrX prefix=${prefix} output=${output} Rscript detect_cis_regions.R

# genome_path=${genome_path} chromosome=chrY prefix=${prefix} output=${output} Rscript detect_cis_regions.R
