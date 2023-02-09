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
        -c|--from_clusters)
            FROM_CLUSTERS="yes"
            shift 1
            ;;
        --input_folders) # Applicable when loading from clusters
            INPUT_FOLDERS=$2
            shift 2
            ;;
    esac
done


if [ ! -d ${DUMP_FOLDER} ]
then
    mkdir -p ${DUMP_FOLDER}
#     exit 
fi

FOOTPRINTS_FOLDER=${DUMP_FOLDER}/found_footprints
mkdir -p ${FOOTPRINTS_FOLDER}

BAMS_FOLDER=${BAMS}
FILTER="${FILTER:-no}"
FROM_CLUSTERS="${FROM_CLUSTERS:-no}"
echo $RGTDATA


LIST_MBPS=()
LIST_SORTED_BAMS=()

if [ ${FROM_CLUSTERS} == "yes" ]
then
    if [ ! -d ${BAMS_FOLDER} ]
    then
        python concatenate_bams_clusters.py --input_folders ${INPUT_FOLDERS} --clusters ${SCALE_OUTPUT}/cluster_assignments_${NUM_ITERATION}.txt --output_folder ${BAMS_FOLDER}
    fi
fi


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
            --imputed_data ${SCALE_OUTPUT}/imputed_data_imputed_${NUM_ITERATION}_${cell_type}.txt \
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
        --motif-dbs $RGTDATA/motifs/hocomoco --filter "name:HUMAN" \
        --output-location ${FOOTPRINTS_FOLDER} --input-file ${FOOTPRINTS_FOLDER}/${cell_type}_${NUM_ITERATION}.bed

done

echo ${FULL_LIST_TYPES}
echo "Differential Footprinting"
rgt-hint differential --organism ${ORGANISM} --bc --nc 24 --mpbs-files ${FULL_LIST_MBPS} \
    --no-lineplots \
    --reads-files ${FULL_LIST_BAMS} \
    --conditions ${FULL_LIST_TYPES} \
    --output-location ${FOOTPRINTS_FOLDER}/cicero_${NUM_ITERATION}
