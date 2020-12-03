#!/bin/bash

HELP=""

while [[ $# -gt 0 ]]
do
    key=$1
    echo $key $2
    case $key in
        -d|--dump_folder)
            DUMP_FOLDER=$2
            shift 2
            ;;
        -p|--peak_file)
            PEAK_FILE=$2
            shift 2
            ;;
        -c|--count_matrix)
            COUNT_MATRIX=$2
            shift 2
            ;;
        -out|--scale_output)
            SCALE_OUTPUT=$2
            shift 2
            ;;
        -it|--iteration)
            NUM_ITERATION=$2
            shift 2
            ;;
        -types|--cell_types)
            readarray -t CELL_TYPES < $2
            shift 2
            for cell_type in ${CELL_TYPES[@]}
            do
                echo $cell_type
            done
            ;;
        -b|--bams)
            BAMS=$2
            shift 2
            ;;
        -o|--organism)
            ORGANISM=$2
            shift 2
            ;;
        -h|--help)
            HELP=1
            shift 2
            ;;
        -f|--filter)
            FILTER="yes"
            shift 1
            ;;
    esac
done


if [ ! -d ${DUMP_FOLDER} ]
then
    echo "${DUMP_FOLDER} does not exist. Run pipeline before"
    exit 
fi

FOOTPRINTS_FOLDER=${DUMP_FOLDER}/found_footprints
mkdir -p ${FOOTPRINTS_FOLDER}

BAMS_FOLDER=${BAMS}
FILTER="${FILTER:-no}"
echo $RGTDATA


LIST_MBPS=()
LIST_SORTED_BAMS=()

for cell_type in ${CELL_TYPES[@]}
do
    LIST_MBPS+=("${FOOTPRINTS_FOLDER}/${cell_type}_${NUM_ITERATION}_mpbs.bed")
    sorted_bam="${BAMS_FOLDER}/${cell_type}_sorted.bam"
    echo "$sorted_bam"
    if [ ! -f $sorted_bam ]
    then
        echo "Sorting ${cell_type}"
        samtools sort ${BAMS_FOLDER}/${cell_type}.bam > ${sorted_bam}
    fi
    LIST_SORTED_BAMS+=("${BAMS_FOLDER}/${cell_type}_sorted.bam")
done

FULL_LIST_MBPS=$(IFS=, ; echo "${LIST_MBPS[*]}")
echo $FULL_LIST_MBPS

FULL_LIST_BAMS=$(IFS=, ; echo "${LIST_SORTED_BAMS[*]}")
echo $FULL_LIST_BAMS


FULL_LIST_TYPES=$(IFS=, ; printf "%s" "${CELL_TYPES[*]}")
echo $FULL_LIST_TYPES

if [ $FILTER == "yes" ]
then
    for cell_type in ${CELL_TYPES[@]}
    do
        python post_filtering_peaks.py \
            --imputed_data ${SCALE_OUTPUT}/imputed_data_${NUM_ITERATION}_${cell_type}.txt \
            --cell_type ${cell_type} \
            --pipeline from_peaks \
            --dataset mouse_atlas \
            --output_path ${DUMP_FOLDER}/${cell_type}_${NUM_ITERATION}_peaks.bed
    done
fi


for cell_type in ${CELL_TYPES[@]}
do
    echo "Cell type: ${cell_type}"
    echo "Footprinting"
    if [ ! -f ${FOOTPRINTS_FOLDER}/${cell_type}_${NUM_ITERATION}.bed ]
    then
        rgt-hint footprinting --atac-seq --paired-end --organism ${ORGANISM} \
            --output-location ${FOOTPRINTS_FOLDER} \
            --output-prefix ${cell_type}_${NUM_ITERATION} ${BAMS_FOLDER}/${cell_type}_sorted.bam ${DUMP_FOLDER}/${cell_type}_${NUM_ITERATION}_peaks.bed
    fi
done

for cell_type in ${CELL_TYPES[@]}
do
    echo "Cell type: ${cell_type}"
    echo "Matching"
    rgt-motifanalysis matching --organism=${ORGANISM} \
        --motif-dbs $RGTDATA/motifs/hocomoco --filter "name:MOUSE" \
        --output-location ${FOOTPRINTS_FOLDER} --input-file ${FOOTPRINTS_FOLDER}/${cell_type}_${NUM_ITERATION}.bed

done

echo "Differential Footprinting"
rgt-hint differential --organism ${ORGANISM} --bc --nc 8 --mpbs-files ${FULL_LIST_MBPS} \
    --reads-files ${FULL_LIST_BAMS} \
    --conditions ${FULL_LIST_TYPES} \
    --output-location ${FOOTPRINTS_FOLDER}/cicero_${NUM_ITERATION}
