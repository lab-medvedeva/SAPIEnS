from argparse import ArgumentParser

import pandas as pd


def parse_args():
    parser = ArgumentParser('Filter peaks by coaccess')
    parser.add_argument('--prefix', type=str, help='Path to peaks, found by Cicero')
    parser.add_argument('--count_matrix', type=str, help='Path to count matrix')
    parser.add_argument('--threshold', type=float, help='Coaccess ratio threshold')
    parser.add_argument('--output', type=str, help='Output path to peaks')
    parser.add_argument('--organism', type=str, help='Organism', choices=['mouse', 'human'], default='human')
    return parser.parse_args()


def read_coaccesses(prefix, organism):
    if organism == 'human':
        chromosomes = list(range(1, 23))
    else:
        chromosomes = list(range(1, 20))
    chromosomes += ['X']

    coaccesses = []
    for chromosome in chromosomes:
        df = pd.read_csv(f'{prefix}chr{chromosome}.csv')
        coaccesses.append(df)

    coaccess_df = pd.concat(coaccesses)

    return coaccess_df


def main():
    args = parse_args()

    coaccess_df = read_coaccesses(args.prefix, args.organism)

    filtered_peak_names = coaccess_df[coaccess_df['coaccess'] > args.threshold]['Peak1'].unique()
    print(len(filtered_peak_names))


    count_matrix = pd.read_csv(args.count_matrix, index_col=0, sep='\t')
    peak_names = count_matrix.index
    #peak_names = pd.read_csv(args.peak_names)
    #peak_names['peak_id'] = peak_names.X1.astype(str) + '_' + peak_names.X2.astype(int).astype(str) + '_' + peak_names.X3.astype(int).astype(str)
    #peak_names = peak_names.reset_index().set_index('peak_id')
    
    print(filtered_peak_names)
    print(peak_names)
    filtered_count_matrix = count_matrix[count_matrix.index.isin(filtered_peak_names)]

    filtered_count_matrix.to_csv(args.output, sep='\t')


if __name__ == '__main__':
    main()
