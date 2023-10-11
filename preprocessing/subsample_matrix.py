import numpy as np

from argparse import ArgumentParser

from utils import get_peaks

import scipy.sparse
from scipy.io import mmwrite
import os


def parse_args():
    parser = ArgumentParser('subset sparse matrix')
    parser.add_argument('--input', required=True, help='Path to dataset')
    parser.add_argument('--sample_ratio', required=True, help='Count subsample ratio', type=float)
    parser.add_argument('--peaks_file', help='Name of peaks_file', default='peaks.txt')
    parser.add_argument('--barcodes_file', help='Name of barcodes file', default='barcodes.txt')
    parser.add_argument('--count_matrix_file', help='Name of count matrix file', default='matrix.mtx')
    parser.add_argument('--output', help='Path to output folder', required=True)
    parser.add_argument('--mode', help='Name of matrix', choices=('10X', 'dense'))
    return parser.parse_args()


def main(args):
    counts, peaks, barcodes = get_peaks(args)

    counts = scipy.sparse.coo_matrix(counts)

    indices = np.arange(0, counts.nnz)

    number_elements = counts.nnz

    remained_elements = int(number_elements * args.sample_ratio)
    remained_indices = np.random.choice(indices, remained_elements, replace=False)

    data = counts.data[remained_indices]
    row = counts.row[remained_indices]
    col = counts.col[remained_indices]

    nnz = remained_elements

    output_matrix = scipy.sparse.coo_matrix((data, (row, col)), shape=counts.shape)

    os.makedirs(args.output, exist_ok=True)

    output_count_file = os.path.join(args.output, 'matrix.mtx')
    output_peaks_file = os.path.join(args.output, 'peaks.txt')
    output_barcodes_file = os.path.join(args.output, 'barcodes.txt')
    mmwrite(output_count_file, scipy.sparse.csr_matrix(output_matrix))
    np.savetxt(output_peaks_file,
               peaks,
               delimiter="\n ",
               fmt='% s')
    np.savetxt(output_barcodes_file,
               barcodes,
               delimiter="\n ",
               fmt='% s')


if __name__ == '__main__':
    args = parse_args()
    print(args)
    main(args)
