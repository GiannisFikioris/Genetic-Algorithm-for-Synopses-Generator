#!/usr/bin/python3


import argparse
import os
import pickle
import random
import sys
from copy import deepcopy
from time import time
from typing import List

import numpy as np
from deap import algorithms, base, creator, tools
from termcolor import colored as col
from tqdm import tqdm

from local_lib import PARAMETERS, Daemon, crit


class progress_bar:
    """A class that is used to show the progress of the genetic algo, and is passed like a deap halloffae object.
    """

    def __init__(self, length: int):
        """Constructor.

        Args:
            length (int): The number of generations
        """

        self.pbar = tqdm(total=length)
        self.counter = length
        self.first = True
        self.save = []

    def update(self, offspring: List):  # pylint: disable=missing-function-docstring,unused-argument
        """A method with the same interface of the update method from the class HallOfFame of deap.
        Is used to update the progress bar.
        Also 

        Args:
            offspring (List): [description]
        """

        x = []
        for off in offspring:
            x.append(list(deepcopy(off)))
        self.save.append(x)

        if self.first:
            self.first = False
            return

        self.pbar.update()
        self.counter -= 1
        if self.counter <= 0:
            self.pbar.close()


def eprint(*args, **kwargs):
    """Print in std err.
    """
    print(*args, file=sys.stderr, **kwargs)


def evaluate(individual: List) -> float:
    """Given a list of synopses-parameters, runs the synopses-generator with them,
    finds the RMSE and Ratio, saves the result, and returns the fitness.
    If these parameters were already evaluated then it simply returns the fitness

    Args:
        individual (List): A list of values for the synopses parameters

    Returns:
        float: The fitness of the parameters
    """

    global results # Already valuated parameters
    global opt # optimizaton option
    global daemon # daemon that runs the synopses
    global PARAMETERS # List of synopses-parameter names and limites

    if tuple(individual) in results:
        # If already found this individual, return the already found fitness
        rmse = results[tuple(individual)][0]
        ratio = results[tuple(individual)][1]
        # Because of deap framework MUST return tuple
        return crit(rmse, ratio, opt),

    # Create a dict that maps the parameter name to the value
    # (This is the input required by the daemon)
    params = {}
    i = 0
    for k, v in PARAMETERS.items():
        # If value outside of range, return huge value
        if individual[i] < v[0] or individual[i] > v[1]:
            return 1e20,

        # Else save in params the value of the individual
        params[k] = individual[i]
        i += 1

    # Run synopses and estimate RMSE and compression ratio
    rmse, ratio = daemon.run_synopses(params)

    # Add result to results-dictionary
    results[tuple(individual)] = (rmse, ratio)

    # Save temp in case of crash
    with open(f'tmp/save{args.type}.pkl', 'wb') as f:
        save = (results, bar.save)
        pickle.dump(save, f)

    return crit(rmse, ratio, opt),


def individual_generator():
    """Generates a random individual.

    Returns:
       [Individual]
    """

    ind = []
    # For each parameter
    for v in PARAMETERS.values():

        # If parameter is int
        if isinstance(v[0], int):
            # Pick at random from the range
            x = random.randint(*v)

            # If range of params is large, roung the value to be a multiple of 50
            if x > 200:
                x = 50*round(x/50)

            ind.append(x)

        # If parameter is float
        elif isinstance(v[0], float):
            ind.append(round(random.uniform(*v), 2))

        else: # Should never reach here
            raise NotImplementedError('Generator only supports int and float')

    # Convert list to individual
    return creator.Individual(ind) # pylint: disable=no-member


def mutate_ind(ind, low: List, up: List, indpb: float):
    """Mutates an individual of values (int or float)
    by adding gaussian noise with std proportional to the range of values.

    Arguments:
       ind {Individual} -- The individual to mutate
       low {List} -- List of values (int or float). Lower bounds for each parameter
       up {List} -- List of values (int or float). Upper bounds for each parameter
       indpb {float} -- Probability with which to mutate each characteristic

    Returns:
       Individual -- New individual
    """

    # Loop for every value of the individual
    for i in range(len(ind)):

        # Mutate this value with probability indpb
        if random.random() < indpb:

            # Make Gaussian Noise from upper and lower bounds
            std = (up[i] - low[i])/4
            div = np.random.normal(scale=std)

            if isinstance(ind[i], int):

                # Add noise to individual and round
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


my_parser = argparse.ArgumentParser(description='Runs an online genetic algorithm',
                                    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=100))

my_parser.add_argument('data',
                       type=str,
                       choices=sorted([d for d in os.listdir('../../data') if os.path.isdir(os.path.join('../../data/', d))]),
                       help=col('Dataset from which to read.\n', 'cyan'))

my_parser.add_argument('type',
                       type=int,
                       help=col('The type of ship.\n', 'cyan'))

