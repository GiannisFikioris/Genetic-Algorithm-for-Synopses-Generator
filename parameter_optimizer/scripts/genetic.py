#!/usr/bin/python3


import argparse
import os
import pickle
import random
import sys
from time import time
from typing import List

import numpy as np
from deap import algorithms, base, creator, tools
from termcolor import colored
from tqdm import tqdm

from local_lib import DEF_PARAMS, PARAMETERS, Daemon, crit


class progress_bar:  # pylint: disable=missing-class-docstring
    def __init__(self, length):
        self.pbar = tqdm(total=length)
        self.counter = length
        self.first = True

    def update(self, *args): # pylint: disable=missing-function-docstring,unused-argument
        if self.first:
            self.first = False
            return

        self.pbar.update()
        self.counter -= 1
        if self.counter <= 0:
            self.pbar.close()


def eprint(*args, **kwargs):
    """Print in std err
    """
    print(*args, file=sys.stderr, **kwargs)


def evaluate(individual: List): # pylint: disable=missing-function-docstring
    global results
    global opt
    global daemon
    global running_stats
    global PARAMETERS

    if tuple(individual) in results:
        # If already found this input, return the previous value
        rmse = results[tuple(individual)][0]
        ratio = results[tuple(individual)][1]
        return crit(rmse, ratio, opt),

    # Create a dict with params from individual
    params = {}
    i = 0
    for k, v in PARAMETERS.items():
        # If value outside of range, return huge value
        if individual[i] < v[0] or individual[i] > v[1]:
            return 1e20,

        # Else save in params the value of the individual
        params[k] = individual[i]
        i += 1

    # Save cur time
    start_time = time()

    # Run synopses and estimate RMSE and compression ratio
    rmse, ratio = daemon.run_synopses(params)

    # Save Running time to stats
    running_stats['total'] += round(time() - start_time)
    running_stats['runs'] += 1

    # Add result to results-dictionary
    results[tuple(individual)] = (rmse, ratio)
    # print(rmse, ratio)
    return crit(rmse, ratio, opt),


def individual_generator():
    """Generates an individual
    Uses parameters dictionary to generate a random value

    Returns:
       [Individual]
    """
    global results
    global opt
    if len(results) > 10 and random.random() < 0.7:
        hof = sorted(results.items(), key=lambda kv: crit(
            kv[1][0], kv[1][1], opt))[:10]
        ind = list(random.choice(hof)[0])
    else:
        ind = []
        for v in PARAMETERS.values():
            if isinstance(v[0], int):
                x = random.randint(*v)
                if x > 200:
                    x = 50*round(x/50)
                else:
                    pass
                ind.append(x)
            elif isinstance(v[0], float):
                ind.append(round(random.uniform(*v), 2))
            else:
                raise NotImplementedError(
                    'Generator only supports int and float')
    return creator.Individual(ind) # pylint: disable=no-member


def mutate_ind(ind, low: List, up: List, indpb: float):
    """Mutates an individual of values (int or float)    by adding gaussian noise with std proportional to the range of values/

    Arguments:
       ind {Individual}
       low {List} -- List of values (int or float). Lower bounds for each parameter
       up {List} -- List of values (int or float). Upper bounds for each parameter
       indpb {float} -- Probability with which to mutate each characteristic

    Returns:
       Individual -- New individual
    """

    # Loop for every value of the individual
    for i in range(len(ind)):

        # Mutate cur value with probability indpb
        if random.random() < indpb:

            # Make Gaussian Noise from upper and lower bounds
            std = (up[i] - low[i])/4
            div = np.random.normal(scale=std)

            if isinstance(ind[i], int):
                # Add noise to individual
                x = int(ind[i]+div)

                # Re adjust individual to bounds
                x = max(x, low[i])
                x = min(x, up[i])
                if x > 200:
                    ind[i] = 50*round(x/50)
                else:
                    ind[i] = x

            elif isinstance(ind[i], float):
                x = round(ind[i]+div, 2)

                # Re adjust individual to bounds
                x = max(x, low[i])
                x = min(x, up[i])
                ind[i] = x

            else:
                raise NotImplementedError(
                    'mutate_ind only supports float or int')
    return ind,


my_parser = argparse.ArgumentParser(description='Runs a genetic algorithm',
                                    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))

my_parser.add_argument('-type',
                       type=int,
                       required=True,
                       help=colored('The type of ship\n', 'cyan'))

my_parser.add_argument('-p',
                       type=int,
                       required=True,
                       #    choices=range(1, 31),
                       help=colored('The part to exclude, e.g. if -p=3, will train on parts 1,2,4,5,6\n', 'cyan'))

my_parser.add_argument('-opt',
                       type=str,
                       required=True,
                       help=colored('Optimization option.\n', 'cyan'))

