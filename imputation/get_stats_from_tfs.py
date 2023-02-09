from argparse import ArgumentParser

import pandas as pd
import numpy as np
import os

import json


def parse_args():
    parser = ArgumentParser('Build difference motifs')
    parser.add_argument('--prefix', help='Path to charts prefix')
    parser.add_argument('--experiment1', help='Path to experiment 1')
    parser.add_argument('--experiment2', help='Path to experiment 2')
    parser.add_argument('--output_path', help='Path to dump stats')
    return parser.parse_args()


def get_motifs_count(df):
    a_records = df.filter(regex='A$', axis=0)
    b_records = df.filter(regex='B$', axis=0)
    c_records = df.filter(regex='C$', axis=0)
    d_records = df.filter(regex='D$', axis=0)

    return {
        'A': len(a_records),
        'B': len(b_records),
        'C': len(c_records),
        'D': len(d_records)
    }


def get_diff_p_value(df_join, args):
    df_join[f'abs_score_{args.experiment1}'] = np.abs(df_join[f'score_{args.experiment1}'])
    df_join[f'abs_score_{args.experiment2}'] = np.abs(df_join[f'score_{args.experiment2}'])
    df_join[f'diff_score'] = df_join[f'abs_score_{args.experiment2}'] - df_join[f'abs_score_{args.experiment1}']
    
    return df_join[['diff_score']].to_json()

    

def main():
    args = parse_args()

    united_name = f'{args.experiment1}_and_{args.experiment2}'

    result_dict={
        args.experiment1: {},
        args.experiment2: {},
        united_name: {}
    }

    values_dict={
    }
    for diff_folder in sorted(os.listdir(args.prefix)):
        diff_path = os.path.join(args.prefix, diff_folder)

        if 'vs' not in diff_path:
            continue
        
        df1 = pd.read_csv(os.path.join(diff_path, f'{args.experiment1}.csv'), index_col='Motif')
        df2 = pd.read_csv(os.path.join(diff_path, f'{args.experiment2}.csv'), index_col='Motif')
        input_path = os.path.join(diff_path, f'{args.experiment1}_and_{args.experiment2}.csv')
        df_join = pd.read_csv(input_path).set_index('Motif')

        result_dict[args.experiment1][diff_folder] = get_motifs_count(df1)
        result_dict[args.experiment2][diff_folder] = get_motifs_count(df2)
        result_dict[united_name][diff_folder] = get_motifs_count(df_join)

        values_dict[diff_folder] = get_diff_p_value(df_join, args)
        print(df_join[[f'abs_score_{args.experiment1}', f'abs_score_{args.experiment2}', 'diff_score']])
    
    with open(args.output_path, 'w') as fp:
        json.dump(result_dict, fp, indent=4)

    with open('test_atlas.json','w') as fp:
        json.dump(values_dict, fp, indent=4)
    print(result_dict)

if __name__ == '__main__':
    main()

