#!/usr/bin/env python3
""" Annotate BLAST output """

import argparse
import pandas as pd
import os
from typing import NamedTuple, TextIO


class Args(NamedTuple):
    """ Command-line arguments """
    hits: TextIO
    annotations: TextIO
    outfile: TextIO
    delimiter: str
    pctid: float


# --------------------------------------------------
def get_args():
    """ Get command-line arguments """

    parser = argparse.ArgumentParser(
        description='Annotate BLAST output',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-b',
                        '--blasthits',
                        metavar='FILE',
                        type=argparse.FileType('rt'),
                        help='BLAST output (-outfmt 6)',
                        required=True)

    parser.add_argument('-a',
                        '--annotations',
                        help='Annotation file',
                        metavar='FILE',
                        type=argparse.FileType('rt'),
                        required=True)

    parser.add_argument('-o',
                        '--outfile',
                        help='Output file',
                        metavar='FILE',
                        type=argparse.FileType('wt'),
                        default='out.csv')

    parser.add_argument('-d',
                        '--delimiter',
                        help='Output field delimiter',
                        metavar='DELIM',
                        type=str,
                        default='')

    parser.add_argument('-p',
                        '--pctid',
                        help='Minimum percent identity',
                        metavar='PCTID',
                        type=float,
                        default=0.)

    args = parser.parse_args()

    return Args(hits=args.blasthits,
                annotations=args.annotations,
                outfile=args.outfile,
                delimiter=args.delimiter or guess_delimiter(args.outfile.name),
                pctid=args.pctid)


# --------------------------------------------------
def main():
    """ Make a jazz noise here """

    args = get_args()
    annots = pd.read_csv(args.annotations)
    hits = pd.read_csv(args.hits,
                       delimiter='\t',
                       names=[
                           'qseqid', 'sseqid', 'pident', 'length', 'mismatch',
                           'gapopen', 'qstart', 'qend', 'sstart', 'send',
                           'evalue', 'bitscore'
                       ])

    data = []
    for _, hit in hits[hits['pident'] >= args.pctid].iterrows():
        centroids = annots[annots['centroid'] == hit['sseqid']]
        if not centroids.empty:
            for _, centroid in centroids.iterrows():
                data.append({
                    'sseqid': hit['sseqid'],
                    'pident': hit['pident'],
                    'genus': centroid['genus'] or 'NA',
                    'species': centroid['species'] or 'NA',
                })

    df = pd.DataFrame.from_records(data=data)
    df.to_csv(args.outfile, index=False, sep=args.delimiter)

    print(f'Exported {len(data):,} to "{args.outfile.name}".')


# --------------------------------------------------
def guess_delimiter(filename: str) -> str:
    """ Guess the field separator from the file extension """

    ext = os.path.splitext(filename)[1]
    return ',' if ext == '.csv' else '\t'


# --------------------------------------------------
if __name__ == '__main__':
    main()