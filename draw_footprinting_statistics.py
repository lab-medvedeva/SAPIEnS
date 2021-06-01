import matplotlib
matplotlib.use('Agg')
import pandas as pd

from argparse import ArgumentParser


import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm, zscore
import numpy as np
import os


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def parse_args():
    parser = ArgumentParser('Draw chart statistics from differential analysis')
    parser.add_argument('--input', help='Path to csv file with name differential_statistics.txt')
    parser.add_argument('--experiment_name', help='Name of experiment')
    parser.add_argument('--output_root', help='Default folder where to save results')
    parser.add_argument('--p_value', help='p-value size', type=float, default=0.05)
    return parser.parse_args()


def draw_plot(df, cell_type1, cell_type2, save_chart_path, save_significant_path, save_raw_path, p_value):
    tf_activity_score = df[f'Protection_Score_{cell_type1}'] + df[f'TC_{cell_type1}']
    tf_activity_score_2 = df[f'Protection_Score_{cell_type2}'] + df[f'TC_{cell_type2}']
    score = tf_activity_score_2 - tf_activity_score
    z_score = zscore(score)
    p_values = norm.sf(abs(z_score)) * 2
    x_axis = np.random.uniform(low=-0.5, high=0.5, size=len(p_values))
    result_df = pd.DataFrame(score, columns=['score'])
    
    result_df['x'] = x_axis
    result_df['p_value'] = p_values
    result_df['significant'] = result_df['p_value'].apply(lambda x: 'Yes' if x < p_value else 'No')
    
    fig, ax = plt.subplots(figsize=(20, 20))
    chart = sns.scatterplot(data=result_df, x='x', y='score', hue='significant')
    for line in range(0, df.shape[0]):
        if result_df.significant.iloc[line] == 'Yes':
            chart.text(
                result_df.x.iloc[line]+0.001,
                result_df.score.iloc[line] + 0.001,
                result_df.index[line],
                horizontalalignment='left',
                size='small',
                color='black'
            )
    chart.set_ylabel(f'{cell_type1} $\longleftrightarrow$ {cell_type2}', fontsize=20)
    
    fig.savefig(save_chart_path)
    result_df[result_df['significant'] == 'Yes'].to_csv(save_significant_path)
    result_df.to_csv(save_raw_path)
    return fig


def main():
    args = parse_args()

    df = pd.read_csv(args.input, sep='\t', index_col='Motif')

    cell_columns = list(filter(lambda x: x.startswith('Protection_Score'), df.columns))
    cell_types = [remove_prefix(type, 'Protection_Score_') for type in cell_columns]


    for cell_type1 in sorted(cell_types):
        for cell_type2 in sorted(cell_types):
            if cell_type1 >= cell_type2:
                continue
            
            output_folder = os.path.join(args.output_root, f'{cell_type1}_vs_{cell_type2}')
            os.makedirs(output_folder, exist_ok=True)
            _ = draw_plot(
                df,
                cell_type1,
                cell_type2,
                save_chart_path=os.path.join(output_folder, f'{args.experiment_name}.png'),
                save_significant_path=os.path.join(output_folder, f'{args.experiment_name}.csv'),
                save_raw_path=os.path.join(output_folder, f'{args.experiment_name}_all.csv'),
                p_value=args.p_value
            )


if __name__ == '__main__':
    main()

