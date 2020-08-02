#!/bin/python3


import os


for ship_type in map(lambda x: x[5:-4], os.listdir('data_per_type/all')):

    lines = 0

    with open(f'data_per_type/all/type_{ship_type}.csv', 'r') as f:
        for row in f:
            lines += 1

    if lines < 1000:
        continue

    with open(f'data_per_type/all/type_{ship_type}.csv', 'r') as f:
        data = []
        i = 1
        len_id = {}
        for row in f:
            words = row.split(' ')
            idd = words[1]
            if idd not in len_id:
                len_id[idd] = 0
            len_id[idd] += 1
            data.append((idd, row))

            if i < 6 and 6*len(data) >= lines:
                if not os.path.exists(f'data_per_type/cross/type{ship_type}'):
                    os.mkdir(f'data_per_type/cross/type{ship_type}')

                final_len = 0
                with open(f'data_per_type/cross/type{ship_type}/month{i}.csv', 'w') as ff:
                    for idd, x in data:
                        if len_id[idd] > 200:
                            ff.write(x)
                            final_len += 1
                print(i, final_len)
                i += 1
                data = []
                len_id = {}

        if not os.path.exists(f'data_per_type/cross/type{ship_type}'):
            os.mkdir(f'data_per_type/cross/type{ship_type}')
        final_len = 0
        with open(f'data_per_type/cross/type{ship_type}/month{i}.csv', 'w') as ff:
            for idd, x in data:
                if len_id[idd] > 200:
                    ff.write(x)
                    final_len += 1
        print(i, final_len)
        i += 1
        data = []
        len_id = {}

    # print(len(data_id), total)
    # print(sorted(list(map(len, data_id.values()))))
    # n, bins, patches = plt.hist(x=list(map(len, data_id.values())))

    # plt.show()
