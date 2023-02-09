import os
import scipy
from scipy.io import mmread
import pandas as pd
import numpy as np
from argparse import ArgumentParser


def read_array(filename):
    elements = []
    with open(filename, 'r') as fp:
        for line in fp:
            elements.append(line.strip())

    return elements


def save_array(filename, elements):
    with open(filename, 'w') as fp:
        for element in elements:
            fp.write(f'{element}\n')


def get_peaks(folder, peaks_file='peaks.txt', counts_file='counts.mtx', barcodes_file='barcodes.txt'):
    assert os.path.exists(folder)

    peaks_file = os.path.join(folder, peaks_file)
    counts_file = os.path.join(folder, counts_file)
    barcodes_file = os.path.join(folder, barcodes_file)

    counts = mmread(counts_file)
    peaks = read_array(peaks_file)
    barcodes = read_array(barcodes_file)

    peak_idx = counts.row
    cell_idx = counts.col
    data = counts.data

    return counts.tocsr(), peaks, barcodes


def read_csv(path):
    print(path)
    if ('.txt' in path) or ('tsv' in path):
        sep = '\t'
    elif '.csv' in path:
        sep = '\t'
    else:
        raise ValueError("File {} not in format txt or csv".format(path))
    if 'txt' in path:
        data = pd.read_csv(path, sep=sep, index_col=0).T.astype('float32')
        genes = data.columns.values
        barcode = data.index.values
    elif 'tsv' in path or 'csv' in path:
        data = pd.read_csv(path, sep=sep, index_col=0)
        print(data.shape)
        data = data.astype('float32')
        genes = data.index.values
        barcode = data.columns.values
    return scipy.sparse.csr_matrix(data.values), genes, barcode


def parse_args():
    parser = ArgumentParser('Split count matrix in 10X format to cell type peaks')
    parser.add_argument('--input', required=True, help='Path to input folder')
    parser.add_argument('--counts_file', required=True, help='Count matrix file', default='matrix.mtx')
    parser.add_argument('--peaks_file', help='Path to peaks file', default='peaks.txt')
    parser.add_argument('--barcodes_file', help='Path to barcodes file', default='barcodes.txt')
    parser.add_argument('--labels', required=True, help='Path to labels')
    parser.add_argument('--iteration', required=True, help='Iteration to save')
    parser.add_argument('--mode', required=True, choices=['10X', 'dense'])
    return parser.parse_args()


def main(args):
    if args.mode == '10X':
        counts, peaks, barcodes = get_peaks(
            args.input,
            counts_file=args.counts_file,
            peaks_file=args.peaks_file,
            barcodes_file=args.barcodes_file
        )
    else:
        counts, peaks, barcodes = read_csv(os.path.join(args.input, args.counts_file))
    
    print(counts.shape)
    labels = pd.read_csv(args.labels, header=None, sep='\t')
    
    for cell_type in labels[1].unique():
        print(cell_type)
        indices = labels[labels[1] == cell_type].index
        print(indices.shape)

        suitable_counts = counts[:, indices]
        print(suitable_counts.shape)

        count_peaks = suitable_counts.sum(axis=1)
        selected_peak_indices = count_peaks > 0

        flattened_indices = np.array(selected_peak_indices.flatten()).flatten()
        selected_peaks = np.array(peaks)[flattened_indices]
        print(selected_peaks.shape)
        save_array(
            filename=os.path.join(args.input, f'imputed_data_imputed_{args.iteration}_{cell_type.replace(" ", "_").replace("/", "_")}.txt'),
            elements=selected_peaks
        )
    


if __name__ == '__main__':
    args = parse_args()
    main(args)
