#!/usr/bin/python3


import argparse
import os
import pickle

import matplotlib.pyplot as plt
import numpy as np
from termcolor import colored as col

from local_lib import DEF_PARAMS, crit


my_parser = argparse.ArgumentParser(description='Plots the results of the normal GA, always from a 6-fold validatioon experiment.',
                                    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))

my_parser.add_argument('type',
                       type=int,
                       help=col('The type of ship. See AIS mnessages type for more details.\n', 'cyan'))

my_parser.add_argument('dataset',
                       type=str,
                       choices=sorted([d for d in os.listdir('../../data') if os.path.isdir(os.path.join('../../data/', d))]),
                       help=col('Dataset from which to read.\n', 'cyan'))

my_parser.add_argument('first_part',
                       type=int,
                       help=col('Number of first part. Will include parts this number and the next 5 parts (6 in total).\n', 'cyan'))

my_parser.add_argument('-t', '--plot_type',
                       choices=['bars', 'lines'],
                       required=True,
                       type=str,
                       help=col('Plot type to use.\n', 'cyan'))

my_parser.add_argument('opt_fcode_label',
                       type=str,
                       nargs='+',
                       help=col('List of options. Each option has 3 arguments, separetaed by @. The 1st is the optimization function (see crit func in local_lib.py). The 2nd argument is the file code and the 3rd is the label to be displayed for it in the x-axis plot.\n', 'cyan'))

args = my_parser.parse_args()

typ = str(args.type)
dataset = args.dataset
first_part = args.first_part
options = args.opt_fcode_label
plot_type = args.plot_type

# Results saved in plots/ folder
if not os.path.exists('plots'):
    os.mkdir('plots')

# Saves are in the following folder
folder = f'saves/{dataset}/type{typ}'

# Plot info
rmses = [] # Left y-axis
ratios = [] # Right y-axis
labels = [] # x-axis labels

for x in options:

    # no option to add a space between plots
    if x == 'no':
        labels.append(' ')
        rmses.append(0)
        ratios.append(0)
        continue

    opt, fcode, label = x.split('@')

    # Remember that the experiment is always 6-fold cross valiadation.
    # These list will hold the results of the 6 folds
    rmse = []
    ratio = []

    # For each fold
    for offset in range(6):

        # Find the file number
        part = first_part + offset

        # Training results are stored here
        p = f'{folder}/{fcode}{part}.pkl'

        # Load training results
        with open(p, 'rb') as f:
            save = pickle.load(f) # save holds a 2-tuple. The second element is time information.
            results = save[0] # The first element is a dict from parameter values to (RMSE, Ratio).

        for k in results:
            # Make the Ratio take values in 0-100.
            results[k] = (results[k][0], 100*results[k][1])

        # Evaluation results are stored here. Read them
        ev = f'{folder}/eval_{fcode}{part}.pkl'
        if os.path.exists(ev):
            with open(ev, 'rb') as f:
                eval_res = pickle.load(f) # Unlike training results, eval results have no time information
            for k in eval_res:
                eval_res[k] = (eval_res[k][0], 100*eval_res[k][1])
        else:
            eval_res = {}

        # if the opt value is def, then take from the valuation set the results for the default parameters.
        if opt == 'def':
            rmse.append(eval_res[DEF_PARAMS][0])
            ratio.append(eval_res[DEF_PARAMS][1])
            continue

        # Find the parameters (key of the dict) that minimize the opt function
        hof = sorted(results.items(), key=lambda kv: crit(
            kv[1][0], kv[1][1], opt))
        key = hof[0][0]


        # If parameterss performance has not been calculated, raise error
        if key not in eval_res:
            raise RuntimeError(
                f'While in part {part}, option {opt}, didnt found {key}')
        vv = eval_res[key]

        # Appen results
        rmse.append(vv[0])
        ratio.append(vv[1])

    # Append the information to the lists. For the RMSE and the Ratio take the avg of the 6 folds.
    labels.append(label)
    rmses.append(np.mean(rmse))
    ratios.append(np.mean(ratio))

# Printing information

# print([f'{x:.2f}' for x in rmses])
# print([f'{x:.2f}' for x in ratios])
print(min(rmses), '\t', max(rmses))
print(min(ratios), '\t', max(ratios))
print()

# Font Size for plots
plt.rcParams.update({'font.size': 16})

# Plot bars
if plot_type == 'bars':
    fig = plt.figure(figsize=(5, 4)) # Create matplotlib figure

    ax = fig.add_subplot(111) # Create matplotlib axes
    ax2 = ax.twinx() # Create another axes that shares the same x-axis as ax.

    my_range = range(len(rmses))

    # Create bars for each value
    ax.bar([i-0.19 for i in my_range], rmses, width=0.36, color='red')
    ax2.bar([i+0.19 for i in my_range], ratios, width=0.36, color='blue')

    ax.set_ylabel('RMSE')
    ax2.set_ylabel('Ratio')

    # Put the labels in the x-axis
    plt.xticks(list(my_range), labels)

    plt.savefig(f'plots/plot_{dataset}_{fcode}_{typ}.png', bbox_inches='tight', dpi=400)

else:
    fig = plt.figure(figsize=(5, 4)) # Create matplotlib figure

    ax = fig.add_subplot(111) # Create matplotlib axes
    ax2 = ax.twinx() # Create another axes that shares the same x-axis as ax.

    my_range = range(len(rmses))
    to_pop = []

    # Check if Def or prev method were used to put them as horizontal lines
    for i in my_range:
        if labels[i] == 'GA':
            ax.hlines(rmses[i], -1000, 1000, color='r', alpha=0.6, linewidth=2)
            ax2.hlines(ratios[i], -1000, 1000, color='b', alpha=0.6, linewidth=2)
            to_pop.append(i)
        elif labels[i] == 'Def':
            ax.hlines(rmses[i], -1000, 1000, color='r', alpha=0.6, linestyle='dashed', linewidth=2)
            ax2.hlines(ratios[i], -1000, 1000, color='b', alpha=0.6, linestyle='dashed', linewidth=2)
            to_pop.append(i)

    # Pop from the lists Def and prev methods
    to_pop.reverse()
    for i in to_pop:
        labels.pop(i)
        rmses.pop(i)
        ratios.pop(i)

    my_range = [int(t) for t in labels]

    range_len = max(my_range) - min(my_range)

    ax.plot(my_range, rmses, marker='o', color='red')
    ax2.plot(my_range, ratios, marker='o', color='blue')

    ax.set_ylabel('RMSE (m)', color='red')
    ax2.set_ylabel('Ratio (%)', color='blue')

    ax.tick_params(axis='y', colors='red')
    ax2.tick_params(axis='y', colors='blue')

    ax.set_xlim((my_range[0]-0.05*range_len, my_range[-1]+0.05*range_len))
    ax2.set_xlim((my_range[0]-0.05*range_len, my_range[-1]+0.05*range_len))

    # ax.set_ylim((0.0, 90.0))
    # ax2.set_ylim((0.0, 50.0))

    ax.set_ylim((0.0, 240.0))
    ax2.set_ylim((0.0, 70.0))

    plt.xticks(list(my_range), labels)
    ax.set_xlabel('θ (m)')
    # plt.grid(True)

    plt.savefig(f'plots/plot_{dataset}_{fcode}_{typ}.png', bbox_inches='tight', dpi=400)
