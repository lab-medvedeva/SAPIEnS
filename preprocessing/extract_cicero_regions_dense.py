import pandas as pd

from argparse import ArgumentParser

from tqdm import tqdm


import os
from scipy.io import mmread
import numpy as np
from tqdm import tqdm


def parse_args():
    parser = ArgumentParser('Extract peaks for Cicero')
    parser.add_argument('--input', type=str, help='Path with csv file with counts')
    parser.add_argument('--output', type=str, help='Path to output tsv file')

    return parser.parse_args()


def read_array(filename):
    elements = []
    with open(filename, 'r') as fp:
        for line in fp:
            elements.append(line.strip())

    return elements


def get_peaks(filename, fp):
    assert os.path.exists(filename)


    sep = ',' if filename.endswith('.csv') else '\t'

    df = pd.read_csv(filename, sep=sep, index_col=0).astype(int)

    for cell_name in tqdm(df.columns):
        cell_series = df[cell_name]

        filtered_series = cell_series[cell_series > 0]

        for peak, value in filtered_series.items():
            fp.write(f'{peak}\t{cell_name}\t{value}\n')


def process_peaks(args):
    
    with open(args.output, 'w') as fp:
        get_peaks(args.input, fp)


def main():
    args = parse_args()
    process_peaks(args)


if __name__ == '__main__':
    main()
