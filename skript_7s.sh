#!/bin/bash
pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure7a caida-data/G_1664575200_1664661599.pickle outputs/7a_100
pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure7b caida-data/G_1664575200_1664661599.pickle outputs/7b_100
pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure7c caida-data/G_1664575200_1664661599.pickle outputs/7c_100
pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure7d caida-data/G_1664575200_1664661599.pickle outputs/7d_100

