#!/bin/python3


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

typ = argv[1]

intervals = []

prev = {}

for l in open(f'data_per_type/all/type_{typ}.csv'):

    w = l.split()

    t = int(w[0])//1000
    idd = w[1]

    if idd in prev and 0 < t - prev[idd] <= 250:
        intervals.append(t - prev[idd])

    prev[idd] = t

plt.hist(intervals, bins=100, density=True)
plt.xlabel('Seconds between two consecutive points')
plt.ylabel('Frequency')
plt.title(f'Histogram for the Brest dataset - {D[typ]}')
# plt.show()
plt.savefig(f'/home/giannis/git/DemokritosMisc/NewReport/histograms/brest_{typ}.png')
