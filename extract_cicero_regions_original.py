import pandas as pd

from argparse import ArgumentParser

from tqdm import tqdm


import os
from scipy.io import mmread
import numpy as np
from tqdm import tqdm


def parse_args():
    parser = ArgumentParser('Extract peaks for Cicero')
    parser.add_argument('--folder', type=str, help='Path to folder with peaks, barcodes, count')
    parser.add_argument('--output', type=str, help='Path to output tsv file')

    return parser.parse_args()


def read_array(filename):
    elements = []
    with open(filename, 'r') as fp:
        for line in fp:
            elements.append(line.strip())

    return elements


def get_peaks(folder):
    assert os.path.exists(folder)

    peaks_file = os.path.join(folder, 'peaks.txt')
    counts_file = os.path.join(folder, 'counts.mtx')
    barcodes_file = os.path.join(folder, 'barcodes.txt')

    counts = mmread(counts_file)
    peaks = read_array(peaks_file)
    barcodes = read_array(barcodes_file)

    #print(counts.shape, peaks.shape, barcodes.shape)

    peak_idx = counts.row
    cell_idx = counts.col
    print(peak_idx)
    data = counts.data

    #peaks_to_counts = peaks[peak_idx]

    # print(peaks_to_counts.shape)
    #barcodes_to_counts = barcodes[cell_idx]

    return counts, peaks, barcodes
    #return pd.DataFrame([peaks_to_counts, barcodes_to_counts, data], columns=['peaks', 'barcodes', 'counts'])
    


def process_peaks(args):
    
    counts, peaks, barcodes = get_peaks(args.folder)

    peak_idx = counts.row
    cell_idx = counts.col
    data = counts.data

    with open(args.output, 'w') as fp:
        for index in tqdm(range(len(data)), total=len(data)):
            peak = peaks[peak_idx[index]]
            barcode = barcodes[cell_idx[index]]
            count = data[index]

            fp.write(f'{peak}\t{barcode}\t{count}\n')


def main():
    args = parse_args()
    process_peaks(args)


if __name__ == '__main__':
    main()
