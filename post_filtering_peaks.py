from argparse import ArgumentParser
import pandas as pd

def parse_args():
    parser = ArgumentParser('Filter output cells')
    parser.add_argument('--imputed_data', help='Path to imputed peaks')
    parser.add_argument('--peak_names', help='Path to peak names', default='')
    #parser.add_argument('--cell_names', help='Path to cell names file')
    parser.add_argument('--cell_type', help='Type of cell to filter')
    parser.add_argument('--output_path', help='Path to output peaks')
    parser.add_argument('--pipeline', choices=['from_peaks', 'from_count_matrix'], default='default')
    parser.add_argument('--dataset', choices=['default', 'mouse_atlas'], default='default')
    return parser.parse_args()


def main():
    args = parse_args()

    if args.pipeline == 'from_peaks':
        imputed_peaks = pd.read_csv(args.imputed_data, header=None)

    #if args.imputed_data.endswith('.txt'):    
    #    imputed_data = pd.read_csv(args.imputed_data, sep='\t', index_col=0).T
    #else:
    #    imputed_data = pd.read_csv(args.imputed_data, index_col=0).T
    #print(imputed_data.index)

    #if args.pipeline == 'default':
    #    cells = pd.read_csv(args.cell_names, index_col=1)
    #else:
    #    cells = pd.read_csv(args.cell_names, sep='\t', header=None, index_col=0)
    #    cells.columns = ['cell_types']
        if args.dataset == 'default':
            peaks = pd.read_csv(args.peak_names).set_index('PeakFile_Peak_ID')
            imputed_peaks = imputed_peaks.set_index(0)

    # print(cells.head)
    # print(imputed_data.head)
    #type_specific_cells = cells[
    #    (cells.cell_types == args.cell_type) & cells.index.isin(imputed_data.index)
    #]

    #binary_imputed_data = ((imputed_data.T > imputed_data.mean(axis=1)).T & imputed_data > imputed_data.mean(axis=0))
    #print(type_specific_cells.shape)
    #type_specific_peaks = binary_imputed_data[
    #    binary_imputed_data.index.isin(type_specific_cells.index)
    #]
    #print(type_specific_peaks.shape)
    #filtered_type_specific_peaks = type_specific_peaks.T.loc[
    #    type_specific_peaks.sum(axis=0) >= 1
    #]
    #print(filtered_type_specific_peaks.shape)
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
            imputed_peaks['chr'] = imputed_peaks[0].apply(lambda x: x.split('_')[0])
            imputed_peaks['start'] = imputed_peaks[0].apply(lambda x: x.split('_')[1])
            imputed_peaks['end'] = imputed_peaks[0].apply(lambda x: x.split('_')[2])
            imputed_peaks[['chr', 'start', 'end']].to_csv(
                args.output_path,
                header=None,
                index=None,
                sep='\t'
            )

if __name__ == '__main__':
    main()
