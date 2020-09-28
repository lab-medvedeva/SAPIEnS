DUMP_FOLDER=cicero_data
mkdir -p ${DUMP_FOLDER}

python extract_cicero_regions.py \
    --input_peaks count_matrix_data/GSE96769_PeakFile.csv \
    --input_count_matrix count_matrix_data/GSE96769_scATACseq_matrix.csv \
    --output ${DUMP_FOLDER}/peaks_for_cicero.tsv

./split_dataset.sh ${DUMP_FOLDER}/peaks_for_cicero.tsv ${DUMP_FOLDER}/peaks
./run_cicero.sh ${DUMP_FOLDER}/peaks_ ${DUMP_FOLDER}/peaks_filtered_

python filter_cells_by_coaccess.py \
    --prefix cicero_data/peaks_filtered \
    --count_matrix count_matrix_data/GSE96769_scATACseq_matrix.csv \
    --threshold 0.6 \
    --output ${DUMP_FOLDER}/cicero_count_matrix.csv \
    --peak_names count_matrix_data/GSE96769_PeakFile.csv

python SCALE.py -d ${DUMP_FOLDER}/cicero_count_matrix.csv \
    --impute --latent 10 \
    -o results/cicero_test \
    --min_peaks 1 \
    -x 0.005 \
    -r count_matrix_data/GSE96769_cell_names_matrix.csv \
    --max_iter 30000 --impute_iteration 5000

python post_filtering_peaks.py \
    --imputed_data results/cicero_test/imputed_data_14999.txt \
    --cell_names count_matrix_data/GSE96769_cell_names_matrix.csv \
    --peak_names count_matrix_data/GSE96769_PeakFile.csv \
    --cell_type CLP \
    --output_path cicero_data/CLP_14999_peaks.bed

python post_filtering_peaks.py \
    --imputed_data results/cicero_test/imputed_data_14999.txt \
    --cell_names count_matrix_data/GSE96769_cell_names_matrix.csv \
    --peak_names count_matrix_data/GSE96769_PeakFile.csv \
    --cell_type HSC \
    --output_path cicero_data/HSC_14999_peaks.bed

DUMP_FOLDER=cicero_data
FOOTPRINTS_FOLDER=${DUMP_FOLDER}/found_footprints
mkdir -p ${FOOTPRINTS_FOLDER}

BAMS_FOLDER=${DUMP_FOLDER}/bams
python concatenate_bams.py --sra /home/akhtyamovpavel/Downloads/SraRunTable\ \(1\).txt \
    --cell_type HSC \
    --input_folder /home/akhtyamovpavel/Science/BioInfo/data/sra_bam_cleaned_shifted \
    --output_folder ${BAMS_FOLDER}

python concatenate_bams.py --sra /home/akhtyamovpavel/Downloads/SraRunTable\ \(1\).txt \
    --cell_type CLP \
    --input_folder /home/akhtyamovpavel/Science/BioInfo/data/sra_bam_cleaned_shifted \
    --output_folder ${BAMS_FOLDER}

rgt-hint footprinting --atac-seq --paired-end --organism hg38 \
    --output-location ${FOOTPRINTS_FOLDER} \
    --output-prefix hsc_14999 ${BAMS_FOLDER}/HSC_sorted.bam ${DUMP_FOLDER}/HSC_14999_peaks.bed

rgt-hint footprinting --atac-seq --paired-end --organism hg38 \
    --output-location ${FOOTPRINTS_FOLDER} \
    --output-prefix clp_14999 ${BAMS_FOLDER}/CLP_sorted.bam ${DUMP_FOLDER}/CLP_14999_peaks.bed

rgt-motifanalysis matching --organism=hg38 \
    --motif-dbs ~/Datasets/BioInfo/RgtData/motifs/hocomoco --filter "name:HUMAN" \
    --output-location ${FOOTPRINTS_FOLDER} --input-file ${FOOTPRINTS_FOLDER}/hsc_14999.bed

rgt-motifanalysis matching --organism=hg38 \
    --motif-dbs ~/Datasets/BioInfo/RgtData/motifs/hocomoco --filter "name:HUMAN" \
    --output-location ${FOOTPRINTS_FOLDER} --input-file ${FOOTPRINTS_FOLDER}/clp_14999.bed

rgt-hint differential --organism hg38 --bc --nc 8 --mpbs-files ${FOOTPRINTS_FOLDER}/hsc_14999_mpbs.bed,${FOOTPRINTS_FOLDER}/clp_14999_mpbs.bed \
    --reads-files ${BAMS_FOLDER}/hsc_sorted.bam,${BAMS_FOLDER}/clp_sorted.bam \
    --conditions HSC,CLP \
    --output-location ${FOOTPRINTS_FOLDER}/cicero_14999_HSC_vs_CLP --no-lineplots
