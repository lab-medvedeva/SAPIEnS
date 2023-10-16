from argparse import ArgumentParser

import os
import pandas as pd
from scipy import sparse
from scipy.io import mmread, mmwrite
import numpy as np
from tqdm import tqdm

from utils import get_peaks


def parse_args():
    parser = ArgumentParser('Filter peaks by coaccess')
    parser.add_argument('--prefix', type=str, help='Path to peaks, found by Cicero')
    parser.add_argument('--input', type=str, help='Path to folder with data')
    # parser.add_argument('--threshold', type=float, help='Coaccess ratio threshold')
    parser.add_argument('--output', type=str, help='Output path to folder')
    parser.add_argument('--organism', type=str, help='Organism', choices=['mouse', 'human'], default='human')
    parser.add_argument('--remain', type=int, help='Num peaks to remain', default=50000)
    parser.set_defaults(mode='10X')
    parser.set_defaults(peaks_file='peaks.txt')
    parser.set_defaults(count_matrix_file='matrix.mtx')
    parser.set_defaults(barcodes_file='barcodes.txt')
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


def guess_threshold(coaccess_df: pd.DataFrame, num_remain: int):
    low_threshold = 0
    high_threshold = 1
    low_remain = 0
    high_remain = len(coaccess_df['Peak1'].unique())
    while high_remain - low_remain > 1 and high_threshold - low_threshold > 1e-5:
        mid_threshold = (low_threshold + high_threshold) / 2.0
        filtered_peak_names = coaccess_df[coaccess_df['coaccess'] > mid_threshold]['Peak1'].unique()
        mid_remain = len(filtered_peak_names)
        print(low_threshold, mid_threshold, high_threshold, low_remain, mid_remain, high_remain)
        if mid_remain > num_remain:
            low_threshold = mid_threshold
            high_remain = mid_remain
        else:
            high_threshold = mid_threshold
            low_remain = mid_remain

    print(low_threshold, mid_threshold, high_threshold, low_remain, mid_remain, high_remain) 
    return mid_threshold, filtered_peak_names


def main():
    args = parse_args()

    coaccess_df = read_coaccesses(args.prefix, args.organism)

    threshold, filtered_peak_names = guess_threshold(coaccess_df, args.remain)

    print(len(filtered_peak_names), 'remained after', threshold)

    counts, peaks, barcodes = get_peaks(args)

    peak_names_dict = {
        peak: index for index, peak in enumerate(peaks)            
    }
    filtered_peak_idx = sorted([peak_names_dict[peak] for peak in filtered_peak_names])
    print(counts.shape, len(peaks), len(barcodes))
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
