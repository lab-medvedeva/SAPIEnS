DUMP_FOLDER=cicero_data
FOOTPRINTS_FOLDER=${DUMP_FOLDER}/found_footprints
mkdir -p ${FOOTPRINTS_FOLDER}

BAMS_FOLDER=${DUMP_FOLDER}/bams
mkdir -p ${BAMS_FOLDER}

CELL_TYPE_1=$1
CELL_TYPE_2=$2

NUM_ITERATION=$3
python post_filtering_peaks.py \
    --imputed_data results/cicero_test/imputed_data_${NUM_ITERATION}.txt \
    --cell_names count_matrix_data/GSE96769_cell_names_matrix.csv \
    --peak_names count_matrix_data/GSE96769_PeakFile.csv \
    --cell_type ${CELL_TYPE_1} \
    --output_path ${DUMP_FOLDER}/${CELL_TYPE_1}_${NUM_ITERATION}_peaks.bed

python post_filtering_peaks.py \
    --imputed_data results/cicero_test/imputed_data_${NUM_ITERATION}.txt \
    --cell_names count_matrix_data/GSE96769_cell_names_matrix.csv \
    --peak_names count_matrix_data/GSE96769_PeakFile.csv \
    --cell_type ${CELL_TYPE_2} \
    --output_path ${DUMP_FOLDER}/${CELL_TYPE_2}_${NUM_ITERATION}_peaks.bed

echo "Concatenating BAMs"
python concatenate_bams.py --sra /home/akhtyamovpavel/Downloads/SraRunTable\ \(1\).txt \
    --cell_type ${CELL_TYPE_1} \
    --input_folder /home/akhtyamovpavel/Science/BioInfo/data/sra_bam_cleaned_shifted \
    --output_folder ${BAMS_FOLDER}

python concatenate_bams.py --sra /home/akhtyamovpavel/Downloads/SraRunTable\ \(1\).txt \
    --cell_type ${CELL_TYPE_2} \
    --input_folder /home/akhtyamovpavel/Science/BioInfo/data/sra_bam_cleaned_shifted \
    --output_folder ${BAMS_FOLDER}

echo "Footprinting"
rgt-hint footprinting --atac-seq --paired-end --organism hg38 \
    --output-location ${FOOTPRINTS_FOLDER} \
    --output-prefix ${CELL_TYPE_1}_${NUM_ITERATION} ${BAMS_FOLDER}/${CELL_TYPE_1}_sorted.bam ${DUMP_FOLDER}/${CELL_TYPE_1}_${NUM_ITERATION}_peaks.bed

rgt-hint footprinting --atac-seq --paired-end --organism hg38 \
    --output-location ${FOOTPRINTS_FOLDER} \
    --output-prefix ${CELL_TYPE_2}_${NUM_ITERATION} ${BAMS_FOLDER}/${CELL_TYPE_2}_sorted.bam ${DUMP_FOLDER}/${CELL_TYPE_2}_${NUM_ITERATION}_peaks.bed

echo "Motif Matching"
rgt-motifanalysis matching --organism=hg38 \
    --motif-dbs ~/Datasets/BioInfo/RgtData/motifs/hocomoco --filter "name:HUMAN" \
    --output-location ${FOOTPRINTS_FOLDER} --input-file ${FOOTPRINTS_FOLDER}/${CELL_TYPE_1}_${NUM_ITERATION}.bed

rgt-motifanalysis matching --organism=hg38 \
    --motif-dbs ~/Datasets/BioInfo/RgtData/motifs/hocomoco --filter "name:HUMAN" \
    --output-location ${FOOTPRINTS_FOLDER} --input-file ${FOOTPRINTS_FOLDER}/${CELL_TYPE_2}_${NUM_ITERATION}.bed

echo "Differential Footprinting"
rgt-hint differential --organism hg38 --bc --nc 8 --mpbs-files ${FOOTPRINTS_FOLDER}/${CELL_TYPE_1}_${NUM_ITERATION}_mpbs.bed,${FOOTPRINTS_FOLDER}/${CELL_TYPE_2}_${NUM_ITERATION}_mpbs.bed \
    --reads-files ${BAMS_FOLDER}/${CELL_TYPE_1}_sorted.bam,${BAMS_FOLDER}/${CELL_TYPE_2}_sorted.bam \
    --conditions ${CELL_TYPE_1},${CELL_TYPE_2} \
    --output-location ${FOOTPRINTS_FOLDER}/cicero_${NUM_ITERATION}_${CELL_TYPE_1}_vs_${CELL_TYPE_2} --no-lineplots
