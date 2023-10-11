import pandas as pd
import os
from argparse import ArgumentParser
from scipy.io import mmread
from scipy.io import mmwrite
import numpy as np
import scipy.sparse

from utils import get_peaks


def parse_args():
    parser = ArgumentParser('subset sparse matrix')
    parser.add_argument('--input', required=True, help='Path to dataset')
    parser.add_argument('--remain', required=True, help='int number', type=int)
    parser.add_argument('--peaks_file', help='Name of peaks_file', default='peaks.txt')
    parser.add_argument('--barcodes_file', help='Name of barcodes file', default='barcodes.txt')
    parser.add_argument('--count_matrix_file', help='Name of count matrix file', default='matrix.mtx')
    parser.add_argument('--output', help='Path to output folder', required=True)
    parser.add_argument('--mode', help='Name of matrix', choices=('10X', 'dense'))
    return parser.parse_args()


def main(args):
    """

    :param args: Input paths to counts file
    :return: Subset of counts, filtered by peaks appearing in specified remain of cells
    """
    counts, peaks, barcodes = get_peaks(args)
    binarized = (counts > 0).astype(np.int32)
    print(counts.shape, peaks.shape)
    sums = np.array(binarized.sum(axis=1))
    if args.mode == '10X':
        perc = (sums*100.0 /counts.shape[1])[:, 0]
    else:
        perc = sums * 100 / counts.shape[1]

    print(perc.max(), perc.min(), perc.shape)
    print(sums.max(), sums.min(), sums.shape, counts.shape[1])
    index_percents = np.argsort(perc)

    list_of_index = sorted(index_percents[-args.remain:])
    print(list_of_index[:10], len(list_of_index))
    subset = counts[list_of_index, :]
    assert os.path.exists(args.input)

    os.makedirs(args.output, exist_ok=True)

    output_count_file = os.path.join(args.output, 'matrix.mtx')
    output_peaks_file = os.path.join(args.output, 'peaks.txt')
    output_barcodes_file = os.path.join(args.output, 'barcodes.txt')
    mmwrite(output_count_file, scipy.sparse.csr_matrix(subset))
    new_peaks = []
    for i in list_of_index:
        new_peaks.append(peaks[i])
    print(len(new_peaks))
    print(len(barcodes))
    np.savetxt(output_peaks_file,
               new_peaks,
               delimiter="\n ",
               fmt='% s')
    np.savetxt(output_barcodes_file,
               barcodes,
               delimiter="\n ",
               fmt='% s')



if __name__ == '__main__':
    args = parse_args()
    print(args.input)
    main(args)

