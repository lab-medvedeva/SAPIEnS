import glob
import json
import pandas as pd
from argparse import ArgumentParser
from collections import defaultdict, Counter
import os


PREPROCESSING_METHODS = ['cicero', 'threshold', 'boruta']


def parse_args():
    parser = ArgumentParser('Metrics Collector')
    parser.add_argument('--input', help='Path to dataset', required=True)
    parser.add_argument('--output', help='Path to output folder', required=True)
    return parser.parse_args()


def load_json(path):
    with open(path, 'r') as fp:
        return json.load(fp)


def normalize(df):
    df['distance_pca'] = df.distance.apply(lambda x: x['pca_score'])
    df['distance_tsne'] = df.distance.apply(lambda x: x['tsne_score'])
    df['distance_umap'] = df.distance.apply(lambda x: x['umap_score'])
    for column in ['hc', 'kmeans', 'louvain']:
        for metric in ['ari', 'ami', 'homogeneity']:
            df[f'{column}_{metric}'] = df[column].apply(lambda x: x[metric])
    return df


def get_metrics_from_json(regex_path, metric_iteration=''):
    metrics_list = []
    indices = []

    for path in glob.glob(regex_path):
        print(path)
        metrics = load_json(path)
        metric_iteration = path.split('/')[-2]
        metrics_list.append(metrics)
        indices.append(metric_iteration)
    
    df = pd.DataFrame(metrics_list, index=indices)
    
    df = normalize(df)
    
    df_melt = df.reset_index().melt('index', var_name='cols', value_name='vals')
    df_melt_new = df_melt[~df_melt.cols.isin(['distance', 'hc', 'kmeans', 'louvain'])]
    df_melt_new['Metric'] = df_melt_new['cols']
    
    return df_melt_new


def collect_metrics_raw(args):
    for method in PREPROCESSING_METHODS:
        print(method)

        input_path = f'{args.input}/clustering/{method}/metrics.json'
        assert os.path.exists(input_path), f'No metrics found for {method} at {input_path}. Please, make clustering'
        df_melt_new = get_metrics_from_json(f'{args.input}/clustering/{method}/metrics.json')
        print(df_melt_new.head())
        df_melt_new['method'] = method # set method here


        df_melt_new.to_csv(f'{args.output}/{method}.csv', index=None) # save to csv


def collect_metrics_scale(args):
    for method in PREPROCESSING_METHODS:
        metrics_list = []
        indices = []

        for path in glob.glob(f'{args.input}/clustering/scale_{method}/*/*.json'):
            print(path)
            metrics = load_json(path)
            metric_iteration = path.split('/')[-2]
            metrics_list.append(metrics)
            indices.append(int(metric_iteration))
        df = pd.DataFrame(metrics_list, index=indices)
        df = normalize(df)
        
        df_melt = df.reset_index().melt('index', var_name='cols', value_name='vals')
        df_melt_new = df_melt[~df_melt.cols.isin(['distance', 'hc', 'kmeans', 'louvain'])]
        df_melt_new['Metric'] = df_melt_new['cols']
        
        counters = Counter()
        for metric in df_melt_new.Metric.unique():
            counters[df_melt_new[df_melt_new.Metric == metric].sort_values('vals', ascending=False).iloc[0]['index']] += 1
        print(method, counters, df_melt_new.shape)
        df_melt_new['method'] = f'scale_{method}' # Set here method to compare
        print(method, counters.most_common(1)[0][0])
        # Paste best value here and save to csv
        df_melt_new[df_melt_new['index'] == counters.most_common(1)[0][0]].to_csv(f'{args.output}/scale_{method}.csv', index=None)


def collect_metrics_scopen(args):
    for method in PREPROCESSING_METHODS:

        metrics_list = []
        indices = []

        for path in glob.glob(f'{args.input}/clustering/scopen_{method}/*/*.json'):
            metrics = load_json(path)
            metric_iteration = path.split('/')[-2]
            metrics_list.append(metrics)
            indices.append(float(metric_iteration.split('_')[1]))
            
        df = pd.DataFrame(metrics_list, index=indices)
        
        df = normalize(df)
        df_melt = df.reset_index().melt('index', var_name='cols', value_name='vals')
        
        df_melt_new = df_melt[~df_melt.cols.isin(['distance', 'hc', 'kmeans', 'louvain'])]
        df_melt_new['Metric'] = df_melt_new['cols']
        print(df_melt.cols)
        
        from collections import defaultdict
        counter1 = Counter()
        counters = defaultdict(int)
        for metric in df_melt_new.Metric.unique():
            print(df_melt_new[df_melt_new.Metric == metric].sort_values('vals', ascending=False).iloc[0]['index'])
            counter1[df_melt_new[df_melt_new.Metric == metric].sort_values('vals', ascending=False).iloc[0]['index']] += 1
        
        df_melt_new['method'] = f'scopen_{method}'
        print(counter1)
        
        most_common = counter1.most_common(1)[0][0]
        
        df_melt_new[df_melt_new['index'] == most_common].to_csv(
            f'{args.output}/scopen_{method}.csv',
            index=None
        )


def main(args):
    os.makedirs(args.output, exist_ok=True)
    collect_metrics_raw(args)
    collect_metrics_scale(args)
    collect_metrics_scopen(args)


if __name__ == '__main__':
    args = parse_args()
    main(args)

