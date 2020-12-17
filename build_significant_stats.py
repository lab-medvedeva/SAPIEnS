from argparse import ArgumentParser

import pandas as pd

import os


def parse_args():
    parser = ArgumentParser('Build difference motifs')
    parser.add_argument('--prefix', help='Path to charts prefix')
    parser.add_argument('--experiment1', help='Path to experiment 1')
    parser.add_argument('--experiment2', help='Path to experiment 2')

    return parser.parse_args()


def main():
    args = parse_args()
    
    for diff_folder in sorted(os.listdir(args.prefix)):
        diff_path = os.path.join(args.prefix, diff_folder)

        if 'vs' not in diff_path:
            continue

        df1 = pd.read_csv(os.path.join(diff_path, f'{args.experiment1}.csv'), index_col='Motif')
        df2 = pd.read_csv(os.path.join(diff_path, f'{args.experiment2}.csv'), index_col='Motif')

        df_join = df1.join(df2, lsuffix='_l', rsuffix='_r', how='inner')
        df_diff_1 = df1[~df1.index.isin(df_join.index)]
        df_diff_2 = df2[~df2.index.isin(df_join.index)]

        df_diff_1.to_csv(os.path.join(diff_path, f'{args.experiment1}_without_{args.experiment2}.csv'))
        df_diff_2.to_csv(os.path.join(diff_path, f'{args.experiment2}_without_{args.experiment1}.csv'))


if __name__ == '__main__':
    main()

