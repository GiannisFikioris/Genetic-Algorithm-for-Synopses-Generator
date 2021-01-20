#!/usr/bin/python3


import matplotlib.pyplot as plt


dict = {
    37: 'Pleasure Craft',
    60: 'Passenger Ship',
    52: 'Tug',
    80: 'Tanker',
    70: 'Cargo',
    40: 'High-Speed Craft',
    90: 'Other'
}

first = True
d = {}
types = {}

for l in open('ais.csv'):
    w = l.split(',')

    if first:
        first = False
        for i in range(len(w)):
            d[w[i]] = i
        continue

    typ = int(w[d['shiptype']]) if w[d['shiptype']] != '' else 90
    if 40 <= typ <= 49:
        typ = 40
    elif 60 <= typ <= 69:
        typ = 60
    elif 70 <= typ <= 79:
        typ = 70
    elif 80 <= typ <= 89:
        typ = 80
    elif 90 <= typ <= 99:
        typ = 90

    types[typ] = types.get(typ, 0) + 1

x = sorted([(s, dict.get(l, '')) for l, s in types.items()], reverse=True)

sizes, labels = zip(*x)
# print(labels)
labels = [l for l in labels if len(l) > 0]

# fig1, ax1 = plt.subplots()
plt.pie(sizes, autopct='%1.1f%%', shadow=True, startangle=90)
plt.legend(labels, loc='lower right')
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

plt.show()
