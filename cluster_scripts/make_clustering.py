import os
from scipy.io import mmread
import numpy as np
import pandas as pd
from tqdm import tqdm
import umap
from argparse import ArgumentParser
from scipy.sparse.linalg import svds
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.cluster import adjusted_rand_score
from sklearn.metrics.cluster import adjusted_mutual_info_score
from sklearn.metrics.cluster import homogeneity_score, silhouette_score
from sklearn.metrics import f1_score
from sklearn.manifold import TSNE
import scanpy as sc
import json
import scipy.sparse
import pickle


def read_array(filename):
    elements = []
    with open(filename, 'r') as fp:
        for line in fp:
            elements.append(line.strip())

    return elements



def get_peaks(args):
    assert os.path.exists(args.input)

    counts_file = os.path.join(args.input, args.count_matrix_file)
    
    if args.mode == '10X':
        peaks_file = os.path.join(args.input, args.peaks_file)
        barcodes_file = os.path.join(args.input, args.barcodes_file)

        counts = mmread(counts_file)
        peaks = read_array(peaks_file)
        barcodes = read_array(barcodes_file)


        peak_idx = counts.row
        cell_idx = counts.col
    else:
        
        df = pd.read_csv(counts_file, sep='\t', index_col=0)
        print(counts_file, df.shape)
        peaks = list(df.index)
        barcodes = list(df.columns)

        counts = scipy.sparse.csr_matrix(df.values)


    return counts.tocsr(), np.array(peaks), np.array(barcodes)


def get_feature_matrix(counts, num_features=150):
    transformer = TfidfTransformer()
    tf_idf_matrix = transformer.fit_transform(counts.T)
    if num_features == 0:
        return tf_idf_matrix
    u, d, vt = svds(tf_idf_matrix, k=num_features)
    feature_matrix = u @ np.diag(d)
    
    return feature_matrix


def getNClusters(adata,n_cluster,range_min=0,range_max=3,max_steps=20):
    this_step = 0
    this_min = float(range_min)
    this_max = float(range_max)
    while this_step < max_steps:
        print('step ' + str(this_step))
        this_resolution = this_min + ((this_max-this_min)/2)
        sc.tl.louvain(adata,resolution=this_resolution)
        this_clusters = adata.obs['louvain'].nunique()
        
        print('got ' + str(this_clusters) + ' at resolution ' + str(this_resolution))
        
        if this_clusters > n_cluster:
            this_max = this_resolution
        elif this_clusters < n_cluster:
            this_min = this_resolution
        else:
            return(this_resolution, adata)
        this_step += 1
    
    print('Cannot find the number of clusters')
    print('Clustering solution from last iteration is used:' + str(this_clusters) + ' at resolution ' + str(this_resolution))


def parse_args():
    parser = ArgumentParser('Make clustering results')
    parser.add_argument('--input', required=True, help='Path to dataset')
    parser.add_argument('--peaks_file', help='Name of peaks_file', default='peaks.txt')
    parser.add_argument('--barcodes_file', help='Name of barcodes file', default='barcodes.txt')
    parser.add_argument('--count_matrix_file', help='Name of count matrix file', default='matrix.mtx')
    parser.add_argument('--labels_path', required=True, help='Path to labels dataset')
    parser.add_argument('--output', required=True, help='Path to output metrics file')
    parser.add_argument('--mode', required=True, choices=('10X', 'dense'))
    parser.add_argument('--num_features', required=False, help='Number of features for PCA', default=150, type=int)
    return parser.parse_args()


def get_scores(labels_pred, labels_true):
    return {
        'ari': adjusted_rand_score(labels_true, labels_pred),
        'ami': adjusted_mutual_info_score(labels_true, labels_pred),
        'homogeneity': homogeneity_score(labels_true, labels_pred)
    }


def get_scores_embedding(feature_matrix, labels_true):

    tsne_embedding = TSNE(n_components=2, random_state=2022).fit_transform(feature_matrix)
    reducer = umap.UMAP()
    umap_embedding = reducer.fit_transform(feature_matrix)
    return {
        'tsne_score': float(silhouette_score(tsne_embedding, labels_true)),
        'umap_score': float(silhouette_score(umap_embedding, labels_true)),
        'pca_score': float(silhouette_score(feature_matrix, labels_true))
    }, {
        'tsne_embedding': tsne_embedding,
        'pca_embedding': feature_matrix,
        'umap_embedding': umap_embedding
    }

def save_json(metrics, file):
    with open(file, 'w') as fp:
        json.dump(metrics, fp, indent=4, sort_keys=True)


def save_embeddings(embeddings, file):
    with open(file.replace('.json', '.pkl'), 'wb') as fp:
        pickle.dump(embeddings, fp)


def main(args):
    print(args)
    labels = pd.read_csv(args.labels_path, sep='\t', header=None)

    counts, peaks, barcodes = get_peaks(args)
    print(args.input)
    print(counts.shape)
    print(peaks.shape)
    print(labels.shape)
    print(barcodes.shape)

    barcodes_isin_labels = np.isin(barcodes, labels)

    print(labels.shape)
    feature_matrix = get_feature_matrix(counts[:, barcodes_isin_labels], num_features=args.num_features)
    labels_column = labels[1]
    
    num_clusters = len(np.unique(labels_column))

    print(num_clusters)
    ann_data = sc.AnnData(feature_matrix)
    print(ann_data.X.shape)
    sc.pp.neighbors(ann_data, n_neighbors=15,use_rep='X')
    getNClusters(ann_data, num_clusters)

    kmeans = KMeans(n_clusters=num_clusters, random_state=2022).fit(feature_matrix)
    hc = AgglomerativeClustering(n_clusters=num_clusters).fit(feature_matrix)

    metrics_distance, embedding_distance = get_scores_embedding(feature_matrix, labels_column)

    metrics = {
        'kmeans': get_scores(kmeans.labels_, labels_column),
        'hc': get_scores(hc.labels_, labels_column),
        'louvain': get_scores(ann_data.obs['louvain'], labels_column),
        'distance': metrics_distance
    }

    save_json(metrics, args.output)
    save_embeddings(embedding_distance, args.output)
    print(metrics)
    

if __name__ == '__main__':
    args = parse_args()
    print(args.input)
    main(args)
