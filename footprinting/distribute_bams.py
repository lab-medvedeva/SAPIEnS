from argparse import ArgumentParser

import pysam
import pandas as pd

import os

from tqdm import tqdm


def parse_args():
    parser = ArgumentParser('Distribute by bams')
    parser.add_argument('--input_bam', help='Path to bam file', required=True)
    parser.add_argument('--cell_labels', help='Path to cell labels file', required=True)
    parser.add_argument('--output_folder', help='Path to output folder', required=True)

    return parser.parse_args()


def get_labels(args):
    labels = pd.read_csv(args.cell_labels, sep='\t', header=None, index_col=0)
    return labels


def get_read_name(read: pysam.AlignedSegment):
    return read.qname.split(':')[0]


def main(args):
    os.makedirs(args.output_folder, exist_ok=True)
    bam_name = os.path.basename(args.input_bam)
    alignment_file = pysam.AlignmentFile(args.input_bam, 'rb')
    bam_prefix = os.path.splitext(bam_name)[0]
    bam_files = dict()

    labels = get_labels(args)

    for read in tqdm(alignment_file.fetch()):
        try:
            cell_type = labels.loc[get_read_name(read)][1]
            cell_type_replaced = cell_type.replace(' ', '_').replace('/', '_')
            bam_prefix_filename = f'{cell_type_replaced}_{bam_prefix}.bam'
            if bam_prefix_filename not in bam_files:
                typed_reads = pysam.AlignmentFile(
                    os.path.join(args.output_folder, bam_prefix_filename),
                    "wb",
                    template=alignment_file
                )
                bam_files[bam_prefix_filename] = typed_reads
            
            bam_file = bam_files[bam_prefix_filename]
            bam_file.write(read)
        except KeyError:
            continue
    
    for key, fp in bam_files.items():
        fp.close()


if __name__ == '__main__':
    args = parse_args()
    main(args)
