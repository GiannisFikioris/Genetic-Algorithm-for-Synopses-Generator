#!/bin/python3


import datetime

import matplotlib.pyplot as plt
import numpy as np

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


intervals = []

prev = {}

first = True
d = {}


for l in open('ais.csv'):
    w = l.split(',')

    if first:
        first = False
        for i in range(len(w)):
            d[w[i]] = i
        continue

    idd = w[d['shipid']] if len(w[d['shipid']]) != '' else '999'
    t = int(datetime.datetime.strptime(w[d['t']], '%Y-%m-%dT%H:%M:%SZ').timestamp())

    if idd in prev and 0 < t - prev[idd] <= 200:
        intervals.append(t - prev[idd])

    prev[idd] = t

plt.hist(intervals, bins=100, density=True)
plt.xlabel('Seconds between two consecutive points')
plt.ylabel('Frequency')
plt.title(f'Histogram for the Small dataset')
plt.show()
# plt.savefig(f'/home/giannis/git/DemokritosMisc/NewReport/histograms/brest_{typ}.png')

print(np.mean(intervals))
print(np.std(intervals))
