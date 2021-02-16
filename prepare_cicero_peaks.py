from scale.dataset import read_mtx

from argparse import ArgumentParser
import pandas as pd
import numpy as np

import os


def parse_args():
    parser = ArgumentParser('Preparing raw peaks from cicero pipeline')
    parser.add_argument('--dataset_path', help='Path to Scale dataset: count, feature, barcode folder')
    parser.add_argument('--label_path', help='Path to cell labels')
    parser.add_argument('--num_peaks_threshold', type=int, help='Num peaks to filter')
    parser.add_argument('--output_path', help='Path to save peaks in bed folder')
    parser.add_argument('--suffix', help='Suffix to path')
    return parser.parse_args()


def main():
    args = parse_args()
    labels = pd.read_csv(args.label_path, sep='\t', header=None)
    count, feature, barcode = read_mtx(args.dataset_path)

    os.makedirs(args.output_path, exist_ok=True)
    cell_types = labels[1].unique()
    cell_barcodes = {}
    for cell_type in cell_types:
        cell_barcodes[cell_type] = list(labels[labels[1] == cell_type].index)

    for cell_type, barcode in cell_barcodes.items():
        cell_by_feature = np.asarray(count[barcode].sum(axis=0)).flatten()
        feature_threshold = cell_by_feature[np.argsort(cell_by_feature)[-args.num_peaks_threshold]]
        print(f'{cell_type}: {feature_threshold}')
        filtered_features = (cell_by_feature > 0) & (cell_by_feature >= feature_threshold)
        print(f'{cell_type}: filtered {np.sum(filtered_features)}')
        output = pd.DataFrame(feature[filtered_features])
        # print(cell_type, cell_by_feature[np.argsort(cell_by_feature)[-args.num_peaks_threshold:]][:10])
        output['chr'] = output[0].apply(lambda x: x.split('_')[0])
        output['start'] = output[0].apply(lambda x: x.split('_')[1])
        output['end'] = output[0].apply(lambda x: x.split('_')[2])
        output.drop(0, axis=1).to_csv(
            os.path.join(args.output_path, f'{cell_type.replace(" ", "_").replace("/", "_")}_{args.suffix}.bed'),
            header=None,
            index=None,
            sep='\t'
        )

if __name__ == '__main__':
    main()

