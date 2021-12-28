from argparse import ArgumentParser
import pandas as pd

def parse_args():
    parser = ArgumentParser('Filter output cells')
    parser.add_argument('--imputed_data', help='Path to imputed peaks')
    parser.add_argument('--peak_names', help='Path to peak names', default='')
    #parser.add_argument('--cell_names', help='Path to cell names file')
    parser.add_argument('--cell_type', help='Type of cell to filter')
    parser.add_argument('--output_path', help='Path to output peaks')
    parser.add_argument('--pipeline', choices=['from_peaks', 'from_count_matrix'], default='from_peaks')
    parser.add_argument('--dataset', choices=['default', 'mouse_atlas'], default='default')
    return parser.parse_args()


def to_peaks_standard(peak_name):
    return peak_name.replace(':', '_').replace('-', '_')


def main():
    args = parse_args()

    if args.pipeline == 'from_peaks':
        imputed_peaks = pd.read_csv(args.imputed_data, header=None)
        print(f'Imputed dataset: {args.imputed_data}', imputed_peaks.shape)
        if args.dataset == 'default':
            peaks = pd.read_csv(args.peak_names).set_index('PeakFile_Peak_ID')

            imputed_peaks = imputed_peaks.set_index(0)

            cicero_type_specific_peaks = peaks[
                peaks.index.isin(imputed_peaks.index)
            ]

            cicero_type_specific_peaks['X2'] = cicero_type_specific_peaks['X2'].astype(int)
            cicero_type_specific_peaks['X3'] = cicero_type_specific_peaks['X3'].astype(int)
            cicero_type_specific_peaks[['X1', 'X2', 'X3']].to_csv(
                args.output_path, sep='\t', header=None, index=None
            )
        elif args.dataset == 'mouse_atlas':
            print(imputed_peaks.columns)
            imputed_peaks['chr'] = imputed_peaks[0].apply(lambda x: to_peaks_standard(x).split('_')[0])
            imputed_peaks['start'] = imputed_peaks[0].apply(lambda x: to_peaks_standard(x).split('_')[1])
            imputed_peaks['end'] = imputed_peaks[0].apply(lambda x: to_peaks_standard(x).split('_')[2])
            imputed_peaks[['chr', 'start', 'end']].to_csv(
                args.output_path,
                header=None,
                index=None,
                sep='\t'
            )

if __name__ == '__main__':
    main()
