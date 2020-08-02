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
                       help=col('The files from which to read. This refers to files in ../../data/*/data_per_type/cross/\n', 'cyan'))

my_parser.add_argument('options',
                       metavar='MONTH@OPT@TYPE',
                       type=str,
                       nargs='+',
                       help=col('The options to run.\nM is the month to train.\nOPT is the optimization option.\nTYPE is the ship type.\n', 'cyan'))

my_parser.add_argument('--eval_only', '-e',
                       action='store_true',
                       help=col('Whether to only evaluate the results.\n', 'cyan'))

args = my_parser.parse_args()

dataset = args.data
fcode = args.fcode

ngen = 7
pops = 7

if not os.path.exists('logs'):
    os.mkdir('logs')

if not os.path.exists('tmp'):
    os.mkdir('tmp')

for arg in args.options:

    w = arg.split('@')
    mmm = w[0]
    opt = w[1]
    ship_type = w[2]

    if '-' in mmm:
        m1 = int(mmm.split('-')[0])
        m2 = int(mmm.split('-')[1]) + 1
    else:
        m1 = int(mmm)
        m2 = int(mmm) + 1

    for m in range(m1, m2):

        t = time()

        if not args.eval_only:
            ret = os.system('python3 genetic.py -data={0} -type={1} -p={2} -opt={3} -ngen={4} -pops={5} -fcode={6} > logs/{0}_{1}_{6}_{2}_{3}.out'.format(
                dataset, ship_type, m, opt, ngen, pops, fcode))
            if ret != 0:
                raise RuntimeError('Return code ' + str(ret))

        ret = os.system(
            'python3 valuate.py {} {} {} {} {}'.format(ship_type, m, opt, dataset, fcode))
        if ret != 0:
            raise RuntimeError('Return code ' + str(ret))

        t = round(time() - t)
        try:
            print('\n ** {}: Took {} hours, {} minutes, {} seconds **\n'.format(
                datetime.time(datetime.now()), t//3600, (t % 3600)//60, t % 60))
        except:
            pass
