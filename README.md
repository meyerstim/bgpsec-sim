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


## Other
To use parallelization of the simulator change value for "PARALLELISM" in experiments.py to desired value






