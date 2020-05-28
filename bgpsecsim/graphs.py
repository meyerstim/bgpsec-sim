from fractions import Fraction
import itertools
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random
import statistics
from typing import List, Sequence, Tuple

from bgpsecsim.asys import AS_ID
from bgpsecsim.as_graph import ASGraph
import bgpsecsim.experiments as experiments

def figure2a(filename: str, nx_graph: nx.Graph, n_trials: int):
    as_ids: List[AS_ID] = list(nx_graph.nodes)
    trials = [random_pair(as_ids) for _ in range(n_trials)]
    return figure2(filename, nx_graph, trials)

def figure2b(filename: str, nx_graph: nx.Graph, n_trials: int):
    """
    This one is a little weird. The paper says "We evaluated, for each victim content provider, the
    success rate of an attacker drawn uniformly at random." But the graph has only one line, so we
    assume the success rate is averaged over them.
    """

    # This list was from 2013. Major content providers have likely changed.
    # TODO: Get updated list.
    content_providers = [
        15169, # Google
        22822, # Limelight
        20940, # Akamai
        8075,  # Microsoft
        10310, # Yahoo
        16265, # Leaseweb
        15133, # Edgecast
        16509, # Amazon
        32934, # Facebook
        2906,  # Netflix
        4837,  # QQ
        13414, # Twitter
        40428, # Pandora
        14907, # Wikipedia
        714,   # Apple
        23286, # Hulu
        38365, # Baidu
    ]

    content_providers_set = set(content_providers)
    asyss_set = set(nx_graph.nodes)
    assert content_providers_set <= asyss_set

    as_ids: List[AS_ID] = list(asyss_set - content_providers_set)
    attackers = random.choices(as_ids, k=n_trials // len(content_providers))
    trials = list(itertools.product(content_providers, attackers))
    return figure2(filename, nx_graph, trials)

def figure2(filename: str, nx_graph: nx.Graph, trials: List[Tuple[AS_ID, AS_ID]]):
    deployments = np.arange(0, 110, 10)

    line1_results = []
    for deployment in deployments:
        print(f"Next-AS (deployment = {deployment})", deployment)
        line1_results.append(fmean(experiments.figure2a_line_1_next_as(nx_graph, deployment, trials)))
    print("Next-AS: ", line1_results)

    line2_results = []
    for deployment in deployments:
        print(f"BGPsec in partial deployment (deployment = {deployment})")
        line2_results.append(fmean(experiments.figure2a_line_2_bgpsec_partial(nx_graph, deployment, trials)))
    print("BGPsec in partial deployment: ", line2_results)

    line3_results = fmean(experiments.figure2a_line_3_two_hop(nx_graph, trials))
    print("2-hop: ", line3_results)

    line4_results = fmean(experiments.figure2a_line_4_rpki(nx_graph, trials))
    print("RPKI (full deployment): ", line4_results)

    line5_results = fmean(experiments.figure2a_line_5_bgpsec_med_full(nx_graph, trials))
    print("BGPsec (full deployment, legacy allowed): ", line5_results)

    plt.figure(figsize=(10, 5))
    plt.plot(deployment, line1_results, label="Next-AS")
    plt.plot(deployment, line2_results, label="BGPsec in partial deployment")
    plt.plot(deployment, np.repeat(line3_results, 11), label="2-hop")
    plt.plot(deployment, np.repeat(line4_results, 11), label="RPKI (full deployment)", linestyle="--")
    plt.plot(deployment, np.repeat(line5_results, 11), label="BGPsec (full deployment, legacy allowed)", linestyle="--")
    plt.legend()
    plt.xlabel("Deployment (top ISPs)")
    plt.ylabel("Attacker's Success Rate")
    plt.savefig(filename)

def fmean(vals: Sequence[Fraction]) -> float:
    return float(statistics.mean(vals))

def random_pair(as_ids: List[AS_ID]) -> Tuple[AS_ID, AS_ID]:
    [asn1, asn2] = random.choices(as_ids, k=2)
    return (asn1, asn2)
