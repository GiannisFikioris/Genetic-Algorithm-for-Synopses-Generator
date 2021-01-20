#!/usr/bin/python3

'''
Script that searches some GA results, and tries various hyper-parameter values.
Shows which hyper-parameter values satisfy RMSE and Ratio below user-specified bounds.
'''

import pickle
from sys import argv

from termcolor import colored as col
from local_lib import crit


if len(argv) < 6:
    print(col('Usage:', 'red'))
    print('\t', argv[0], 'Dataset Type Fcode LowRMSE LowRatio')

dataset = argv[1]
ship_type = argv[2]
fcode = argv[3]
low_rmse = float(argv[4]) # RMSE bound that the hyper-parameter must satisfy
low_ratio = float(argv[5]) # Ratio bound that the hyper-parameter must satisfy


# File where results are stored
save_name = 'saves/{}/type{}/{}.pkl'.format(dataset, ship_type, fcode)

with open(save_name, 'rb') as file:
    save = pickle.load(file)
    results = save[0]  # Mapping of synopses-parameters to (RMSE, Ratio)


# Hyper-Parameter Values to try
if dataset == 'brest':
    l1 = [2, 4, 7, 10, 13, 17]
    l2 = [0.7, 0.8, 1.0, 1.2, 1.4, 1.6]
elif dataset == 'mtraffic':
    l1 = [16, 24, 32, 42, 52, 62, 74, 88]
    l2 = [0.3, 0.45, 0.6, 0.75, 1.0, 1.3, 1.65, 2.0]
else:
    raise ValueError('Wrong dataset')

# For all combinations
for x in l1:
    for n in l2:

        opt = 'new,{},{}'.format(n, x)
        print(f'{x:3.0f},{n:.2f}: ', end='')

        # Find the best result according to the above opt func
        rmse, ratio = sorted(results.items(), key=lambda kv: crit(kv[1][0], kv[1][1], opt))[0][1]

        # Check if bounds are satisfies and print it
        if rmse < low_rmse and 100*ratio < low_ratio:
            print(col('True', 'green'), end='  ')
        else:
            print(col('False', 'red'), end=' ')
    print()
