#!/bin/python3


import datetime
from sys import argv

import matplotlib.pyplot as plt

D = {
    '60': 'Passenger',
    '0': 'Unknown',
    '30': 'Fishing',
    '52': 'Tug',
    '70': 'Cargo',
    '80': 'Tanker',
    '35': 'Military',
    '90': 'Other',
    '50': 'Pilot Vessel',
    '37': 'Pleasure Craft',
    '36': 'Sailing Vessel',
    '51': 'Search and Rescue'
}


first = True
d = {}

dens = {}

for l in open('ais.csv'):
    w = l.split(',')

    if first:
        first = False
        for i in range(len(w)):
            d[w[i]] = i
        continue

    idd = w[d['shipid']] if len(w[d['shipid']]) != '' else '999'

    dens[idd] = dens.get(idd, 0) + 1


plt.hist(list(dens.values()), bins=100, density=True)
plt.xlabel('Number of points per ship')
plt.ylabel('Frequency')
plt.title(f'Density Histogram for the Small dataset')
plt.show()
