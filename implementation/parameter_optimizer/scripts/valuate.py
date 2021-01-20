#!/usr/bin/python3


import os
import pickle
import sys
from typing import List, Tuple

from local_lib import Daemon
from local_lib import crit, DEF_PARAMS, PARAMETERS


def evaluate(individual: List) -> Tuple[float, float]:
    """Evaluates an individual: calculates synopses from individual params.
    Returns rmse and ratio


    Arguments:
        individual {List} -- A list-individual that holds parameters to evaluate

    Returns:
        Tuple[float, float] -- RMSE and Ratio
    """

    global daemon
    global PARAMETERS

    # Create a dict with params from individual
    params = {}
    i = 0
    for k in PARAMETERS.keys():

        # Else save in params the value of the individual
        params[k] = individual[i]
        i += 1

    # Run synopses and estimate RMSE and compression ratio
    rmse, ratio = daemon.run_synopses(params)

    return rmse, ratio


if len(sys.argv) < 5:
    raise RuntimeError('Not enough args')

typ = sys.argv[1]
month = sys.argv[2]
opt = sys.argv[3]
dataset = sys.argv[4]
fcode = sys.argv[5]

folder = 'saves/{}/type{}'.format(dataset, typ)

p = '{}/{}{}.pkl'.format(folder, fcode, month)

if not os.path.exists(p):
    sys.exit(0)

with open(p, 'rb') as f:
    save = pickle.load(f)
    results = save[0]  # Fitness of each value
    for k in results:
        results[k] = (results[k][0], 100*results[k][1])

p = '{}/eval_{}{}.pkl'.format(folder, fcode, month)
if os.path.exists(p):
    with open(p, 'rb') as f:
        eval_res = pickle.load(f)
else:
    eval_res = {}

vals = list(results.values())

try:
    daemon = Daemon(typ, [month], dataset, fcode)

    if DEF_PARAMS not in eval_res:
        rmse, ratio = evaluate(DEF_PARAMS)
        eval_res[DEF_PARAMS] = (rmse, ratio)

    for j in range(1):

        if j == 0:
            hof_len = 1
            hof = sorted(results.items(), key=lambda kv: crit(
                kv[1][0], kv[1][1], opt))[:hof_len]
        elif j == 1:
            hof_len = 1
            hof = sorted(results.items(), key=lambda kv: crit(
                kv[1][0], kv[1][1], 'rmse'))[:hof_len]
        else:
            hof_len = 2
            hof = sorted(results.items(), key=lambda kv: crit(
                kv[1][0], kv[1][1], 'ratio'))[:hof_len]

        for i, v in enumerate(hof):
            params = v[0]
            if params not in eval_res:
                rmse, ratio = evaluate(params)
                eval_res[params] = (rmse, ratio)
finally:
    daemon.end()
    p = '{}/eval_{}{}.pkl'.format(folder, fcode, month)
    with open(p, 'wb') as f:
        pickle.dump(eval_res, f)
