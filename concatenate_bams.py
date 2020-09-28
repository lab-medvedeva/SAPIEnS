from argparse import ArgumentParser

import pandas as pd
import os
import subprocess

def parse_args():
    parser = ArgumentParser('Preparing files for concatenation')
    parser.add_argument('--sra', help='Path to SRA run table')
    parser.add_argument('--cell_type', help='Type of cell to concatenate')
    parser.add_argument('--input_folder', help='Folder with single-cell BAMs')
    parser.add_argument('--output_folder', help='Output folder')
    return parser.parse_args()


def write_samtools_script(df, bam_folder):
    runs = []
    for run in list(df.index):
        runs.append(f'{bam_folder}{os.path.sep}{run}_cleaned.shifted.bam')
    run_command = f'samtools cat {" ".join(runs)}'
    return run_command


def main():
    args = parse_args()
    sra = pd.read_csv(args.sra, index_col=0)
    specific_sra = sra[sra.Cell_type == args.cell_type]

    os.makedirs(args.output_folder, exist_ok=True)
    script = write_samtools_script(
        specific_sra,
        args.input_folder,
    )
    print(script)
    output_file = os.path.join(args.output_folder, f'{args.cell_type}_merged.bam')
    with open(output_file, 'wb') as fp:
        subprocess.call(script.split(), stdout=fp)

    output_sorted_file = os.path.join(args.output_folder, f'{args.cell_type}_sorted.bam')
    with open(output_sorted_file, 'wb') as fp:
        subprocess.call(['samtools', 'sort', output_file], stdout=fp)


if __name__ == '__main__':
    main()
