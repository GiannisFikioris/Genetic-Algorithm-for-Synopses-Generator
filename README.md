# Genetic Algorithm for Synopses Generator

## About

This is a free software made to optimize the [Trajectory Synopses Generator](https://github.com/DataStories-UniPi/Trajectory-Synopses-Generator) developed by Kostas Patroumpas (UPRC), as well as use the synopses generated for complex event recognition. It is written in Python 3 and uses a Genetic Algorithm to automatically "learn" the best parameters for a ship type in a dataset.



## Installation

This repository should be placed in folder `~/infore/datacron/`, i.e. one should run the following commands for installation:
```bash
cd ~
mkdir -p infore/
cd infore
git clone -v https://github.com/GiannisFikioris/Genetic-Algorithm-for-Synopses-Generator.git datacron
```

To run the genetic algorithm one needs Flink (see folder `implementation/synopses_generator` for installation instructions and version). Flink should also be installed in the directory `~/infore/`.

Finally, to perform complex event recognition, one should download and install [RTEC](https://github.com/aartikis/RTEC) - this can be installed in any folder.



## Usage

To learn how to run the system, see the ReadMe in folder `parameter_optimizer/scripts` where there are detailed instruction about what each scripts does and how to use it.



## Requirements

A version of [Python 3](https://docs.python.org/3/) >= 3.7 with [pip](https://pip.pypa.io/en/stable/installing/).




## Licence

This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions; See the [GNU Lesser General Public License v3 for more details](https://www.gnu.org/licenses/lgpl-3.0.html).



## Documentation

* Giannis Fikioris, Kostas Patroumpas, Alexander Artikis. [Optimizing Vessel Trajectory Compression](https://ieeexplore.ieee.org/document/9162228). MDM 2020
* Giannis Fikioris, Kostas Patroumpas, Alexander Artikis, Georgios Paliouras, Manolis Pitsikalis. [Fine-Tuned Compressed Representations of Vessel Trajectories](https://dl.acm.org/doi/10.1145/3340531.3412706). CIKM 2020