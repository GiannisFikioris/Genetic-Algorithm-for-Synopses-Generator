#!/usr/bin/python3


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

from local_lib import Daemon
from local_lib import crit, PARAMETERS


def eprint(*args, **kwargs):
    """Print in std err
    """
    print(*args, file=sys.stderr, **kwargs)


def evaluate(individual: List):  # pylint: disable=missing-function-docstring
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
    if len(results) > 10 and random.random() < 0.4:
        hof = sorted(results.items(), key=lambda kv: crit(
            kv[1][0], kv[1][1], opt))[:15]
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
    return creator.Individual(ind)  # pylint: disable=no-member


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


# Get ship type from arguments
if len(sys.argv) < 4:
    print(colored('Not enough args. Give:\n{} ShipType Dataset FileCode'.format(
        sys.argv[0]), 'red'))
    raise ValueError()

ship_type = sys.argv[1]
dataset = sys.argv[2]
fcode = sys.argv[3]

# Low and High Limits for mutation
lows = [x[0] for x in PARAMETERS.values()]
highs = [x[1] for x in PARAMETERS.values()]

# Location where results are saved
save_name = 'saves/{}/type{}/{}.pkl'.format(dataset, ship_type, fcode)
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
ngen = 10       # Number of generations
pop_size = 10   # Population Size
hof_len = 1   # Hall of Fame Length

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

# Initialize statistics
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("min", np.min)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("max", np.max)


if dataset == 'brest':
    l1 = [2, 4, 7, 10, 13, 17]
    l2 = [0.7, 0.8, 1.0, 1.2, 1.4, 1.6]
elif dataset == 'mtraffic':
    l1 = [16, 24, 32, 42, 52, 62, 74, 88]
    l2 = [0.3, 0.45, 0.6, 0.75, 1.0, 1.3, 1.65, 2.0]
else:
    raise ValueError('Wrong dataset')

try:
    for x in tqdm(l1):
        for n in tqdm(l2):

            try:
                opt = 'new,{},{}'.format(n, x)

                # Initial Population
                pop = toolbox.population(  # pylint: disable=no-member
                    n=pop_size)
                # Begin Daemon. Type of Daemon is declared in the top of
                daemon = Daemon(ship_type, [''], dataset, file_names=[fcode])

                # Run Genetic Algo
                pop, log = algorithms.eaSimple(pop, toolbox, cxpb=cxpb, mutpb=mutpb,
                                               ngen=ngen, stats=stats, verbose=True)

            finally:
                daemon.end()
finally:
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
