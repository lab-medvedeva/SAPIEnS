from argparse import ArgumentParser

import pandas as pd


def parse_args():
    parser = ArgumentParser('Filter peaks by coaccess')
    parser.add_argument('--prefix', type=str, help='Path to peaks, found by Cicero')
    parser.add_argument('--count_matrix', type=str, help='Path to count matrix')
    parser.add_argument('--threshold', type=float, help='Coaccess ratio threshold')
    parser.add_argument('--output', type=str, help='Output path to peaks')
    parser.add_argument('--peak_names', type=str, help='Path to peaks table')
    return parser.parse_args()


def main():
    args = parse_args()
    count_matrix = pd.read_csv(args.count_matrix, index_col=0)

    coaccesses = []
    for i in range(1, 23):
        df = pd.read_csv(f'{args.prefix}_chr{i}.csv')
        coaccesses.append(df)

    coaccesses.append(pd.read_csv(f'{args.prefix}_chrX.csv'))
    coaccess_df = pd.concat(coaccesses)

    peak_names = pd.read_csv(args.peak_names)
    peak_names['peak_id'] = peak_names.X1.astype(str) + '_' + peak_names.X2.astype(int).astype(str) + '_' + peak_names.X3.astype(int).astype(str)
    peak_names = peak_names.reset_index().set_index('peak_id')
    
    filtered_peak_names = coaccess_df[coaccess_df['coaccess'] > args.threshold]['Peak1'].unique()
    print(filtered_peak_names)
    print(peak_names.index)
    filtered_peaks = peak_names[peak_names.index.isin(list(filtered_peak_names))]
    filtered_peaks = filtered_peaks.reset_index().set_index('PeakFile_Peak_ID') 
    print(filtered_peaks.index)
    print(count_matrix.index)
    filtered_count_matrix = count_matrix[count_matrix.index.isin(filtered_peaks.index)]

    filtered_count_matrix.to_csv(args.output)


if __name__ == '__main__':
    main()
