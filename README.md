# scATAC-seq preprocessing and imputation evaluation system for visualization, clustering and digital footprinting

## Requirements

* Python 3.7+
* Docker for running inside containers
* R 4.3.0 for running Cicero
* CUDA 11.0+

## Installation steps

We represent three options for you to install evaluation system.

### Option 1. Docker images
We prepared Docker images to run evaluation system in Docker. Please, complete this steps using Docker images. CPU version:
```
docker pull akhtyamovpavel/sapiens:cpu
docker run -v <full path to datasets>:/home/ubuntu/Datasets --name sapiens -it -d akhtyamovpavel akhtyamovpavel/sapiens:cpu bash
```
GPU version (SCALE supported)
```
docker pull akhtyamovpavel/sapiens:gpu
docker run --gpus all --shm-size 10G -v <full path to datasets>:/home/ubuntu/Datasets --name sapiens -it -d akhtyamovpavel akhtyamovpavel/sapiens:gpu bash
```

### Option 2. Build Docker image
1. CPU version:
```
docker build -f Dockerfile-cpu -t lab-medvedeva/sapiens:cpu .
docker run -v <full path to datasets>:/home/ubuntu/Datasets --name sapiens -it -d akhtyamovpavel akhtyamovpavel/sapiens:cpu bash
```
2. GPU version:
```
docker build -f Dockerfile -t lab-medvedeva/sapiens:gpu .
docker run --gpus all --shm-size 10G -v <full path to datasets>:/home/ubuntu/Datasets --name sapiens -it -d akhtyamovpavel/sapiens:gpu bash
```

### Option 2. Installation using conda + pip

1. Install Miniconda using this [link](https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html)
2. Create environment:
```
conda create -n sapiens python=3.10 r-base=4.3.0
```
3. Activate environment:
```
conda activate sapiens
```
4. Install packages in your environment:
```
pip install -r requirements.txt
```
5. (GPU required) Install pytorch for your environment:
```
pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 --extra-index-url https://download.pytorch.org/whl/cu113
```
6. Install Cicero:
```
Rscript install.R
```


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

## Input folders structure

```
input
├── barcodes.txt
├── labels.tsv
├── matrix.mtx
└── peaks.txt
```

The structure of Labels file:
* Tab-separated file
* Contains two columns:
  * Cell id
  * Cell type

The structure of barcodes, peaks, and labels files follows 10X structure. We designed to accept any types of prefixes using the following options:
```
--peaks_file - path to peaks file (barcodes.txt)
--count_matrix_file - path to count matrix file (matrix.mtx)
--peaks_file - path to count peaks file (peaks.txt)
```

## Output folders

```
output
├── boruta
├── cicero
├── raw
├── scale_boruta
├── scale_cicero
├── scale_threshold
├── scopen_boruta
├── scopen_cicero
├── scopen_threshold
└── threshold
```

These folders are needed to generate metrics evaluation.

### Preprocessing steps

Input folder: `preprocessing`


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
    --input ../../Datasets/PBMC5K/output/raw \
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
./run_cicero_pipeline.sh ../../Datasets/PBMC5K/output human 50000
```
It takes input folder and selects peaks for datasets.

#### Subsampling method (for ablation study)

```shell
python subsample_matrix.py \
    --input ../../Datasets/PBMC5K/input \
    --sample_ratio 0.2 \
    --mode 10X \
    --output ../../Datasets/PBMC5K/samples/0.2/output/raw
```

## Imputation methods
Folder: [imputation](/imputation)

### scOpen

Full datasets:
```
./02_run_scopen_full.sh PBMC5K
```
Subsampled datasets:
```
02_run_scopen_subsampled.sh PBMC5K
```

### Clustering analysis

Input folder: [clustering](/clustering).

Processing datasets:
```
./run_all_clustering_sbatch.sh ../../Datasets/PBMC5K/ ../../Datasets/PBMC5K/input/labels.tsv
```

Script will check whether `sbatch` is available. If you do not have sbatch, you will be notified that script will be executed in 10 seconds!

After collecting the results the folder `clustering` should be generated with contents:

```shell
./clustering/
|-- boruta
|-- cicero
|-- scale_boruta
|-- scale_cicero
|-- scale_threshold
|-- scopen_boruta
|-- scopen_cicero
|-- scopen_threshold
`-- threshold
```

For each folder you will be found two files:
* `metrics.json` - JSON document containing 12 metrics
* `metrics.pkl` - Pickle-formatted values containing PCA, tSNE and UMAP scatterplots for visualization.

For `scale` method the folder will contain:

```shell
clustering/scale_boruta/
|-- 10000
|   |-- metrics.json
|   `-- metrics.pkl
|-- 100000
|   |-- metrics.json
|   `-- metrics.pkl
|-- 20000
|   |-- metrics.json
|   `-- metrics.pkl
|-- 30000
|   |-- metrics.json
|   `-- metrics.pkl
|-- 40000
|   |-- metrics.json
|   `-- metrics.pkl
|-- 50000
|   |-- metrics.json
|   `-- metrics.pkl
|-- 60000
|   |-- metrics.json
|   `-- metrics.pkl
|-- 70000
|   |-- metrics.json
|   `-- metrics.pkl
|-- 80000
|   |-- metrics.json
|   `-- metrics.pkl
`-- 90000
    |-- metrics.json
    `-- metrics.pkl
```

For scOpen method folder structure will be generated:
```shell
clustering/scopen_boruta/
|-- matrix_0.0
|   |-- metrics.json
|   `-- metrics.pkl
|-- matrix_0.1
|   |-- metrics.json
|   `-- metrics.pkl
|-- matrix_0.2
|   |-- metrics.json
|   `-- metrics.pkl
|-- matrix_0.3
|   |-- metrics.json
|   `-- metrics.pkl
|-- matrix_0.4
|   |-- metrics.json
|   `-- metrics.pkl
|-- matrix_0.5
|   |-- metrics.json
|   `-- metrics.pkl
|-- matrix_0.6
|   |-- metrics.json
|   `-- metrics.pkl
|-- matrix_0.7
|   |-- metrics.json
|   `-- metrics.pkl
|-- matrix_0.8
|   |-- metrics.json
|   `-- metrics.pkl
|-- matrix_0.9
|   |-- metrics.json
|   `-- metrics.pkl
`-- matrix_1.0
```

#### Get clustering metrics
```
python3 collect_metrics.py --input ../../Datasets/PBMC5K/ --output ../../Datasets/PBMC5K/output_metrics
```



### Footprinting analysis

Folder [footprinting](/footprinting)
```shell
./footprinting_atlas_full_dataset.sh \
    --dump_folder ../../Datasets/HSC/footprinting/threshold \
    --scale_output ../../Datasets/GSE96769/output/threshold
    --iteration 0 --cell_types ../cell_types_hema.txt \
    --organism hg19 \
    --filter --bams <path to bams file>
```
