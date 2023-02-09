import os
from argparse import ArgumentParser
from scipy.io import mmread
from scipy.io import mmwrite
import numpy as np
import scipy.sparse


def parse_args():
    """

    :return: input arguments
    """
    parser = ArgumentParser('subset sparse matrix')
    parser.add_argument('--input', required=True, help='Path to dataset')
    parser.add_argument('--percent', required=True, help='int number', type=int)
    parser.add_argument('--peaks_file', help='Name of peaks_file', default='peaks.txt')
    parser.add_argument('--barcodes_file', help='Name of barcodes file', default='barcodes.txt')
    parser.add_argument('--count_matrix_file', help='Name of count matrix file', default='matrix.mtx')
    return parser.parse_args()


def read_array(filename):
    """

    :param filename: peaks file
    :return: list of peaks
    """
    elements = []
    with open(filename, 'r') as fp:
        for line in fp:
            elements.append(line.strip())

    return elements


def get_peaks(args):
    """

    :param args: read counts file
    :return: readable format of counts
    """
    assert os.path.exists(args.input)
    peaks_file = os.path.join(args.input, args.peaks_file)
    counts_file = os.path.join(args.input, args.count_matrix_file)
    print(counts_file)
    peaks = read_array(peaks_file)
    counts = mmread(counts_file)
    return counts.tocsr(), np.array(peaks)


def main(args):
    """

    :param args: Input paths to counts file
    :return: Subset of counts, filtered by peaks appearing in specified percent of cells
    """
    counts, peaks = get_peaks(args)
    print(counts.shape, peaks.shape)
    sums = counts.sum(axis=1)
    perc = sums*100/counts.shape[1]

    list_of_index = []
    for i in range(0, len(perc)):
        if perc[i] > int(args.percent):
            list_of_index.append(i)
    subset = counts.tocsr()[list_of_index, :]
    assert os.path.exists(args.input)
    mmwrite(os.path.join(args.input, f"matrix_subset_{args.percent}.mtx"), subset)
    new_peaks = []
    for i in list_of_index:
        new_peaks.append(peaks[i])
    print(len(new_peaks))
    np.savetxt(os.path.join(args.input, f"peaks_subset_{args.percent}.txt"),
               new_peaks,
               delimiter="\n ",
               fmt='% s')


if __name__ == '__main__':
    args = parse_args()
    print(args.input)
    main(args)

