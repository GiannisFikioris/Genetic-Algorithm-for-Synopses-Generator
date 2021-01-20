#!/usr/bin/python3

import argparse
import os
import random

from termcolor import colored as col
from tqdm import tqdm

from local_lib import (DEF_PARAMS, OPT_BREST_PARAMS, PARAMETERS, TYPE_TO_TYPE,
                       Daemon)

my_parser = argparse.ArgumentParser(description='Script tha given a dataset runs the synopses for all types. Uses folders in ../../data/<dataset>/data_per_type/all/',
                                    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))

my_parser.add_argument('dataset',
                       type=str,
                       choices=sorted([d for d in os.listdir(
                           '../../data') if os.path.isdir(os.path.join('../../data/', d))]),
                       help=col('The dataset to use.\n', 'cyan'))

my_parser.add_argument('--default', '-d',
                       action='store_true',
                       help=col('Whether to use the default parameters to perform the synopses.\n', 'cyan'))

args = my_parser.parse_args()
dataset = args.dataset
use_default = args.default

# Results are stored here
if not os.path.exists('tmp_RTEC'):
    os.mkdir('tmp_RTEC')

# Take all the vessel types' names
l = os.listdir(f'../../data/{dataset}/data_per_type/all')
random.shuffle(l)
# Create a tqdm object to show the progress
t = tqdm(l, desc='Type ?')

# For each vessel type
for name in t:

    # Get the raw type integer
    typ = name.replace('type_', '').replace('.csv', '')

    # Refesh the counter with the new type
    t.set_description('Type ' + typ)
    t.refresh()

    # Create a dict with params from individual
    params = {}
    i = 0
    for k, v in PARAMETERS.items():

        # `TYPE_TO_TYPE` maps some types (for which the GA was not run) to the types that were used in GA
        # `use_default` is an argument that indicates whether to run synopses with default params
        if typ in TYPE_TO_TYPE and not use_default:

            # `OPT_BREST_PARAMS` is a dict mapping the type to GA's parameters
            # If you look at local_lib.py you can see that now these params are generated
            # by minimizing $Ratio + ReLU(RMSE - 15)$
            params[k] = str(OPT_BREST_PARAMS[TYPE_TO_TYPE[typ]][i])

        # Other wise use the default params
        else:
            params[k] = str(DEF_PARAMS[i])
        i += 1

    try:
        # Start the daemon.
        # Because `one_file` is true the input will ne be read from the usual place,
        # but from folder ``../../data/brest/data_per_type/all`
        # Because `syn_prints_noise` is false the Synopses Generator will not output
        # noisy positions (as done usually), but rather the noiseless points
        daemon = Daemon(typ, [], dataset, '', one_file=True,
                        syn_prints_noise='false')

        # Run synopses and copies results to the 2 files. These names are used by other scripts
        daemon.run_synopses_and_copy_files(
            params,
            'tmp_RTEC/synopses_{}_{}.json'.format(dataset, typ),
            'tmp_RTEC/synopses_{}_{}_noiseless.json'.format(dataset, typ)
        )

    finally:
        daemon.end()
