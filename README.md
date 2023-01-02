# BGP Security Simulations

Reproduction of "Jumpstarting BGP Security with Path-End Validation".
In current version extended by ASPA (Autononous System Provider Authorization) Algorithm.

## Setup

- Install Python 3.8+
- Install pip3 
- Install [Pipenv](https://pipenv.pypa.io/en/latest/)
- Install required packages inside pipenv
  - click
  - networkx
  - matplotlib

For fast setup the attatched file "SetupSkript.bash" can be used to install all required applications and packages. Before execution customize the file with your personal parameters. In the file there are comments in the places that need to be adjusted.

Written and tested with Ubuntu 20.04.5 LTS

## Commands
Simulation environment is run by command line utility

Before first start the unittests can be ran to check for correct operation of the simulator:


Run the tests:

```bash
$ pipenv run python -m unittest
```

To run the simulation by command line utility use:

```bash
$ pipenv run python -m bgpsecsim
```

After execution of the command, the four possible command arguments will be shown according to the cli.py:
- check-graph
- evaluation
- find-route
- generate
- get-path-lengths


## Running

To run a simulation command according to last section has to be run with the argument "generate".

Several parameters have to be specified and passed along with the command:
- (seed; optional): Integer
- trials: Integer, number of runs
- figure: Name of figure which should be evaluated (e.g.: figure3a)
- input-File: AS_Rel File OR pickled Graph file which is used to create the required network-graph
- outputFile: Name and destination where the outputfile should be saved

Example command (runs figure3a with 100 trials)
```bash
$ pipenv run python -m bgpsecsim generate --trials 100 figure3a caida-data/20221101.as-rel.txt outputs/figure3a_100trials
```

## Evaluation

Command "evaluation" can be used to generate a 3-dimensional graphic representation for data gained by running figure_10 to analyse optimal ASPA deployment scenarios.
Data gets exported to .csv file, when "generate" function with the desired experiment was run. 
This file can now be used to create graphic output.

Value "threshold" can be used to get a more detailed version of the graphic. Represents a percentage off all values.
All data points which have an attacker-success rate worse then the given percentage, will be excluded from the graphic.
This results in a graph with fewer data points, which allows a finer view.

Several parameters have to be specified and passed along with the command:
- input-file: path to the file with the values received by running the figure_10 experiment
- output-file: path and desired name of the output graphic
- threshold: Integer, represents percentage

```bash
$ pipenv run python -m bgpsecsim evaluate results.csv graphic -threshold 0.005
```


## Other
To use parallelization of the simulator change value for "PARALLELISM" in experiments.py to desired value.

Simulation framework does NOT work on Windows Systems.

2-Hop Attacks were excluded from evaluation in graphs.py as they were not used in the current evaluation.
They can be added to the evaluation by removing the comment brackets.






