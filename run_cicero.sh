prefix=$1
output=$2

for i in $(seq 1 22)
do
    echo $i
    chromosome=chr$i prefix=${prefix} output=${output} Rscript detect_cis_regions.R
done
chromosome=chrX prefix=${prefix} output=${output} Rscript detect_cis_regions.R
