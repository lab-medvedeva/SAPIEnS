import os
from scipy.io import mmread
import numpy as np
from tqdm import tqdm
from argparse import ArgumentParser
import pandas as pd
from boruta import BorutaPy
from sklearn.ensemble import RandomForestClassifier
import scipy.sparse
from utils import get_peaks
import sys


def read_array(filename):
    elements = []
    with open(filename, 'r') as fp:
        for line in fp:
            elements.append(line.strip())

    return elements


def fit_boruta(counts, peaks, labels, percentage=95):
    rf = RandomForestClassifier(n_jobs=32, class_weight='balanced', max_depth=5)

    # define Boruta feature selection method
    feat_selector = BorutaPy(rf, n_estimators='auto', verbose=2, random_state=1, perc=percentage)

    feat_selector.fit(counts.toarray(), labels)
    return counts.T[feat_selector.support_], peaks[feat_selector.support_]


def parse_args():
    parser = ArgumentParser('Run Boruta pipeline')
    parser.add_argument('--input', required=True, help='Path to dataset')
    parser.add_argument('--peaks_file', help='Name of peaks_file', default='peaks.txt')
    parser.add_argument('--barcodes_file', help='Name of barcodes file', default='barcodes.txt')
    parser.add_argument('--count_matrix_file', help='Name of count matrix file', default='matrix.mtx')
    parser.add_argument('--mode', choices=('10X', 'dense'), required=True)
    parser.add_argument('--labels_path', required=True, help='Path to labels')
    parser.add_argument('--length_deep', type=int, help='Length of coverage in Boruta', default=10000)
    parser.add_argument('--output_folder', required=True, help='Path to output folder')
    parser.add_argument('--percentage', required=True, type=int, help='Path to parse input data', default=95)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    print(args)
    print('Reading peaks')
    counts, peaks, barcodes = get_peaks(args)
    labels = pd.read_csv(args.labels_path, sep='\t', header=None)

    barcodes_isin_labels = np.isin(barcodes, labels)
    counts = counts[:, barcodes_isin_labels]
    print(counts.shape)
    matrix_length = counts.shape[0]
    length_deep = args.length_deep

    counts_filtered_set = []
    peaks_filtered_set = []
    labels_columns = labels[1]
    sys.stdout.flush()
    sys.stderr.flush()
    for index in range(0, matrix_length, length_deep):
        count_submatrix = counts[index: index + length_deep]

        peaks_submatrix = peaks[index: index + length_deep]

        counts_filtered, peaks_filtered = fit_boruta(
            count_submatrix.T,
            peaks_submatrix,
            labels_columns,
            percentage=args.percentage
        )

        counts_filtered_set.append(counts_filtered)
        peaks_filtered_set.append(peaks_filtered)
        sys.stdout.flush()
        sys.stderr.flush()

    counts_boruta = scipy.sparse.vstack(counts_filtered_set)
    peaks_boruta = np.concatenate(peaks_filtered_set)

    folder = args.output_folder
    os.makedirs(folder, exist_ok=True)

    peaks_path = os.path.join(folder, 'peaks.txt')

    barcodes_path = os.path.join(folder, 'barcodes.txt')
    pd.DataFrame(list(barcodes)).to_csv(barcodes_path, index=None, header=None)
    pd.DataFrame(list(peaks_boruta)).to_csv(peaks_path, index=None, header=None)

    scipy.io.mmwrite(os.path.join(folder, 'matrix.mtx'), counts_boruta)
