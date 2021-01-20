#!/usr/bin/python3


import argparse
import os
import pickle

import matplotlib.pyplot as plt
from termcolor import colored as col

from local_lib import crit


my_parser = argparse.ArgumentParser(description='Plots the progress of the incremental genetic algo on the training set.',
                                    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))

my_parser.add_argument('dataset',
                       type=str,
                       choices=sorted([d for d in os.listdir('../../data') if os.path.isdir(os.path.join('../../data/', d))]),
                       help=col('Dataset from which to read.\n', 'cyan'))

my_parser.add_argument('type',
                       type=int,
                       help=col('The type of ship\n', 'cyan'))

my_parser.add_argument('opt',
                       type=str,
                       help=col('Optimization option.\n', 'cyan'))

args = my_parser.parse_args()

typ = str(args.type)
dataset = args.dataset
opt = args.opt

if not os.path.exists('plots'):
    os.mkdir('plots')

log_file = f'logs/running_{dataset}_{typ}_t60_new.log'
save_folder = f'saves_running/{dataset}/type{typ}/'

# List of generations,
# i.e. if we have 2 batches of 10 and 5 generations,
# then gens = [range(10), range(5)]
gens = []

rmses = [] # List of lists  of rmses of the best individual in each generation
ratios = [] # List of lists of ratios of the best individual in each generation

# Only works for brest dataset (timespane of march-august)
for m in ['march', 'april', 'may', 'june', 'july']:

    try:
        with open(f'{save_folder}{m}.pkl', 'rb') as f:
            save = pickle.load(f)
            res = save[0]   # RMSE and Ratio of each individual (dictionary)
            order = save[1] # Individuals of each generation
    except:
        break

    c_rmses = [] # List of rmses of the best individuals for this generation
    c_ratios = [] # List of ratios of the best individuals for this generation

    for g in range(len(order)):
        minn = 1e30
        argmin = -1

        # For each individual (ind) in this generation
        for i, ind in enumerate(order[g]):
            err, rat = res[tuple(ind)]
            fit = crit(err, rat, opt) # Calculate fitness
            
            # Save best individual
            if fit < minn:
                minn = fit
                argmin = i

        err, rat = res[tuple(order[g][argmin])]
        c_rmses.append(err)
        c_ratios.append(100*rat)

    # I dont know what is this
    if len(order) == 10 and typ == '70':
        order.append(0)
        c_rmses.append(c_rmses[-1])
        c_ratios.append(c_ratios[-1])

    gens.append(list(range(len(order))))
    rmses.append(c_rmses)
    ratios.append(c_ratios)

print(f'{min(map(min, rmses)):.1f}, {max(map(max, rmses)):.1f}')
print(f'{min(map(min, ratios)):.1f}, {max(map(max, ratios)):.1f}\n')



# fig = plt.figure(figsize=(5, 4)) # Create matplotlib figure

# ax = fig.add_subplot(111) # Create matplotlib axes
# ax2 = ax.twinx() # Create another axes that shares the same x-axis as ax.

# my_range = range(len(rmses))
# to_pop = []

# for i in my_range:
#     if labels[i] == 'GA':
#         ax.hlines(rmses[i], -1000, 1000, label='GA', color='r', alpha=0.5)
#         ax2.hlines(ratios[i], -1000, 1000, label='GA', color='b', alpha=0.5)
#         to_pop.append(i)
# to_pop.reverse()
# for i in to_pop:
#     labels.pop(i)
#     rmses.pop(i)
#     ratios.pop(i)

# my_range = [int(t) for t in labels]
# # my_range = range(len(rmses))

# range_len = max(my_range) - min(my_range)


# ax.plot(my_range, rmses, marker='o', color='red')
# ax2.plot(my_range, ratios, marker='o', color='blue')

# ax.set_ylabel('RMSE', color='red')
# ax2.set_ylabel('Ratio', color='blue')

# ax.tick_params(axis='y', colors='red')
# ax2.tick_params(axis='y', colors='blue')

# ax.set_xlim((my_range[0]-0.05*range_len, my_range[-1]+0.05*range_len))
# ax2.set_xlim((my_range[0]-0.05*range_len, my_range[-1]+0.05*range_len))

# # ax.set_ylim((0.0, 90.0))
# # ax2.set_ylim((0.0, 50.0))

# ax.set_ylim((30.0, 200.0))
# ax2.set_ylim((15.0, 70.0))

# ax.grid(True, axis='x')
# ax2.grid(True, axis='x')

# plt.xticks(list(my_range), labels, fontsize=1)
# plt.grid(True)

# plt.savefig(f'plots/plot_{dataset}_{fcode}_{typ}.png', bbox_inches='tight')



##################
# Plotting Time! #
##################


plt.rcParams.update({'font.size': 16})
fig = plt.figure(figsize=(7, 4)) # Create matplotlib figure


ax = fig.add_subplot(111) # Create matplotlib axes
ax2 = ax.twinx() # Create another axes that shares the same x-axis as ax.

colors = ['g', 'b', 'c', 'y', 'k']

start = 0 # Which position (in the graph) is available. 

labels = [] # Labels in the x-axis
labels_pos = [] # Their positions

for i in range(len(gens)):

    # Vertical line that splits different batches.
    if i > 0:
        ax.axvline(start - .5, alpha=0.2, c='black')

    # Plot rmses and ratios
    ax.plot(range(start, start + len(gens[i])), rmses[i], marker='o', color='red', markersize=4)
    ax2.plot(range(start, start + len(gens[i])), ratios[i], marker='o', color='blue', markersize=4)

    # Variable step shows the distance between ticks in the x-axis
    if len(gens[i]) == 16:
        step = 4
    elif len(gens[i]) == 9:
        step = 3
    elif len(gens[i]) == 11:
        step = 4
    else:
        print('Unknown range:', len(gens[i]))
        step = 1

    # x labels and their positions
    labels += list(range(0, len(gens[i]), step))
    labels_pos += list(range(start, start + len(gens[i]), step))

    # Save the next available position
    start += len(gens[i])

ax.set_ylabel('RMSE (m)', color='red')
ax2.set_ylabel('Ratio (%)', color='blue')

ax.tick_params(axis='y', colors='red')
ax2.tick_params(axis='y', colors='blue')

# Set limits (this is hand-picked probably would want to change later)
ax.set_ylim((0.0, 140.0))
ax2.set_ylim((0.0, 90.0))

# Horizontal line for threshold in the optimization function
ax.hlines(60, -1000, 1000, color='r', linestyles='solid', alpha=0.5)

# Set limits in the x-axis because of hlines 
start -= 1
ax.set_xlim((-start/20, start + start/20))
ax2.set_xlim((-start/20, start + start/20))

ax.set_xlabel('Generation')

plt.xticks(labels_pos, labels)

plt.savefig(f'plots/plot_online_{dataset}_{typ}.png', bbox_inches='tight', dpi=400)
# plt.show()
