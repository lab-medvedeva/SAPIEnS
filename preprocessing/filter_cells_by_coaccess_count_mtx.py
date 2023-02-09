from argparse import ArgumentParser

import os
import pandas as pd
from scipy import sparse
from scipy.io import mmread, mmwrite
import numpy as np
from tqdm import tqdm

def parse_args():
    parser = ArgumentParser('Filter peaks by coaccess')
    parser.add_argument('--prefix', type=str, help='Path to peaks, found by Cicero')
    parser.add_argument('--folder', type=str, help='Path to folder with data')
    parser.add_argument('--threshold', type=float, help='Coaccess ratio threshold')
    parser.add_argument('--output', type=str, help='Output path to folder')
    parser.add_argument('--organism', type=str, help='Organism', choices=['mouse', 'human'], default='human')
    return parser.parse_args()

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


def read_coaccesses(prefix, organism):
    if organism == 'human':
        chromosomes = list(range(1, 23))
    else:
        chromosomes = list(range(1, 20))
    chromosomes += ['X'] #, 'Y']

    coaccesses = []
    for chromosome in chromosomes:
        df = pd.read_csv(f'{prefix}chr{chromosome}.csv')
        coaccesses.append(df)

    coaccess_df = pd.concat(coaccesses)

    return coaccess_df


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

def main():
    args = parse_args()

    coaccess_df = read_coaccesses(args.prefix, args.organism)

    filtered_peak_names = coaccess_df[coaccess_df['coaccess'] > args.threshold]['Peak1'].unique()

    print(len(filtered_peak_names), 'remained after', args.threshold)

    counts, peaks, barcodes = get_peaks(args.folder)

    peak_names_dict = {
        peak: index for index, peak in enumerate(peaks)            
    }
    filtered_peak_idx = sorted([peak_names_dict[peak] for peak in filtered_peak_names])
    print(filtered_peak_idx[:10])

    counts_matrix = sparse.csr_matrix(counts)[filtered_peak_idx]

    peaks_new = []

    for peak_idx in filtered_peak_idx:
        peaks_new.append(peaks[peak_idx])

    os.makedirs(args.output, exist_ok=True)
    
    save_array(os.path.join(args.output, 'peaks.txt'), peaks_new)

    save_array(os.path.join(args.output, 'barcodes.txt'), barcodes)

    mmwrite(os.path.join(args.output, 'counts.mtx'), counts_matrix)    


if __name__ == '__main__':
    main()
