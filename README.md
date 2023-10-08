# scATAC-seq preprocessing and imputation evaluation system for visualization, clustering and digital footprinting

## Requirements

* Python 3.7+
* Docker for running inside containers
* R 4.3.0 for running Cicero
* CUDA 11.0+

## Reproducing experiments

### Preprocessing steps

Input folder: `preprocessing`

#### Threshold method

```shell
python subset_matrix.py \
    --input ../../Datasets/Splenocyte/input \
    --remain 100000 \
    --mode 10X \
    --count_matrix_file matrix.mtx \
    --output ../../Datasets/Splenocyte/output/threshold
```

#### Boruta preprocessing
```shell
python get_boruta_matrix.py \
    --input ../../Datasets/Splenocyte/input/ \
    --peaks_file peaks.txt \
    --barcodes_file barcodes.txt \
    --count_matrix_file matrix.mtx \
    --mode 10X \
    --labels_path ../../Datasets/Splenocyte/input/labels.tsv \
    --length_deep 1000 
    --output_folder ../../Datasets/Splenocyte/output/boruta
```


#### Cicero preprocessing

```shell
python extract_cicero_regions_original.py \
    --folder ../../Datasets/Splenocyte/output/raw \
    --output ../../Datasets/Splenocyte/output/cicero/peaks_dumped.tsv
```

