#!/bin/bash

HELP=""

while [[ $# -gt 0 ]]
do
    key=$1
    echo $key
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
        --cell_names)
            CELL_NAMES=$2
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
        --sra)
            SRA=$2
            shift 2
            ;;
        -b|--bams)
            BAMS=$2
            shift 2
            ;;
        --peak_save)
            PEAK_SAVE=$2
            shift 2
            ;;
        -h|--help)
            HELP=1
            shift 1
            echo "Usage: ..."
            exit 0
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

BAMS_FOLDER=${DUMP_FOLDER}/bams
mkdir -p ${BAMS_FOLDER}

echo $RGTDATA

echo "Filtering peaks"
for cell_type in ${CELL_TYPES[@]}
do
    echo $cell_type
    python post_filtering_peaks.py \
        --imputed_data ${SCALE_OUTPUT}/imputed_data_${PEAK_SAVE}_${NUM_ITERATION}_${cell_type}.txt \
        --peak_names ${PEAK_FILE} \
        --output_path ${DUMP_FOLDER}/${PEAK_SAVE}_${cell_type}_${NUM_ITERATION}_peaks.bed
done

LIST_MBPS=()
LIST_SORTED_BAMS=()


echo "Concatenating BAMs"
for cell_type in ${CELL_TYPES[@]}
do
    echo $cell_type
    sorted_bam="${BAMS_FOLDER}/${cell_type}_sorted.bam"

    if [ ! -f $sorted_bam ]
    then
        python concatenate_bams.py --sra "${SRA}" \
            --cell_type ${cell_type} \
            --input_folder ${BAMS} \
            --output_folder ${BAMS_FOLDER}
    fi
    LIST_MBPS+=("${FOOTPRINTS_FOLDER}/${PEAK_SAVE}_${cell_type}_${NUM_ITERATION}_mpbs.bed")
    LIST_SORTED_BAMS+=("${BAMS_FOLDER}/${cell_type}_sorted.bam")
done

FULL_LIST_MBPS=$(IFS=, ; echo "${LIST_MBPS[*]}")
echo $FULL_LIST_MBPS

FULL_LIST_BAMS=$(IFS=, ; echo "${LIST_SORTED_BAMS[*]}")
echo $FULL_LIST_BAMS


FULL_LIST_TYPES=$(IFS=, ; printf "%s" "${CELL_TYPES[*]}")
echo $FULL_LIST_TYPES


echo "Footprinting"

for cell_type in ${CELL_TYPES[@]}
do
    echo $cell_type
    if [ ! -f ${FOOTPRINTS_FOLDER}/${PEAK_SAVE}_${cell_type}_${NUM_ITERATION}.bed ]
    then
        rgt-hint footprinting --atac-seq --paired-end --organism hg38 \
            --output-location ${FOOTPRINTS_FOLDER} \
            --output-prefix ${PEAK_SAVE}_${cell_type}_${NUM_ITERATION} ${BAMS_FOLDER}/${cell_type}_sorted.bam ${DUMP_FOLDER}/${PEAK_SAVE}_${cell_type}_${NUM_ITERATION}_peaks.bed
    fi
done


echo "Motif Matching"

for cell_type in ${CELL_TYPES[@]}
do
    echo $cell_type
    if [ ! -f "${FOOTPRINTS_FOLDER}/${PEAK_SAVE}_${cell_type}_${NUM_ITERATION}_mpbs.bed" ]
    then
        rgt-motifanalysis matching --organism=hg38 \
            --motif-dbs $RGTDATA/motifs/hocomoco --filter "name:HUMAN" \
            --output-location ${FOOTPRINTS_FOLDER} --input-file ${FOOTPRINTS_FOLDER}/${PEAK_SAVE}_${cell_type}_${NUM_ITERATION}.bed
    fi
done


echo "Differential Footprinting"
rgt-hint differential --organism hg38 --bc --nc 24 --mpbs-files ${FULL_LIST_MBPS} \
    --reads-files ${FULL_LIST_BAMS} \
    --conditions ${FULL_LIST_TYPES} \
    --output-location ${FOOTPRINTS_FOLDER}/cicero_${PEAK_SAVE}_${NUM_ITERATION}

