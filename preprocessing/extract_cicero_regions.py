import pandas as pd

from argparse import ArgumentParser

from tqdm import tqdm


def parse_args():
    parser = ArgumentParser('Extract peaks for Cicero')
    parser.add_argument('--input_peaks', type=str, help='Input csv file with peaks info')
    parser.add_argument('--input_count_matrix', type=str, help='Input count matrix file')
    parser.add_argument('--output', type=str, help='Path to output tsv file')

    return parser.parse_args()


def get_peaks(peak_names, cell_name, count_matrix):
    new_df = peak_names.join(count_matrix[count_matrix[cell_name] > 0], how='inner')[['peak_id', cell_name]].reset_index()
    new_df['cell_name'] = cell_name
    
    new_df = new_df[['peak_id', 'cell_name', cell_name]]
    
    new_df.columns = ['peak_id', 'cell_name', 'counts']
    return new_df


def process_peaks(args):
    peak_names = pd.read_csv(args.input_peaks)

    count_matrix = pd.read_csv(args.input_count_matrix, index_col=0)
    print(count_matrix.columns)
    peak_names['peak_id'] = peak_names.X1.astype(str) + '_' + peak_names.X2.astype(int).astype(str) + '_' + peak_names.X3.astype(int).astype(str)
    peak_names = peak_names.set_index('PeakFile_Peak_ID')

    #peak_names = peak_names.reset_index().set_index('peak_id')
    print(count_matrix.index)
    print(peak_names.index)
    peaks = []
    for cell_name in tqdm(count_matrix.columns):
        try:
            peak = get_peaks(peak_names, cell_name, count_matrix)
            peaks.append(peak)
        except KeyError:
            continue

    peaks_df = pd.concat(peaks)

    peaks_df.to_csv(args.output, sep='\t', header=False, index=None)


def main():
    args = parse_args()
    process_peaks(args)


if __name__ == '__main__':
    main()
