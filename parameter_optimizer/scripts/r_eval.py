#!/usr/bin/python3


import argparse
import os
import pickle
import sys
from typing import List

from termcolor import colored as col
from tqdm import tqdm

from local_lib import DEF_PARAMS, PARAMETERS, Daemon, crit


def eprint(*args, **kwargs):
    """Print in std err
    """
    print(*args, file=sys.stderr, **kwargs)


def evaluate(individual: List):  # pylint: disable=missing-function-docstring
    global daemon
    global PARAMETERS

    # Create a dict with params from individual
    params = {}
    i = 0
    for k, v in PARAMETERS.items():
        # If value outside of range, return huge value
        if individual[i] < v[0] or individual[i] > v[1]:
            return 1e20, 1e20

        # Else save in params the value of the individual
        params[k] = individual[i]
        i += 1

    # Run synopses and estimate RMSE and compression ratio
    rmse, ratio = daemon.run_synopses(params)

    return rmse, ratio


my_parser = argparse.ArgumentParser(description='Finds the results on the valuation set of the online gen algo.',
                                    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))

my_parser.add_argument('type',
                       type=int,
                       help=col('The type of ship\n', 'cyan'))

my_parser.add_argument('data',
                       type=str,
                       choices=sorted([d for d in os.listdir(
                           '../../data') if os.path.isdir(os.path.join('../../data/', d))]),
                       help=col('Dataset from which to read.\n', 'cyan'))

my_parser.add_argument('opt',
                       type=str,
                       help=col('Optimization option.\n', 'cyan'))

args = my_parser.parse_args()

ship_type = str(args.type)
opt = args.opt
dataset = args.data

# Low and High Limits for mutation
lows = [x[0] for x in PARAMETERS.values()]
highs = [x[1] for x in PARAMETERS.values()]

# Location where results are saved
saves_folder = f'saves_running/{dataset}/type{ship_type}/'

months = ['march', 'april', 'may', 'june', 'july', 'august']

for m in tqdm(range(len(months) - 1)):

    save_name = f'{saves_folder}/{months[m]}.pkl'
    save_name_ev = f'{saves_folder}/{months[m+1]}_eval.pkl'

    with open(save_name, 'rb') as f:
        save = pickle.load(f)
        res = save[0]  # Fitness of each value

    best = sorted(res.items(), key=lambda kv: crit(
        kv[1][0], kv[1][1], opt))[0][0]


    if os.path.exists(save_name_ev):
        with open(save_name_ev, 'rb') as f:
            save = pickle.load(f)
            res_ev = save  # Fitness of each value
    else:
        res_ev = {}

    # print(f'{months[m+1]}\t{res_ev[best][0] - res[best][0]:.1f}')

    # if DEF_PARAMS not in res_ev or best not in res_ev:
    if best not in res_ev:
        try:
            # Begin Daemon. Type of Daemon is declared in the top of
            # this file, in the import
            daemon = Daemon(ship_type, ['1', '2', '3',
                                        '4', '5', '6'], dataset, [months[m+1]])

            # if DEF_PARAMS not in res_ev:
            #     rmse, ratio = evaluate(DEF_PARAMS)
            #     res_ev[DEF_PARAMS] = (rmse, ratio)

            if best not in res_ev:
                rmse, ratio = evaluate(best)
                res_ev[best] = (rmse, ratio)
        finally:
            daemon.end()

        with open(save_name_ev, 'wb') as f:
            pickle.dump(res_ev, f)
