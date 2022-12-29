#!/bin/bash
pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure2a caida-data/G_1664575200_1664661599.pickle outputs/2a_100
pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure2b caida-data/G_1664575200_1664661599.pickle outputs/2b_100

pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure3a caida-data/G_1664575200_1664661599.pickle outputs/3a_100
pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure3b caida-data/G_1664575200_1664661599.pickle outputs/3b_100

pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure8a caida-data/G_1664575200_1664661599.pickle outputs/8a_100
pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure8b caida-data/G_1664575200_1664661599.pickle outputs/8b_100
pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure8c caida-data/G_1664575200_1664661599.pickle outputs/8c_100

pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure9a caida-data/G_1664575200_1664661599.pickle outputs/9a_100
pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure9b caida-data/G_1664575200_1664661599.pickle outputs/9b_100
pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure9b_update caida-data/G_1664575200_1664661599.pickle outputs/9b_update_100

pipenv run python -m bgpsecsim generate -s 37 --trials 100 figure4 caida-data/G_1664575200_1664661599.pickle outputs/4_100
