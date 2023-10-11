import os
from scipy.io import mmread
import pandas as pd
import numpy as np


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
    print(args.mode)
    if args.mode == '10X':
        peaks_file = os.path.join(args.input, args.peaks_file)
        counts_file = os.path.join(args.input, args.count_matrix_file)
        barcodes_file = os.path.join(args.input, args.barcodes_file)
        print(counts_file)
        barcodes = read_array(barcodes_file)
        peaks = read_array(peaks_file)
        counts = mmread(counts_file)
        print(counts.shape)
        if len(peaks) !=  counts.shape[0]:
            counts = counts.T
        print(counts.shape)
        return counts.tocsr(), np.array(peaks), np.array(barcodes)
    else:
        counts_file = os.path.join(args.input, args.count_matrix_file)

        counts = pd.read_csv(counts_file, sep='\t', index_col=0)
        peaks = counts.index

        return counts.values, peaks, counts.columns