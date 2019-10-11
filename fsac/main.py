import argparse
import logging
import os
import sys
from pathlib import Path

from . import __version__
from .allele_call import allele_call
from .update import update_directory
from .tabulate import tabulate_calls

# Ensure numpy, via pandas, doesn't use more than 1 thread.
# If numpy uses multiple threads, it brings no performance benefit in this
# case, but can cause problems if you're running lots of jobs
# on a single HPC node
for env_var in ('OPENBLAS_NUM_THREADS',
                'OMP_NUM_THREADS',
                'MKL_NUM_THREADS',
                'NUMEXPR_NUM_THREADS'):
    os.environ[env_var] = '1'

def arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'{parser.prog} {__version__}')

    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers(title='Commands')

    ### Allele Calling ###
    allelecall = subparsers.add_parser('call',
                                       help='Call MLST alleles')

    allelecall.set_defaults(func=call_alleles)

    allelecall.add_argument('-i', '--input',
                            type=Path,
                            required=True,
                            help='Input genome')

    allelecall.add_argument('-a', '--alleles',
                            type=Path,
                            required=True,
                            help='Alleles directory')

    allelecall.add_argument('-o', '--output',
                            type=Path,
                            default=sys.stdout,
                            help='JSON output filename [-]')


    ### Allele Updating ###
    update = subparsers.add_parser('update',
                                   help='Update allele definitions')

    update.set_defaults(func=update_results)

    update.add_argument('-a', '--alleles',
                        type=Path,
                        required=True,
                        help='Alleles directory')

    update.add_argument('-j', '--json-dir',
                        type=Path,
                        required=True,
                        help='Directory containing JSON result files')

    update.add_argument('-g', '--genome-dir',
                        type=Path,
                        required=True,
                        help='Directory containing FASTA formatted genomes')

    update.add_argument('-t', '--threshold',
                        type=int,
                        default=10,
                        help='If the hit is this number of basepairs or fewer \
                        shorter than expected, attempt to extend the hit [10]')

    ### Tabulation ###
    tabulate = subparsers.add_parser('tabulate',
                                     help='Create a table from JSON results')

    tabulate.set_defaults(func=tabulate_allele_calls)

    tabulate.add_argument('-j', '--json-dir',
                          type=Path,
                          required=True,
                          help='Directory containing JSON result files')

    tabulate.add_argument('-o', '--output',
                          type=Path,
                          default=sys.stdout,
                          help='Output filename [-]')

    tabulate.add_argument('-d', '--delimiter',
                          type=str,
                          default='\t',
                          help='Delimiter character [TAB]')

    args = parser.parse_args()

    if args.func is None:
        parser.print_help()
        sys.exit(0)

    return args


def main():

    args = arguments()

    logging.basicConfig(datefmt='%Y-%m-%d %H:%M',
                        format='%(asctime)s - %(levelname)s: %(message)s',
                        stream=sys.stderr,
                        level=logging.INFO)

    logging.info('Running %s', args.func.__name__)
    args.func(args)


def call_alleles(args):

    allele_call(args.input, args.alleles, args.output)


def update_results(args):

    update_directory(args.json_dir, args.alleles,
                     args.threshold, args.genome_dir)


def tabulate_allele_calls(args):

    tabulate_calls(args.json_dir, args.output, args.delimiter)


if __name__ == '__main__':
    main()
