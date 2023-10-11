# scATAC-seq preprocessing and imputation evaluation system for visualization, clustering and digital footprinting

## Requirements

* Python 3.7+
* Docker for running inside containers
* R 4.3.0 for running Cicero
* CUDA 11.0+

## Reproducing experiments

We support dense matrix format (TSV-files for count matrices) or sparse matrix format in [MEX](https://kb.10xgenomics.com/hc/en-us/articles/115000794686-How-is-the-MEX-format-used-for-the-gene-barcode-matrices-) format. We provide scripts converting matrices into the MEX format (next - 10X mode).

To convert matrix into the subset folder, please run the following script:
```
python subset_matrix.py \
    --input ../../Datasets/PBMC5K/input \
    --remain <number of peaks in dataset> \
    --mode dense \
    --count_matrix_file <path to name of the count matrix file> \
    --output ../../Datasets/PBMC5K/output/raw
```


### Preprocessing steps

Input folder: `preprocessing`

#### Subsampling method

```shell
python subsample_matrix.py \
    --input ../../Datasets/PBMC5K/input \
    --sample_ratio 0.2 \
    --mode 10X \
    --output ../../Datasets/PBMC5K/samples/0.2
```

#### Threshold method

```shell
python subset_matrix.py \
    --input ../../Datasets/PBMC5K/input \
    --remain 50000 \
    --mode 10X \
    --count_matrix_file matrix.mtx \
    --output ../../Datasets/PBMC5K/output/threshold
```

#### Boruta preprocessing
```shell
python get_boruta_matrix.py \
    --input ../../Datasets/PBMC5K/raw \
    --peaks_file peaks.txt \
    --barcodes_file barcodes.txt \
    --count_matrix_file matrix.mtx \
    --mode 10X \
    --labels_path ../../Datasets/PBMC5K/input/labels.tsv \
    --length_deep 1000  \
    --output_folder ../../Datasets/PBMC5K/output/boruta
```


#### Cicero preprocessing

```shell
python extract_cicero_regions_original.py \
    --folder ../../Datasets/PBMC5K/output/raw \
    --output ../../Datasets/PBMC5K/output/cicero/peaks_dumped.tsv
```

