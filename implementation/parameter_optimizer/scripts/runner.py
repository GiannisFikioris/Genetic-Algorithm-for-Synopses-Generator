#!/usr/bin/python3

import os
from time import time
from datetime import datetime
import argparse
from termcolor import colored as col


my_parser = argparse.ArgumentParser(description='Python3 Script that trains the genetic algorithm and then finds the RMSE and Ratio for the best parameter on the valuation set.',
                                    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))

my_parser.add_argument('data',
                       type=str,
                       choices=sorted([d for d in os.listdir('../../data') if os.path.isdir(os.path.join('../../data/', d))]),
                       help=col('Dataset to use.\n', 'cyan'))

my_parser.add_argument('fcode',
                       type=str,
                       help=col('The files from which to read. This refers to files in ../../data/`dataset`/data_per_type/cross/\n', 'cyan'))

my_parser.add_argument('options',
                       metavar='Part@Opt@Type',
                       nargs='+',
                       help=col('What to run. Is a list, where each element contains 3 arguments, separated by "@". First is "Part", the part or parts to train on (for single part simpy contains an integer. For multiple parts contains a range of the form `x-y` that indicates to use parts x to y (inclusive)). Secondly is "Opt", the optimization option to use. Thirdly is "Type", the ship type.\n', 'cyan'))

my_parser.add_argument('--eval_only', '-e',
                       action='store_true',
                       help=col('Whether to only evaluate the results and skip the training.\n', 'cyan'))

args = my_parser.parse_args()

dataset = args.data
fcode = args.fcode
eval_only = args.eval_only

# Number of generations and population size TODO put these as args
ngen = 7
pops = 7

# Stdout of scripts will be saved in this folder
if not os.path.exists('logs'):
    os.mkdir('logs')

# Scripts will use this folder
if not os.path.exists('tmp'):
    os.mkdir('tmp')

# For each option
for o in args.options:

    w = o.split('@')
    parts = w[0]
    opt = w[1] # String for optimization function
    ship_type = w[2] # Ship Type

    if '-' in parts: # If true user entered something in the form of x-y, indicating that parts x to y should be used.
        p1 = int(parts.split('-')[0])
        p2 = int(parts.split('-')[1]) + 1
    else:
        p1 = int(parts)
        p2 = int(parts) + 1

    # For each part in range
    for p in range(p1, p2):

        t = time()

        if not eval_only:
            # Run genetic.py
            ret = os.system('python3 genetic.py -data={0} -type={1} -p={2} -opt={3} -ngen={4} -pops={5} -fcode={6} > logs/{0}_{1}_{6}_{2}_{3}.log'.format(
                dataset, ship_type, p, opt, ngen, pops, fcode))

            # This means that some error occurred
            if ret != 0:
                raise RuntimeError('Return code ' + str(ret))

        # Run valuation. This will store the RMSE,Ratio for the best individual
        ret = os.system(f'python3 valuate.py {ship_type} {p} {opt} {dataset} {fcode}')
        if ret != 0:
            raise RuntimeError('Return code ' + str(ret))

        t = round(time() - t)

        # I dont remember why there is a try here. I guess it doesnt hurt though
        try:
            print('\n ** {}: Took {} hours, {} minutes, {} seconds **\n'.format(
                datetime.time(datetime.now()), t//3600, (t % 3600)//60, t % 60))
        except:
            pass
