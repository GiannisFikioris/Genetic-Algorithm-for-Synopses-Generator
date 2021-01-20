#!/usr/bin/python3

'''
Finds the parameters that minimized the optimization function in a 6-fold cross validation. For each of the 6 training sets it finds the params that minimized the opt func.
'''

import os
import pickle
from sys import argv

import numpy as np

from local_lib import crit

if len(argv) < 6:
    raise RuntimeError(f'\nNot enough args. Run with:\n"{argv[0]}" "Type" "dataset" "First_Part" "Option" "File_Code"')


typ = argv[1]
dataset = argv[2]
first_part = int(argv[3])
opt = argv[4]
fcode = argv[5]

folder = f'saves/{dataset}/type{typ}'

minn = 1e20
bests = []

for offset in range(6):
    month = first_part + offset

    p = f'{folder}/{fcode}{month}.pkl'

    if not os.path.exists(p):
        raise FileNotFoundError(p)

    with open(p, 'rb') as f:
        save = pickle.load(f)
        results = save[0]  # Fitness of each value

    # ev = f'{folder}/eval_{fcode}{month}.pkl'
    # if os.path.exists(ev):
    #     with open(ev, 'rb') as f:
    #         eval_res = pickle.load(f)
    # else:
    #     eval_res = {}

    vals = list(results.values())


    hof = sorted(results.items(), key=lambda kv: crit(
        kv[1][0], kv[1][1], opt))[0]

    rmse, rat = results[hof[0]]
    score = crit(rmse, rat, opt)
    if score < minn:
        minn = score
        best = hof[0]
    bests.append(hof[0])

print(best)
m = np.mean(bests, axis=0)
s = np.std(bests, axis=0)

for i in range(len(m)):
    print(f'{m[i]:.2f}  {s[i]:.2f}')
