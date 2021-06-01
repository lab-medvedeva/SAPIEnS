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
        -t|--cicero_threshold)
            CICERO_THRESHOLD=$2
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
        --run_cicero)
            RUN_CICERO=true
            shift 2
            ;;
        -h|--help)
            HELP=1
            shift 2
            ;;
        --peak_save)
            PEAK_SAVE=$2
            shift 2
            ;;
    esac
done

CICERO_THRESHOLD=${CICERO_THRESHOLD:-0.6}
DUMP_FOLDER=${DUMP_FOLDER:-cicero_data}
RUN_CICERO=${RUN_CICERO:-false}
PEAK_SAVE=${PEAK_SAVE:-raw}

echo "DUMP_FOLDER: ${DUMP_FOLDER}"
echo "PEAK_FILE: ${PEAK_FILE}"
echo "CICERO_THRESHOLD: ${CICERO_THRESHOLD}"
echo "CELL_NAMES: ${CELL_NAMES}"
echo "SCALE_OUTPUT_FOLDER: ${SCALE_OUTPUT}"
echo "RUN_CICERO: ${RUN_CICERO}"

mkdir -p ${DUMP_FOLDER}


if [ ${RUN_CICERO} == "true" ]
then 

    echo "Extracting Cicero peaks"
    python extract_cicero_regions.py \
        --input_peaks ${PEAK_FILE} \
        --input_count_matrix ${COUNT_MATRIX} \
        --output ${DUMP_FOLDER}/peaks_for_cicero.tsv

    echo "Splitting dataset by chromosome"

    ./split_dataset.sh ${DUMP_FOLDER}/peaks_for_cicero.tsv ${DUMP_FOLDER}/peaks

    echo "Running Cicero"
    ./run_cicero.sh ${DUMP_FOLDER}/peaks_ ${DUMP_FOLDER}/peaks_filtered_

    echo "Filtering cells by coaccess threshold"
    python filter_cells_by_coaccess.py \
        --prefix ${DUMP_FOLDER}/peaks_filtered \
        --count_matrix ${COUNT_MATRIX} \
        --threshold ${CICERO_THRESHOLD} \
        --output ${DUMP_FOLDER}/cicero_count_matrix.csv \
        --peak_names ${PEAK_FILE}
fi

python SCALE.py -d ${DUMP_FOLDER}/cicero_count_matrix.csv \
    --latent 10 \
    -o ${SCALE_OUTPUT} \
    --min_peaks 1 \
    -x 0.001 \
    -r ${CELL_NAMES} \
    --max_iter 30000 --impute_iteration 1000 --reference_type default --peak_save ${PEAK_SAVE}

#python post_filtering_peaks.py \
#    --imputed_data results/cicero_test/imputed_data_14999.txt \
#    --cell_names count_matrix_data/GSE96769_cell_names_matrix.csv \
#    --peak_names count_matrix_data/GSE96769_PeakFile.csv \
#    --cell_type CLP \
#    --output_path cicero_data/CLP_14999_peaks.bed

#python post_filtering_peaks.py \
#    --imputed_data results/cicero_test/imputed_data_14999.txt \
#    --cell_names count_matrix_data/GSE96769_cell_names_matrix.csv \
#    --peak_names count_matrix_data/GSE96769_PeakFile.csv \
#    --cell_type HSC \
#    --output_path cicero_data/HSC_14999_peaks.bed

#DUMP_FOLDER=cicero_data
#FOOTPRINTS_FOLDER=${DUMP_FOLDER}/found_footprints
#mkdir -p ${FOOTPRINTS_FOLDER}

#BAMS_FOLDER=${DUMP_FOLDER}/bams
#python concatenate_bams.py --sra /home/akhtyamovpavel/Downloads/SraRunTable\ \(1\).txt \
#    --cell_type HSC \
#    --input_folder /home/akhtyamovpavel/Science/BioInfo/data/sra_bam_cleaned_shifted \
#    --output_folder ${BAMS_FOLDER}

#python concatenate_bams.py --sra /home/akhtyamovpavel/Downloads/SraRunTable\ \(1\).txt \
#    --cell_type CLP \
#    --input_folder /home/akhtyamovpavel/Science/BioInfo/data/sra_bam_cleaned_shifted \
#    --output_folder ${BAMS_FOLDER}
#
#rgt-hint footprinting --atac-seq --paired-end --organism hg38 \
#    --output-location ${FOOTPRINTS_FOLDER} \
#    --output-prefix hsc_14999 ${BAMS_FOLDER}/HSC_sorted.bam ${DUMP_FOLDER}/HSC_14999_peaks.bed

#rgt-hint footprinting --atac-seq --paired-end --organism hg38 \
#    --output-location ${FOOTPRINTS_FOLDER} \
#    --output-prefix clp_14999 ${BAMS_FOLDER}/CLP_sorted.bam ${DUMP_FOLDER}/CLP_14999_peaks.bed

#rgt-motifanalysis matching --organism=hg38 \
#    --motif-dbs ~/Datasets/BioInfo/RgtData/motifs/hocomoco --filter "name:HUMAN" \
#    --output-location ${FOOTPRINTS_FOLDER} --input-file ${FOOTPRINTS_FOLDER}/hsc_14999.bed

#rgt-motifanalysis matching --organism=hg38 \
#    --motif-dbs ~/Datasets/BioInfo/RgtData/motifs/hocomoco --filter "name:HUMAN" \
#    --output-location ${FOOTPRINTS_FOLDER} --input-file ${FOOTPRINTS_FOLDER}/clp_14999.bed

#rgt-hint differential --organism hg38 --bc --nc 8 --mpbs-files ${FOOTPRINTS_FOLDER}/hsc_14999_mpbs.bed,${FOOTPRINTS_FOLDER}/clp_14999_mpbs.bed \
#    --reads-files ${BAMS_FOLDER}/hsc_sorted.bam,${BAMS_FOLDER}/clp_sorted.bam \
#    --conditions HSC,CLP \
#    --output-location ${FOOTPRINTS_FOLDER}/cicero_14999_HSC_vs_CLP --no-lineplots
