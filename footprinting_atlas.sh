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
        -type1|--cell_type_1)
            CELL_TYPE_1=$2
            shift 2
            ;;
        -type2|--cell_type_2)
            CELL_TYPE_2=$2
            shift 2
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

echo $RGTDATA

python post_filtering_peaks.py \
    --imputed_data ${SCALE_OUTPUT}/imputed_data_${NUM_ITERATION}_${CELL_TYPE_1}.txt \
    --cell_type ${CELL_TYPE_1} \
    --pipeline from_peaks \
    --dataset mouse_atlas \
    --output_path ${DUMP_FOLDER}/${CELL_TYPE_1}_${NUM_ITERATION}_peaks.bed

python post_filtering_peaks.py \
    --imputed_data ${SCALE_OUTPUT}/imputed_data_${NUM_ITERATION}_${CELL_TYPE_2}.txt \
    --cell_type ${CELL_TYPE_2} \
    --pipeline from_peaks \
    --dataset mouse_atlas \
    --output_path ${DUMP_FOLDER}/${CELL_TYPE_2}_${NUM_ITERATION}_peaks.bed


#python post_filtering_peaks.py \
#    --imputed_data ${COUNT_MATRIX} \
#    --cell_names ${CELL_NAMES} \
#    --peak_names ${PEAK_FILE} \
#    --cell_type ${CELL_TYPE_1} \
#    --output_path ${DUMP_FOLDER}/${CELL_TYPE_1}_raw_peaks.bed

#python post_filtering_peaks.py \
#    --imputed_data ${COUNT_MATRIX} \
#    --cell_name ${CELL_NAMES} \
#    --peak_names ${PEAK_FILE} \
#    --output_path ${DUMP_FOLDER}/${CELL_TYPE_2}_raw_peaks.bed


#echo "Concatenating BAMs"
#python concatenate_bams.py --sra "${SRA}" \
#    --cell_type ${CELL_TYPE_1} \
#    --input_folder ${BAMS} \
#    --output_folder ${BAMS_FOLDER}

#python concatenate_bams.py --sra "${SRA}" \
#    --cell_type ${CELL_TYPE_2} \
#    --input_folder ${BAMS} \
#    --output_folder ${BAMS_FOLDER}

echo "Footprinting"
rgt-hint footprinting --atac-seq --paired-end --organism ${ORGANISM} \
    --output-location ${FOOTPRINTS_FOLDER} \
    --output-prefix ${CELL_TYPE_1}_${NUM_ITERATION} ${BAMS_FOLDER}/${CELL_TYPE_1}_sorted.bam ${DUMP_FOLDER}/${CELL_TYPE_1}_${NUM_ITERATION}_peaks.bed

rgt-hint footprinting --atac-seq --paired-end --organism ${ORGANISM} \
    --output-location ${FOOTPRINTS_FOLDER} \
    --output-prefix ${CELL_TYPE_2}_${NUM_ITERATION} ${BAMS_FOLDER}/${CELL_TYPE_2}_sorted.bam ${DUMP_FOLDER}/${CELL_TYPE_2}_${NUM_ITERATION}_peaks.bed

#echo "Footprinting raw peaks"
#rgt-hint footprinting --atac-seq --paired-end --organism hg38 \
#    --output-location ${FOOTPRINTS_FOLDER} \
#    --output-prefix ${CELL_TYPE_1}_raw ${BAMS_FOLDER}/${CELL_TYPE_1}_sorted.bam ${DUMP_FOLDER}/${CELL_TYPE_1}_raw_peaks.bed

#rgt-hint footprinting --atac-seq --paired-end --organism hg38 \
#    --output-location ${FOOTPRINTS_FOLDER} \
#    --output-prefix ${CELL_TYPE_2}_raw ${BAMS_FOLDER}/${CELL_TYPE_2}_sorted.bam ${DUMP_FOLDER}/${CELL_TYPE_2}_raw_peaks.bed


echo "Motif Matching"
rgt-motifanalysis matching --organism=hg38 \
    --motif-dbs $RGTDATA/motifs/hocomoco --filter "name:MOUSE" \
    --output-location ${FOOTPRINTS_FOLDER} --input-file ${FOOTPRINTS_FOLDER}/${CELL_TYPE_1}_${NUM_ITERATION}.bed

rgt-motifanalysis matching --organism=hg38 \
    --motif-dbs $RGTDATA/motifs/hocomoco --filter "name:MOUSE" \
    --output-location ${FOOTPRINTS_FOLDER} --input-file ${FOOTPRINTS_FOLDER}/${CELL_TYPE_2}_${NUM_ITERATION}.bed

#echo "Motif Matching for raw peaks"
#rgt-motifanalysis matching --organism=hg38 \
#    --motif-dbs $RGTDATA/motifs/hocomoco --filter "name:HUMAN" \
#    --output-location ${FOOTPRINTS_FOLDER} --input-file ${FOOTPRINTS_FOLDER}/${CELL_TYPE_1}_raw.bed

#rgt-motifanalysis matching --organism=hg38 \
#    --motif-dbs $RGTDATA/motifs/hocomoco --filter "name:HUMAN" \
#    --output-location ${FOOTPRINTS_FOLDER} --input-file ${FOOTPRINTS_FOLDER}/${CELL_TYPE_2}_raw.bed

#echo "Raw Differential Footprinting"
#rgt-hint differential --organism hg38 --bc --nc 8 --mpbs-files ${FOOTPRINTS_FOLDER}/${CELL_TYPE_1}_raw_mpbs.bed,${FOOTPRINTS_FOLDER}/${CELL_TYPE_2}_raw_mpbs.bed \
#    --reads-files ${BAMS_FOLDER}/${CELL_TYPE_1}_sorted.bam,${BAMS_FOLDER}/${CELL_TYPE_2}_sorted.bam \
#    --conditions ${CELL_TYPE_1},${CELL_TYPE_2} \
#    --output-location ${FOOTPRINTS_FOLDER}/cicero_raw_${CELL_TYPE_1}_vs_${CELL_TYPE_2} --no-lineplots

echo "Differential Footprinting"
rgt-hint differential --organism hg38 --bc --nc 8 --mpbs-files ${FOOTPRINTS_FOLDER}/${CELL_TYPE_1}_${NUM_ITERATION}_mpbs.bed,${FOOTPRINTS_FOLDER}/${CELL_TYPE_2}_${NUM_ITERATION}_mpbs.bed \
    --reads-files ${BAMS_FOLDER}/${CELL_TYPE_1}_sorted.bam,${BAMS_FOLDER}/${CELL_TYPE_2}_sorted.bam \
    --conditions ${CELL_TYPE_1},${CELL_TYPE_2} \
    --output-location ${FOOTPRINTS_FOLDER}/cicero_${NUM_ITERATION}_${CELL_TYPE_1}_vs_${CELL_TYPE_2}
