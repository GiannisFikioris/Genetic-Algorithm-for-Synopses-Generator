#!/usr/bin/python3


import argparse
import os
import pickle

import matplotlib.pyplot as plt
from termcolor import colored as col

from local_lib import crit


my_parser = argparse.ArgumentParser(description='Plots the results of genetic algo run on the evaluation set.',
                                    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))

my_parser.add_argument('type',
                       type=int,
                       help=col('The type of ship\n', 'cyan'))

my_parser.add_argument('dataset',
                       type=str,
                       choices=sorted([d for d in os.listdir('../../data') if os.path.isdir(os.path.join('../../data/', d))]),
                       help=col('Dataset from which to read.\n', 'cyan'))

my_parser.add_argument('opt',
                       type=str,
                       help=col('Optimization option.\n', 'cyan'))

my_parser.add_argument('-t', '--plot_type',
                       choices=['tikz', 'bars', 'lines'],
                       required=True,
                       type=str,
                       help=col('Plot type to use.\n', 'cyan'))

args = my_parser.parse_args()

typ = str(args.type)
dataset = args.dataset
opt = args.opt
plot_type = args.plot_type

if not os.path.exists('plots'):
    os.mkdir('plots')

saves_folder = f'saves_running/{dataset}/type{typ}/'

rmses = [] # RMSEs to plot
ratios = [] # Rations to plot
labels = [] # Labels of the points

months = ['march', 'april', 'may', 'june', 'july', 'august']

# For each batch
for i in range(len(months) - 1):

    # Pickle file locations for this batch
    save_name = f'{saves_folder}/{months[i]}.pkl' # Training result
    save_name_ev = f'{saves_folder}/{months[i+1]}_eval.pkl' # Valuation result

    with open(save_name, 'rb') as f:
        save = pickle.load(f)
        res = save[0]  # Dictionary: Individual to (RMSE,ratio)

    # Get best individual
    best = sorted(res.items(), key=lambda kv: crit(
        kv[1][0], kv[1][1], opt))[0][0]

    # Load evaluation results
    if os.path.exists(save_name_ev):
        with open(save_name_ev, 'rb') as f:
            save = pickle.load(f)
            res_ev = save  # Dictionary: Individual to (RMSE,ratio)
    else:
        res_ev = {}

    # if best individual not in dict raise error.
    if best not in res_ev:
        raise RuntimeError(
            f'Option {opt}, didnt found {best}. Run r_eval.py')

    # (rmse, ratio) of best individual in valuation set
    t = res_ev[best]

    labels.append(months[i+1].title()[:3]) # Save month name (first 3 letters)
    rmses.append(t[0])
    ratios.append(100*t[1])

# print([f'{x:.2f}' for x in rmses])
# print([f'{x:.2f}' for x in ratios])
print(min(rmses), '\t', max(rmses))
print(min(ratios), '\t', max(ratios))
print()

plt.rcParams.update({'font.size': 16})


if plot_type == 'bars':

    fig = plt.figure(figsize=(5, 3)) # Create matplotlib figure

    ax = fig.add_subplot(111) # Create matplotlib axes
    ax2 = ax.twinx() # Create another axes that shares the same x-axis as ax.

    my_range = range(len(rmses))

    ax.bar([i-0.19 for i in my_range], rmses, width=0.36, color='red')
    ax2.bar([i+0.19 for i in my_range], ratios, width=0.36, color='blue')

    plt.xticks(list(my_range), labels)

    ax.set_ylabel('RMSE (M)', color='red')
    ax2.set_ylabel('Ratio (%)', color='blue')

    ax.tick_params(axis='y', colors='red')
    ax2.tick_params(axis='y', colors='blue')

# plot lines
else:
    fig = plt.figure(figsize=(6.3, 3.5)) # Create matplotlib figure

    ax = fig.add_subplot(111) # Create matplotlib axes
    ax2 = ax.twinx() # Create another axes that shares the same x-axis as ax.

    my_range = range(len(rmses))
    to_pop = []

    ax.plot(my_range, rmses, marker='o', color='red')
    ax2.plot(my_range, ratios, marker='o', color='blue')

    ax.set_ylabel('RMSE (m)', color='red')
    ax2.set_ylabel('Ratio (%)', color='blue')

    ax.tick_params(axis='y', colors='red')
    ax2.tick_params(axis='y', colors='blue')

    # ax.set_xlim((my_range[0]-0.05*range_len, my_range[-1]+0.05*range_len))
    # ax2.set_xlim((my_range[0]-0.05*range_len, my_range[-1]+0.05*range_len))

    # ax.set_ylim((0.0, 90.0))
    # ax2.set_ylim((0.0, 50.0))

    ax.set_ylim((0.0, 200.0))
    ax2.set_ylim((0.0, 90.0))

    ax.grid(True, axis='x')
    ax2.grid(True, axis='x')

    ax.hlines(60, -1000, 1000, color='r', linestyles='solid', alpha=0.5)

    ax.set_xlim((-4/20, 4 + 4/20))
    ax2.set_xlim((-4/20, 4 + 4/20))

    plt.xticks(list(my_range), labels, fontsize=1)

plt.savefig(f'plots/plot_online_eval_{dataset}_{typ}.png', bbox_inches='tight', dpi=400)
