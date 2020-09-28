from argparse import ArgumentParser
import pandas as pd

def parse_args():
    parser = ArgumentParser('Filter output cells')
    parser.add_argument('--imputed_data', help='Path to imputed peaks')
    parser.add_argument('--peak_names', help='Path to peak names')
    parser.add_argument('--cell_names', help='Path to cell names file')
    parser.add_argument('--cell_type', help='Type of cell to filter')
    parser.add_argument('--output_path', help='Path to output peaks')
    return parser.parse_args()


def main():
    args = parse_args()
    
    imputed_data = pd.read_csv(args.imputed_data, sep='\t', index_col=0).T
    print(imputed_data.index)
    cells = pd.read_csv(args.cell_names, index_col=1)

    peaks = pd.read_csv(args.peak_names).set_index('PeakFile_Peak_ID')

    # print(cells.head)
    # print(imputed_data.head)
    type_specific_cells = cells[
        (cells.cell_types == args.cell_type) & cells.index.isin(imputed_data.index)
    ]

    binary_imputed_data = ((imputed_data.T > imputed_data.mean(axis=1)).T & imputed_data > imputed_data.mean(axis=0))
    print(type_specific_cells.shape)
    type_specific_peaks = binary_imputed_data[
        binary_imputed_data.index.isin(type_specific_cells.index)
    ]
    print(type_specific_peaks.shape)
    filtered_type_specific_peaks = type_specific_peaks.T.loc[
        type_specific_peaks.sum(axis=0) >= 1
    ]
    print(filtered_type_specific_peaks.shape)
    cicero_type_specific_peaks = peaks[
        peaks.index.isin(filtered_type_specific_peaks.index)
    ]

    cicero_type_specific_peaks['X2'] = cicero_type_specific_peaks['X2'].astype(int)
    cicero_type_specific_peaks['X3'] = cicero_type_specific_peaks['X3'].astype(int)

    cicero_type_specific_peaks[['X1', 'X2', 'X3']].to_csv(
        args.output_path, sep='\t', header=None, index=None
    )

if __name__ == '__main__':
    main()
