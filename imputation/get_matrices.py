import pandas as pd
import numpy as np
import gc
import os
from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser('Obtain matrices for scOpen')
    parser.add_argument('--peaks', required=True, help='Path to peaks')
    parser.add_argument('--barcodes', required=True, help='Path to barcodes')
    parser.add_argument('--format', required=True, help='Mode to load', choices=('dense', '10x'))
    parser.add_argument('--output_folder', required=True, help='Path to output folder')
    return parser.parse_args()


def main(args):
    barcodes = pd.read_csv(args.barcodes, sep='\t', index_col=0)
    peaks = pd.read_csv(args.peaks, sep='\t', index_col=0)

    peaks_barcodes = peaks.values @ barcodes.values

    os.makedirs(args.output_folder, exist_ok=True)
    for quantile_level in np.linspace(0, 1, 11):
        quantile = np.quantile(peaks_barcodes, q=quantile_level)
        imputed_matrix = (peaks_barcodes > quantile).astype(np.uint8)
        df = pd.DataFrame(imputed_matrix, columns=barcodes.columns, index=peaks.index)

        matrix_name = f'matrix_{round(quantile_level, 1)}'

        matrix_folder = os.path.join(args.output_folder, matrix_name)

        os.makedirs(matrix_folder, exist_ok=True)

        matrix_path = os.path.join(matrix_folder, 'matrix.csv')

        df.to_csv(matrix_path, sep='\t')

        del imputed_matrix
        del df
        gc.collect()


if __name__ == '__main__':
    args = parse_args()
    main(args)
