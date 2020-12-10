# Single-Cell ATAC-seq analysis via Latent feature Extraction
![](https://github.com/jsxlei/SCALE/wiki/png/model.png)

## Installation  

SCALE neural network is implemented in [Pytorch](https://pytorch.org/) framework.  
Running SCALE on CUDA is recommended if available.   
	
#### install from GitHub

	git clone git://github.com/jsxlei/SCALE.git
	cd SCALE
	python setup.py install
    
Installation only requires a few minutes.  

## Running pipeline

```
./run_pipeline.sh \
	--dump_folder cicero_test_pipeline \
	--peak_file count_matrix_data/GSE96769_PeakFile.csv \
	--count_matrix count_matrix_data/GSE96769_scATACseq_matrix.csv \
	--cicero_threshold 0.6 \
	--cell_names count_matrix_data/GSE96769_cell_names_matrix.csv \
	--scale_output cicero_test_pipeline/scale_result
```

## Running footprinting
```
./footprinting.sh \
	--dump_folder cicero_test_pipeline \
	--peak_file count_matrix_data/GSE96769_PeakFile.csv \
	--count_matrix count_matrix_data/GSE96769_scATACseq_matrix.csv \
	--cell_names count_matrix_data/GSE96769_cell_names_matrix.csv \
    --scale_output  results/cicero_test \
    --iteration 14999 \
    --cell_type_1 HSC \
    --cell_type_2 CLP \
    --sra ~/Downloads/SraRunTable\ \(1\).txt \
    --bams ~/Science/BioInfo/data/sra_bam_cleaned_shifted
```

# Running footprinting from ATLAS dataset

## Prepare raw peaks
```
python prepare_cicero_peaks.py \
    --dataset_path ../data/MouseAtlasPreprocessed/mouse_atlas \
    --label_path mouse_atlas_cicero/labels.txt \
    --num_peaks_threshold 30000 \
    --output_path mouse_cicero_pipeline/raw_peaks \
    --suffix raw_peaks
```

## Prepare Cicero peaks
```
python prepare_cicero_peaks.py \
    --dataset_path mouse_atlas_cicero \
    --label_path mouse_atlas_cicero/labels.txt \
    --num_peaks_threshold 30000 \
    --output_path mouse_cicero_pipeline/cicero_peaks \
    --suffix cicero_peaks
```

## Run footprinting on raw peaks
```
./footprinting_atlas.sh \
    --dump_folder mouse_cicero_pipeline/raw_peaks \
    --iteration raw --cell_type_1 Astrocytes \
    --cell_type_2 Hepatocytes \
    --bams /8tbsata/Science/BioInfo/data/MouseDataset/ConcatenatedBams \
    --organism mm9
```

## Run footprinting on Cicero peaks
```
./footprinting_atlas.sh \
    --dump_folder mouse_cicero_pipeline/cicero_peaks \
    --iteration cicero \
    --cell_type_1 Astrocytes \
    --cell_type_2 Hepatocytes \
    --bams /8tbsata/Science/BioInfo/data/MouseDataset/ConcatenatedBams --organism mm9
```

## Run footprinting on SCALE results
```
./footprinting_atlas.sh \
    --dump_folder mouse_cicero_pipeline \
    --scale_output results/mouse_atlas_cicero_k_30_test  \
    --iteration 9999 \
    --cell_type_1 Inhibitory_neurons \
    --cell_type_2 Purkinje_cells \
    --bams <path/to/bams> \
    --organism mm9 \
    --filter
```

## Run footprinting on all dataset

### For raw peaks

```
./footprinting_atlas_full_dataset.sh \
    --dump_folder mouse_cicero_pipeline \
    -out ../SCALE_results/mouse_atlas_cicero_k_30_test \
    --iteration raw \
    --cell_types cell_types.txt 
    --bams <path/to/bams> --organism mm9
```
If you use `raw` or `cicero` option, you should not set filter option

### For SCALE results

```
./footprinting_atlas_full_dataset.sh \
    --dump_folder mouse_cicero_pipeline \
    -out ../SCALE_results/mouse_atlas_cicero_k_30_test \
    --iteration 29999 \
    --cell_types cell_types.txt \
    --bams <path/to/bams> \
    --organism mm9 \
    --filter
```

## Draw postprocessing statistics
```
python draw_footprinting_statistics.py \
    --input mouse_cicero_pipeline/found_footprints/cicero_29999/differential_statistics.txt\
    --experiment_name cicero_29999 \
    --output_root charts
```

In folder `charts` you can find comparison chart and csv file with significant motif factors.

# Docker setup

## Building Docker container for gpu

```
docker build -t scale .
```

## Running Docker container for gpu
```
./run_docker_gpu.sh
```

Please, sure that nvidia-container-runtime is installed and configured for Docker. 
Links for installation are: 
* https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/user-guide.html#daemon-configuration-file
* https://nvidia.github.io/nvidia-container-runtime/


## Building Docker container for cpu
```
docker build -t scale-cpu -f Dockerfile-cpu .
```

## Running Docker container for cpu
```
./run_docker_cpu.sh
```
## Running pipeline from container:
```
python3 SCALE.py \
    --outdir results/mouse_atlas_cicero_k_30_test \
    -d data/mouse_atlas_cicero \
    -r data/mouse_atlas_cicero/labels.txt \
    -x 0.002 \
    --max_iter 50000 \
    --impute \
    --impute_iteration 10000 \
    -k 30 \
    --reference_type atlas
```

## Quick Start

#### Input
* either a **count matrix file**:  
	* row is peak and column is barcode, in **txt** / **tsv** (sep=**"\t"**) or **csv** (sep=**","**) format
* or a **folder** contains **three files**:   
	* **count file**: count in **mtx** format, filename contains key word **"count"** / **"matrix"**    
	* **peak file**: 1-column of peaks **chr_start_end**, filename contains key word **"peak"**  
	* **barcode file**: 1-column of barcodes, filename contains key word **"barcode"**

#### Run
with known cluster number k:  

    SCALE.py -d [input] -k [k]

with estimated cluster number k by SCALE if k is unknown: 

    SCALE.py -d [input]

#### Output
Output will be saved in the output folder including:
* **model.pt**:  saved model to reproduce results cooperated with option --pretrain
* **feature.txt**:  latent feature representations of each cell used for clustering or visualization
* **cluster_assignments.txt**:  clustering assignments of each cell
* **emb_tsne.txt**:  2d t-SNE embeddings of each cell
* **emb_tsne.pdf**:  visualization of 2d t-SNE embeddings of each cell

#### Imputation  
Get binary imputed data in folder **binary_imputed** with option **--binary** (recommended for saving storage)

    SCALE.py -d [input] --binary  
    
or get numerical imputed data in file **imputed_data.txt** with option **--impute**

    SCALE.py -d [input] --impute
     
#### Useful options  
* save results in a specific folder: [-o] or [--outdir] 
* embed feature by tSNE or UMAP: [--emb]  TSNE/UMAP
* filter rare peaks if the peaks quality if not good or too many, default is 0.01: [-x]
* filter low quality cells by valid peaks number, default 100: [--min_peaks]  
* modify the initial learning rate, default is 0.002: [--lr]  
* change iterations by watching the convergence of loss, default is 30000: [-i] or [--max_iter]  
* change random seed for parameter initialization, default is 18: [--seed]
* binarize the imputation values: [--binary]
* run with scRNA-seq dataset: [--log_transform]
	
#### Note    
If come across the nan loss, 
* try another random seed
* filter peaks with harsher threshold, e.g. -x 0.04 or 0.06
* filter low quality cells, e.g. --min_peaks 400 or 600
* change the initial learning rate, e.g. --lr 0.0002 
	

#### Help
Look for more usage of SCALE

	SCALE.py --help 

Use functions in SCALE packages.

	import scale
	from scale import *
	from scale.plot import *
	from scale.utils import *
	
#### Running time
<p float="left">
  <img src="https://github.com/jsxlei/SCALE/wiki/png/runtime.png" width="350" />
  <img src="https://github.com/jsxlei/SCALE/wiki/png/memory.png" width="350" /> 
</p>

#### Data availability  
Download all the **provided datasets** [[Download]](https://cloud.tsinghua.edu.cn/d/eb4371c556bc46ef8516/) 

## Tutorial


**[Tutorial Forebrain](https://github.com/jsxlei/SCALE/wiki/Forebrain)**   Run SCALE on dense matrix **Forebrain** dataset (k=8, 2088 cells)
	
**[Tutorial Mouse Atlas](https://github.com/jsxlei/SCALE/wiki/Mouse-Atlas)**   Run SCALE on sparse matrix **Mouse Atlas** dataset (k=30, ~80,000 cells)


## Reference
[Lei Xiong, Kui Xu, Kang Tian, Yanqiu Shao, Lei Tang, Ge Gao, Michael Zhang, Tao Jiang & Qiangfeng Cliff Zhang. SCALE method for single-cell ATAC-seq analysis via latent feature extraction. Nature Communications, (2019).](https://www.nature.com/articles/s41467-019-12630-7)
./run_pipeline.sh --dump_folder cicero_test_pipeline --peak_file count_matrix_data/GSE96769_PeakFile.csv --count_matrix count_matrix_data/GSE96769_scATACseq_matrix.csv --cicero_threshold 0.6 --cell_names count_matrix_data/GSE96769_cell_names_matrix.csv --scale_output cicero_test_pipeline/scale_result