my_parser.add_argument('-data',
                       type=str,
                       required=True,
                       choices=sorted([d for d in os.listdir('../../data') if os.path.isdir(os.path.join('../../data/', d))]),
                       help=colored('Dataset from which to read.\n', 'cyan'))

my_parser.add_argument('-ngen',
                       type=int,
                       default=15,
                       help=colored('Number of generations in the gentic algorithm.\n', 'cyan'))

my_parser.add_argument('-pops',
                       type=int,
                       default=15,
                       help=colored('Population size to use in the gentic algorithm.\n', 'cyan'))

my_parser.add_argument('-fcode',
                       type=str,
                       default='month',
                       required=True,
                       help=colored('The files from which to read. This refers to files in ../../data/*/data_per_type/cross/\n', 'cyan'))

args = my_parser.parse_args()

ship_type = str(args.type)
part = args.p
opt = args.opt
dataset = args.data
fcode = args.fcode

s = part - (part-1) % 6
parts = list(map(str, range(s, s+6)))
parts.remove(str(part))

# Low and High Limits for mutation
lows = [x[0] for x in PARAMETERS.values()]
highs = [x[1] for x in PARAMETERS.values()]

# Location where results are saved
save_name = 'saves/{}/type{}/{}{}.pkl'.format(dataset, ship_type, fcode, part)
eprint(colored(save_name, 'blue'))

os.makedirs('saves/{}/type{}'.format(dataset, ship_type), exist_ok=True)

if os.path.exists(save_name):
    # If previous results exist, then load them
    with open(save_name, 'rb') as file:
        save = pickle.load(file)
        results = save[0]  # Fitness of each value
        old_running_stats = save[1]  # Old Running statistics
else:
    # Dictionary with previous results of individuals
    results = {}
    # Dictionary with old running stats
    old_running_stats = {
        'total': 0,
        'runs': 0
    }

# Initialize dict for current running stats
running_stats = {
    'total': 0,
    'runs': 0
}

# Genetic Algorithm Parameters
cxpb = 0.4     # Cross-over Prob
mutpb = 0.8    # Mutation Prob

# Number of generations
ngen = args.ngen
# Population Size
pop_size = args.pops

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

# Individual Class
creator.create("Individual", list,
               fitness=creator.FitnessMin)  # pylint: disable=no-member

toolbox = base.Toolbox()
# Individual Constructor
toolbox.register("individual", individual_generator)
# Population Constructor
toolbox.register("population", tools.initRepeat, list,
                 toolbox.individual)  # pylint: disable=no-member

# Gen Algo Functions
toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mutate", mutate_ind, low=lows, up=highs, indpb=0.5)
toolbox.register("select", tools.selTournament, tournsize=3)

# Initial Population
pop = toolbox.population(n=pop_size)  # pylint: disable=no-member

# Initialize statistics
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

try:
    # Begin Daemon. Type of Daemon is declared in the top of
    # this file, in the import
    daemon = Daemon(ship_type, parts, dataset, fcode)

    eprint(colored('\n ******** Starting Genetic Algo ********\n', 'yellow'))

    evaluate(list(DEF_PARAMS))

    # Run Genetic Algo
    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=cxpb, mutpb=mutpb,
                                   ngen=ngen, stats=stats, verbose=True, halloffame=progress_bar(ngen))

finally:
    # Print HallOfFame - Best Individuals
    hof = sorted(results.items(), key=lambda kv: crit(kv[1][0], kv[1][1], opt))
    print(colored('\nFinished type {}, part {}, ngen={}, popsize={}'.format(
        ship_type, part, ngen, pop_size), 'blue'))

    for i in range(min(1, len(hof))):
        print(colored('Individual #{} has parameters'.format(
            i+1), 'green'), hof[i][0])
        print(colored('\t(RMSE, CompRatio) =', 'green'), hof[i][1])
        print()

    # Print Current running Statistics
    if running_stats['runs'] > 0:
        print(colored('\nAvg Running Time this run is {}'.format(
            running_stats['total']/running_stats['runs']), 'yellow'))
        old_running_stats['total'] += running_stats['total']
        old_running_stats['runs'] += running_stats['runs']

    # Print total running statistics
    if old_running_stats['runs'] > 0:
        print(colored('Total avg Running Time is {}'.format(
            old_running_stats['total']/old_running_stats['runs']), 'yellow'))

    # If found results save them
    if len(results) > 0:
        with open(save_name, 'wb') as file:
            save = (results, old_running_stats)
            pickle.dump(save, file)

    # End daemon
    daemon.end()

    eprint(colored('\n ******** Ended Genetic Algo ********\n', 'yellow'))