my_parser.add_argument('opt',
                       type=str,
                       help=col('Optimization option.\n', 'cyan'))

my_parser.add_argument('popsizes',
                       type=str,
                       help=col('Population Sizes for each batch, separated by commas (don\'t include spaces).\n', 'cyan'))

my_parser.add_argument('gennumbers',
                       type=str,
                       help=col('Number of Generations for each batch, separated by commas (don\'t include spaces).\n', 'cyan'))

my_parser.add_argument('--start_from', '-s',
                       type=int,
                       default=0,
                       help=col('How many of the first batches to skip (used to start from the middle).\n', 'cyan'))

args = my_parser.parse_args()

dataset = args.data
ship_type = str(args.type)
opt = args.opt
pop_sizes = list(map(int, args.popsizes.split(',')))
gen_numbers = list(map(int, args.gennumbers.split(',')))
start_from = int(args.start_from)

print(col(f'OptFunc {opt}, Type {ship_type} {dataset}\n', 'blue'))

# Low and High Limits for mutation
lows = [x[0] for x in PARAMETERS.values()]
highs = [x[1] for x in PARAMETERS.values()]

# Location where results are saved
saves_folder = f'saves_running/{dataset}/type{ship_type}/'
eprint(col(saves_folder, 'blue'))

os.makedirs(saves_folder, exist_ok=True)

# File names
if dataset == 'mtraffic':
    months = ['march', 'april', 'may', 'june', 'july', 'august']
elif dataset == 'brest':
    months = ['month1', 'month2', 'month3', 'month4', 'month5', 'month6']
else:
    raise NotImplementedError('Dataset ' + dataset + ' is not implemented yet')

# Genetic Algorithm Parameters
cxpb = 0.4     # Cross-over Prob
mutpb = 0.8    # Mutation Prob

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
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

# If start_from=0 (normal run),
# then loop for all batrches except the last one
for m in range(start_from, len(months) - 1):

    # Dictionary with mapping from individual to (RMSE, Ratio)
    results = {}

    # Population size and Number of generations for this training
    pop_size = pop_sizes[min(m, len(pop_sizes))]
    ngen = gen_numbers[min(m, len(gen_numbers))]

    # List of individuals of previous run (sorted from best-fitness to worst-fitness)
    best = []

    # If starting from middle
    if m == start_from and m > 0:

        # Open the file with the previous results and load dicitonary
        with open(f'{saves_folder}/{months[m-1]}.pkl', 'rb') as f:
            temp = pickle.load(f)[0]

        # Sort individuals according to optimization function
        hof = sorted(temp.items(), key=lambda kv: crit(kv[1][0], kv[1][1], opt))

        # Take the individuals sorted according to fitness
        best = [kv[0] for kv in hof]
        eprint('Read from', months[m-1])

    try:
        # Begin Daemon. This workso only for the mtraffic dataset. If would like to work for the brest dataset,
        # the change the 2nd argument of the constructor.
        daemon = Daemon(ship_type, ['1', '2', '3',
                                    '4', '5', '6'], dataset, months[:m+1])

        eprint(col(f'\n ******** Starting Genetic Algo on {months[m]} ********\n', 'yellow'))

        # Initial Population
        if len(best) == 0:
            # Random initializetion if best is empty (no previous results)
            pop = toolbox.population(n=pop_size)  # pylint: disable=no-member
        else:
            # Initializetion from previous results (top individuals)
            pop = [creator.Individual(best[i]) for i in range(pop_size)]  # pylint: disable=no-member

        # Start progress bar and place where individuals are saved
        bar = progress_bar(ngen)

        t = time()

        # Run Genetic Algo
        pop, log = algorithms.eaSimple(pop, toolbox, cxpb=cxpb, mutpb=mutpb,
                                       ngen=ngen, stats=stats, verbose=True, halloffame=bar)

        # Runing time
        t = time() - t
    finally:
        daemon.end()

    # Best contains the individuals of this training, sorted by fitness from best to worst
    hof = sorted(results.items(), key=lambda kv: crit(kv[1][0], kv[1][1], opt))
    best = [kv[0] for kv in hof]

    # Print Running time
    print(col(f'\nTotal Running Time this run is {t} s', 'yellow'))

    # File where results are saved (the name of of the .pkl file is the last batvh used for training)
    save_name = f'{saves_folder}/{months[m]}.pkl'

    # If found results save them
    if len(results) > 0:
        with open(save_name, 'wb') as f:
            # `results` contains the dict that maps individual to (RMSE, Ratio).
            # `bar.save` contains the list of lists of individuals (denoting which individuals were in each generation).
            save = (results, bar.save)
            pickle.dump(save, f)
    else:
        raise RuntimeError('Results are empty!')

    eprint(col(f'\n ******** Ended Genetic Algo on {months[m]} ********\n', 'yellow'))
