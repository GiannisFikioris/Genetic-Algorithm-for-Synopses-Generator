"""Import for controlling the synopses, as well as important global variables/functions
"""

import json
import os
import shutil
from collections import OrderedDict
from copy import deepcopy
from math import asin, cos, radians, sin, sqrt
from os.path import join
from shutil import copyfile
from subprocess import PIPE, Popen
from typing import Dict, List, Tuple


# The mapping from type number to name
SHIP_TYPES = {
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

# Name of the synopses parameters and the range to search from.
PARAMETERS = OrderedDict([
    ('ANGLE_THRESHOLD', (2.0, 25.0)),  # Controls Turning Crit. Points
    ('GAP_PERIOD', (200, 5000)),  # Controls Gap Crit. Points
    ('BUFFER_SIZE', (3, 50)),  # Controls Number of points in buffer
    ('HISTORY_PERIOD', (300, 5000)),  # Controls how long the buffer is in seconds
    ('NO_SPEED_THRESHOLD', (0.05, 2.0)),  # Controls Stop Crit. Points
    ('DISTANCE_THRESHOLD', (2.0, 100.0)),  # Controls how long the buffer is in meters, and whether to terminate stop event
    ('SPEED_RATIO', (0.01, 0.8)),  # Controls ChangeInSpeed Crit. Points
    ('LOW_SPEED_THRESHOLD', (0.05, 8.0))  # Controls SlowMotion Crit. Points
])

# Default parameters
DEF_PARAMS = (4, 1800, 5, 3600, 0.5, 50.0, 0.25, 5.0)

# Brest GA's parameters when opt func was $Ratio + ReLU(RMSE - 10)$
# OPT_BREST_PARAMS = {
#     '60': [6.4, 200, 38, 4200, 1.15, 49.81, 0.32, 7.76],
#     '0':  [10.47, 200, 13, 2350, 0.76, 38.28, 0.07, 0.83],
#     '30': [23.95, 200, 3, 1100, 0.41, 36.31, 0.01, 3.62],
#     '52': [25.0, 1550, 16, 300, 0.93, 52.88, 0.01, 0.58],
#     '70': [25.0, 200, 3, 5000, 0.66, 6.89, 0.04, 1.87],
#     '35': [14.14, 2300, 3, 500, 0.93, 22.54, 0.01, 0.44]
# }

# Brest GA's parameters when opt func was $Ratio + ReLU(RMSE - 15)$
OPT_BREST_PARAMS = {
    '60': [9.83, 200, 44, 3400, 1.41, 57.18, 0.34, 6.22],
    '0':  [13.67, 200, 4, 2400, 1.18, 15.03, 0.01, 0.8],
    '30': [25.0, 300, 3, 2150, 0.71, 56.96, 0.01, 0.98],
    '52': [23.49, 600, 43, 4050, 1.26, 34.78, 0.01, 0.48],
    '70': [22.46, 200, 3, 2450, 0.63, 17.94, 0.01, 4.59],
    '35': [21.49, 2650, 3, 1350, 1.25, 28.19, 0.01, 0.4]
}

# I think these are from the old optimization funciton
# OPT_BREST_PARAMS = {
#     '60': [10.71, 200, 50, 2750, 2.0, 76.51, 0.63, 4.58],
#     '0':  [17.58, 400, 21, 1500, 1.52, 44.45, 0.01, 1.02],
#     '30': [18.99, 200, 3, 3550, 0.41, 23.97, 0.01, 0.61],
#     '52': [4.96, 450, 29, 2300, 0.84, 2.0, 0.01, 6.06],
#     '70': [17.5, 2500, 3, 1750, 0.81, 15.12, 0.01, 0.82],
#     '35': [11.68, 2600, 3, 4800, 0.88, 22.96, 0.01, 0.45]
# }


# Type to type matching.
# The first argument is similar to the second argument (in terms of size, behavior, etc.)
TYPE_TO_TYPE = {
    '60': '60',
    '0': '0',
    '30': '30',
    '52': '52',
    '70': '70',
    '35': '35',
    '80': '70',
    '89': '70',
    '81': '70',
    '84': '70',
    '82': '70',
    '83': '70',
    '88': '70',
    '79': '70',
    '71': '70',
    '74': '70',
    '73': '70',
    '72': '70',
    '77': '70',
    '76': '70',
    '78': '70',
    '50': '52',
    '69': '60',
    '90': '0'
}

def crit(rmse: float, ratio: float, option: str) -> float:
    """Transforms rmse and ratio values to a single number, i.e. the optimization funciton

    Arguments:
        rmse {float} -- RMSE
        ratio {float} -- Ratio
        option {str} -- String code denoting which function to use.
                        * 'rmse'     ->   RMSE
                        * 'mult,x'   ->   RMSE^x * Ratio
                        * 'new,x,y'  ->   (RMSE+y)^x * Ratio
                        * 'max,x,y'  ->   max(RMSE, y)^x * Ratio
                        * 'thresh,x' ->   ReLU(RMSE - x)^x + Ratio

    Returns:
        float -- The result of the optimization function
    """

    if option == 'rmse':
        return rmse
    if 'mult' in option:
        i = float(option[4:])
        return (rmse**i)*ratio
    if 'new' in option:
        opts = option.split(',')
        i = float(opts[1])
        j = float(opts[2])
        return ((rmse+j)**i)*ratio
    if 'max' in option:
        opts = option.split(',')
        i = float(opts[1])
        j = float(opts[2])
        return (max(rmse, j)**i)*ratio
    if 'thresh' in option:
        opts = option.split(',')
        r = float(opts[1])
        return ratio + max(0, rmse-r)
    raise RuntimeError('Wrong value for optimizaton criterion')


def interpolate(lon1: float, lat1: float, t1: int, lon2: float, lat2: float, t2: int, t: int) -> Tuple[float, float]:
    """Estimate the time-synchronized interpolated location at time t between two
    other timestamped locations (lon1, lat1, t1) and (lon2, lat2, t2) georeferenced at WGS84.

    Arguments:
        lon1 {float} -- Position 1 lon
        lat1 {float} -- Position 1 lat
        t1 {int} -- Position 1 timestamp
        lon2 {float} -- Position 2 lon
        lat2 {float} -- Position 2 lat
        t2 {int} -- Position 2 timestamp
        t {int} -- Time to interpolate

    Returns:
        Tuple[float,float] -- Interpolated (lon, lat)
    """

    if t2 > t1:   # Verify that the first position precedes the second one
        lon = lon1 + (t - t1) * (lon2 - lon1) / (t2 - t1)
        lat = lat1 + (t - t1) * (lat2 - lat1) / (t2 - t1)
    else:           # Timestamp values coincide, so return the second position
        lon = lon2
        lat = lat2
    return lon, lat


def project(lon1: float, lat1: float, lon2: float, lat2: float, lon: float, lat: float) -> Tuple[float, float]:
    """Estimate the projection of (lon,lat) on the line created by the 2 points (lon1,lat1) and (lon2,lat2)

    Arguments:
        lon1 {float}
        lat1 {float}
        lon2 {float}
        lat2 {float}
        lon {float}
        lat {float}

    Returns:
        Tuple[float,float] -- Projected (lon, lat)
    """

    if (lon1, lat1) == (lon2, lat2):
        return lon1, lat1

    a = -(lat2-lat1)
    b = lon2-lon1
    c = lon1*(lat2-lat1) - lat1*(lon2-lon1)

    est_lon = (b*(b*lon - a*lat) - a*c)/(a**2 + b**2)
    est_lat = (a*(-b*lon + a*lat) - b*c)/(a**2 + b**2)
    return est_lon, est_lat


def haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Calculate the Haversine distance between two geographic locations (lon1, lat1) and (lon2, lat2)
    This is the great circle distance between two points on the Earth (both specified in decimal degrees at WGS84)

    Arguments:
        lon1 {float}
        lat1 {float}
        lon2 {float}
        lat2 {float}

    Returns:
        float -- haversine distance
    """

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000    # Approximate radius of the Earth in meters
    return c * r   # distance in meters


def estimate_RMSE(in_data: Dict[str, List[Tuple]], out_data: Dict[str, List[Tuple]], noise: Dict[str, Dict[Tuple, int]], proj: bool = False) -> Tuple[float, float]:
    """Function that estimates RMSE and compression ratio from data and noisy points.

    Arguments:
        in_data {Dict[str, List[Tuple[float,float,int]]]} -- Holds the uncompressed points (also contains noisy points).
                                                             It is a dictionary that maps a ship-ID to a list of tuples.
                                                             Each tuple is a point: (lon,lat,t).

        out_data {Dict[str, List[Tuple[float,float,int]]]} -- Holds the compressed points. It is a dictionary that maps
                                                              a ship-ID to a list of tuples. Each tuple is a point: (lon,lat,t).

        noise {Dict[str, Dict[Tuple[float, float, int], int]]} -- A dict from ship-id to a dict. The second dictionary maps
                a point (lon,lat,t) to how many times its has been reported as noise. This should be sent as a copy, because the counters are reduced.

    Keyword Arguments:
        proj {bool} -- Whether to calculate approximate points using a simple projection (proj=True) or using time interpolation (proj=False) (default: {False})

    Returns:
        Tuple[float, float] -- RMSE and Compression Ratio
    """

    total_rmse = 0.0
    total_raw_points = 0
    total_approx_points = 0

    # Loop for each ship id
    # x is the double list
    for idd, raw in in_data.items():

        if idd not in out_data:
            continue

        # Get list of approximate-compressed points, sorted in time
        approx = sorted(out_data[idd], key=lambda t: t[2])

        n = len(raw)
        m = len(approx)

        # Add to total apprroximate points the number of (unique) critical points
        total_approx_points += len(set(map(lambda t: t[2], approx)))

        i = 0
        rmse = 0

        for j in range(m-1):

            # Get first approx point
            lon1 = approx[j][0]
            lat1 = approx[j][1]
            t1 = approx[j][2]

            # Get second approx point
            lon2 = approx[j+1][0]
            lat2 = approx[j+1][1]
            t2 = approx[j+1][2]

            if t1 > t2:
                raise RuntimeError('Approximate Data not in order')

            # Iterate over the respective items of RAW data during the specified time interval
            while i < n:

                # Get raw point
                lon = raw[i][0]
                lat = raw[i][1]
                t = raw[i][2]

                # Make key for noise dictionary
                k = (lon, lat, t)

                # Ignore points before first point
                if t < t1:
                    i += 1
                # If raw point is noisy ignore it
                elif idd in noise and k in noise[idd] and noise[idd][k] > 0:
                    i += 1
                    noise[idd][k] -= 1
                # Else, it holds that t \in [t1,t2]
                # Calculate distance of raw point from approximation
                elif t <= t2:

                    # Increase the counter of raw points
                    total_raw_points += 1

                    if proj:
                        # Simply project point into line
                        est_lon, est_lat = project(lon1, lat1, lon2, lat2, lon, lat)
                    else:
                        # Estimated location after interpolation at time t
                        est_lon, est_lat = interpolate(lon1, lat1, t1, lon2, lat2, t2, t)

                    # Deviation between raw and interpolated location
                    h = haversine(lon, lat, est_lon, est_lat)

                    # Update summation of error values
                    rmse += h * h
                    i += 1
                else:
                    break  # Consider the next time interval between successive locations in the COMPRESSED dataset

        # Add error to previously computed errors
        total_rmse += rmse

    # Calculate total error
    total_rmse = sqrt(total_rmse/total_raw_points)

    # Calculate Compression Ratio
    total_ratio = total_approx_points/total_raw_points

    return total_rmse, total_ratio


class Daemon:
    """Daemon made for controling the synopses. It makes that correct files, passes the parameters, uses flink, etc.
    """

    def __init__(self, ship_type: str, parts: List[str], dataset: str, file_names: List[str], one_file: bool = False, syn_prints_noise: str = 'true'):        
        """Constructor. Initializes input files and commands that will be used to run app.

        Arguments:
            ship_type (str): The number that corresponds to the ship type.
            parts (List[str]): A list of the parts to run on. (the strings in the list should be numbers).
            dataset (str): The dataset to use. Possible values: The folders of '../../data/'
            file_names (List[str]): [description]
            one_file (bool, optional): [description]. Defaults to False.
            syn_prints_noise (str, optional): Whether the Synopses-Generator will output noisy points or noiseless points. Defaults to 'true'.
        """

        self.home = os.path.expanduser('~/infore')
        scripts_fold = join(self.home, 'datacron/implementation/parameter_optimizer/scripts')

        # If temp folder does not exist, create it
        if not os.path.exists('tmp'):
            os.mkdir('tmp')

        # File that contains ids of other applications. To know what this is read the Daemon entry in ReadMe.md.
        self.ids_file = join(scripts_fold, 'tmp/ids.txt')

        # Create application unique id
        self.id = ''
        if os.path.exists(self.ids_file):
            with open(self.ids_file, 'r') as f:
                taken = set(f.read().split())
                for i in range(10):
                    j = str(i)
                    if j not in taken:
                        taken.add(j)
                        self.id = j
                        break
            if self.id == '':
                raise RuntimeError('All ids taken')
        else:
            taken = ['0']
            self.id = '0'

        # Store new file with previous ids + this application id
        with open(self.ids_file, 'w') as f:
            for i in taken:
                f.write(i + ' ')

        self.type = ship_type

        # File location from where input data for the compression will be read
        self.input_file = join(scripts_fold, 'tmp/type{}.in'.format(self.id))

        # File location where 1st output data will be stored (critical points without gap_start).
        self.output_file = join(scripts_fold, 'tmp/type{}.out'.format(self.id))

        # File location where 2nd output data will be stored (noisy or noiseless points, depending on the value of param `syn_prints_noise`).
        self.noise_file = join(scripts_fold, 'tmp/type{}_loc.out'.format(self.id))

        # File location where 3rd output data will be stored (originally called notifications, is basically gap_start critical points)
        self.not_file = join(scripts_fold, 'tmp/type{}_not.out'.format(self.id))

        # Template-File that will be modified to include the right set of parameters each time
        self.template_file_loc = join(self.home, 'datacron/implementation/parameter_optimizer/parameters/maritime_config_template.properties')
        if not os.path.exists(self.template_file_loc):
            raise FileNotFoundError(f'Template file does not exist in {self.template_file_loc}')

        # Location of file that will include the parameters used for the synopses
        self.param_file_loc = join(scripts_fold, 'tmp/maritime_config{}.properties'.format(self.id))

        # Jar file location to run from
        self.synopses_jar_loc = join(self.home, 'datacron/implementation/synopses_generator/target/datacron_trajectory_synopses-0.7-type{}.jar'.format(self.id))

        # Command that starts application and gives it as an argument the unique id and the input/outputfiles
        self.start_app = [
            'nice',
            join(self.home, 'flink-0.10.2/bin/flink'),
            'run',
            '-c',
            'eu.datacron.synopses.maritime.TrajectoryStreamManager',
            self.synopses_jar_loc,
            self.id, 
            self.input_file,
            self.output_file,
            self.noise_file,
            self.not_file,
            syn_prints_noise # 'true' or 'false': whether to print noiseless or noisy messages. Noisy messages are fewer => runs faster
        ]

        if not os.path.exists(self.synopses_jar_loc):
            raise FileNotFoundError(f'Synopses jar file does not exist in {self.synopses_jar_loc}. Run make.py in that folder')

        # Location where input data are stored
        self.data_folder = join(self.home, 'datacron/implementation/data/{}/'.format(dataset))

        if not isinstance(file_names, list):
            file_names = [file_names]

        if not one_file:
            # Place correct input file with desired time-length and ship-type
            self.place_input(ship_type, parts, file_names=file_names)
        else:
            self.place_input2(ship_type)

    def place_input(self, ship_type: str, parts: List[str], file_names: List[str]):
        """Creates a concatenate input file, from where the synopses will be created.

        Arguments:
           ship_type {str} -- The nmber that indicates the type of ship
           parts {List[str]} -- A list that contains all the parts to use.
           file_names {List[str]} -- A list of the file names to use e.g. month, march, etc. See `../../data`.
        """

        # Copy file from ../../data/
        with open(self.input_file, 'w') as w: # open target file
            for file_name in file_names:
                for p in parts:

                    # For each combination of part and file_name
                    src = join(self.data_folder, f'data_per_type/cross/type{ship_type}/{file_name}{p}.csv')
                    # Copy the lines to the target file
                    for line in open(src, 'r'):
                        if len(line) > 2:
                            w.write(line)

        self.save_input_file_to_dict()


    def place_input2(self, ship_type: str):
        """Creates an input file, from where the Synopses-Generator will read the input.
        Copies from only one file, `../../data/{dataset}/data_per_type/all/type_x.csv`.

        Arguments:
           ship_type {str} -- The nmber that indicates the type of ship
        """

        # Copy file from data/
        with open(self.input_file, 'w') as w:
            src = join(self.data_folder, 'data_per_type/all/type_{}.csv'.format(ship_type))
            for line in open(src, 'r'):
                if len(line) > 2:
                    w.write(line)

        self.save_input_file_to_dict()


    def save_input_file_to_dict(self):
        """Reads self.input_file and saves it to a dictionary.

        Raises:
            RuntimeError: In case self.input_file is empty.
        """        

        # Dictionary that contains points
        # The key is an string, the id of the ship
        # The value is a list of tuples: (lon,lat,t)
        self.in_data = {} # pylint: disable=attribute-defined-outside-init

        for x in open(self.input_file, 'r'):
            words = x.split(' ') # File is a space separated .csv file
            idd = words[1] # ID might not be an int
            lon = float(words[2])
            lat = float(words[3])
            t = int(words[0])

            # If id not in data initialize with empty list
            if idd not in self.in_data:
                self.in_data[idd] = []

            # Append to list: (lon, lat, t)
            self.in_data[idd].append((lon, lat, t))

        if len(self.in_data) == 0:
            raise RuntimeError("Couldn't Read Raw Data")


    def make_config(self, params: Dict[str, int]):
        """Function that creates the config file that will contain the paramaters
        """

        # Copy template file to location from where Synopses-Generator reads the params
        shutil.copyfile(self.template_file_loc, self.param_file_loc)

        with open(self.param_file_loc, 'a') as f:  # Append new params to template
            for k, v in params.items():
                f.write('val_' + k)  # Append param name
                f.write('=')
                f.write(str(v))  # Append param value
                f.write('\n')


    def read_synopses_files(self) -> Tuple[Dict, Dict]:
        """Func that reads and merges the output of the synopses

        Returns:
            Tuple -- A 2-tuple containing the output data and the noisy points.
                     If the output was not read, returns None
        """

        # Similar to self.in_data:
        # Dict of ID to list,
        # where list contains tuples: (lon,lat,t)
        out_data = {}

        # wrong=True if not read anything
        wrong = True

        # For each point in critical points
        for point in open(self.output_file, 'r'):
            if len(point) > 1:
                wrong = False
                # Translate json and get id
                t = json.loads(point)
                idd = t['id']

                # Create list for that id
                if idd not in out_data:
                    out_data[idd] = []

                # Append point info to list, as a tuple
                out_data[idd].append((
                    t['longitude'],
                    t['latitude'],
                    t['timestamp']
                ))

        if wrong:
            return None

        if os.path.exists(self.not_file):
            # For each point in notifications (gap_start points)
            for point in open(self.not_file, 'r'):
                if len(point) > 1:
                    # Translate json and get id
                    t = json.loads(point)
                    idd = t['id']

                    # If id not in dict create listy
                    if idd not in out_data:
                        out_data[idd] = []

                    # Append point info to list, as a tuple
                    out_data[idd].append((
                        t['longitude'],
                        t['latitude'],
                        t['timestamp']
                    ))

        # Initialize noisy points
        # Variable 'noise' is a dictionry, where the key is a ship-id(string) and the value is another dictionary,
        # whose key is a tuple (lon,lat,t) and value is an integer that counts how many times that specific point has been classified as noise
        noise = {}

        if os.path.exists(self.noise_file):
            # For each point in noisy points
            for point in open(self.noise_file, 'r'):
                if len(point) <= 1:
                    continue

                # Translate json and get id
                t = json.loads(point)
                idd = t['id']
                k = (t['longitude'], t['latitude'], t['timestamp'])

                if idd not in noise:
                    noise[idd] = {}

                if k not in noise[idd]:
                    # Initialize counter for that spesific point to 1
                    noise[idd][k] = 1
                else:
                    # Increment counter for that spesific point to 1
                    noise[idd][k] += 1

        return (out_data, noise)

    def run_synopses_and_copy_files(self, params: Dict[str, float], out_target: str, noise_target: str):
        """Method that reads and merges the output of the synopses. Then writes them to files.

        Args:
            params (Dict[str, float]): Dictionary that maps synopses params to their values
            out_target (str): File location to store ALL critical points
            noise_target (str): File location to store noiseless (or noisy) points.
        """

        # Write params to file
        self.make_config(params)

        # Run Synopses-Generator and wit for finish
        app = Popen(self.start_app, stdout=PIPE, stderr=PIPE)
        app.wait()

        # Dict that maps id to list,
        # Said list contains all the jsons, which is the output of the Synopses-Generator
        out_data = {}

        # For each point in critical points
        for point in open(self.output_file, 'r'):
            if len(point) > 1:
                wrong = False
                # Translate json and get id
                t = json.loads(point)
                idd = t['id']

                if idd not in out_data:
                    out_data[idd] = []

                # Append point
                out_data[idd].append(t)

        if wrong:
            raise RuntimeError('Not run correctly')

        if os.path.exists(self.not_file):
            # For each point in notifications (gap_start points)
            for point in open(self.not_file, 'r'):
                if len(point) > 1:
                    # Translate json and get id
                    t = json.loads(point)
                    idd = t['id']

                    # If id not in set with raw points raise error
                    if idd not in out_data:
                        out_data[idd] = []

                    # Append point info to second list, as a tuple
                    out_data[idd].append(t)

        # Write output to file
        with open(out_target, 'w') as f:
            for dics in out_data.values():
                for dic in dics:
                    f.write(str(json.dumps(dic)))
                    f.write('\n')

        # Copy noiseless file
        copyfile(self.noise_file, noise_target)


    def run_synopses_and_read_result(self, params: Dict[str, float], retries: int = 0, delete: bool = True) -> Tuple[Dict[str, List[Tuple]], Dict[str, List[Tuple]], Dict[str, Dict[Tuple, int]]]:
        """Runs the synopses for a given set of parameters.
        Returns the uncompressed points, the compressed points, and the noisy points

        Arguments:
           params {Dict[str, float]} -- A mapping from the name of the parameter to its value.
           retries {int} -- A counter which counts how many failures have happened.
           delete {bool} -- A flag that indicates whether to delete files after reading them.

        Raises:
            RuntimeError: When output has not been produced for 3 consecutive times.

        Returns:
            Dict[str, List[Tuple[float, float, int]]] -- Uncompressed points. A dictionary that maps the ship-id to a list of points
            Dict[str, List[Tuple[float, float, int]]] -- Compressed points. A dictionary that maps the ship-id to a list of points
            Dict[str, Dict[Tuple[float, float, int], int]] -- Noise points. A dictionary that mpas ship-id to another dictionary.
                This ones maps a point (lon,lat,t) to how many times its has been reported as noisy.
        """

        # Write params to file
        self.make_config(params)

        # Run Synopses-Generator and wit for finish
        app = Popen(self.start_app, stdout=PIPE, stderr=PIPE)
        app.wait()

        # Read result: 2 dicts, one with the crit-points, one with the noisy ones
        res = self.read_synopses_files()

        if res is not None:

            # Clean files
            if delete:
                os.remove(self.output_file)
                if os.path.exists(self.noise_file):
                    os.remove(self.noise_file)
                if os.path.exists(self.not_file):
                    os.remove(self.not_file)

            # Return in_data, out_data, noisy_points
            return self.in_data, res[0], res[1]

        if retries < 2:
            return self.run_synopses_and_read_result(params, retries+1)

        raise RuntimeError('Couldn\'t Read Output Data')

    def run_synopses(self, params: Dict[str, float], retries: int = 0) -> Tuple[float, float]:
        """Runs the synopses for a given set of parameters.
        Returns the RMSE and Compression Ratio.

        Arguments:
            params {Dict[str, float]} -- A mapping from the name of the parameter to its value.
            retries {int} -- An integer that counts how many times a synopses has gone wrong (default: {0})

        Returns:
            Tuple[float, float] -- (RMSE, Compr.Ratio)
        """

        # Run Synopses-Generator and read the output
        _, out_data, noise = self.run_synopses_and_read_result(params, retries)

        # Calculate RMSE and Comprasion Ratio
        rmse, comp_ratio = estimate_RMSE(self.in_data, out_data, deepcopy(noise))

        return rmse, comp_ratio


    def end(self):
        """Removes id from ids file
        Removes input file and parameter files
        """

        with open(self.ids_file, 'r') as f:
            taken = set(f.read().split())
            taken.remove(self.id)

        with open(self.ids_file, 'w') as f:
            for i in taken:
                f.write(i + ' ')

        # Delete csv and parameter files that were created during runs
        try:
            os.remove(self.input_file)
        except FileNotFoundError:
            pass

        try:
            os.remove(self.param_file_loc)
        except FileNotFoundError:
            pass
