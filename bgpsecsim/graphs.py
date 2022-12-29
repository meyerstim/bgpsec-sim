from fractions import Fraction
import itertools
import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random
import statistics
from typing import List, Sequence, Tuple
from matplotlib import cm
from numpy import asarray
from numpy import savetxt

from bgpsecsim.asys import AS_ID
import bgpsecsim.as_graph as as_graph
from bgpsecsim.as_graph import ASGraph
import bgpsecsim.experiments as experiments
import other.evaluation as eval

def get_attacks():
    return [
        ("Syria Telecom attacks Youtube-1", "attacks/STE-1.txt", "caida-data/20141201.as-rel.txt"),
        ("Syria Telecom attacks Youtube-2", "attacks/STE-2.txt", "caida-data/20141201.as-rel.txt"),
        ("Indosat attacks various ASes", "attacks/Indosat.txt", "caida-data/20110101.as-rel.txt"),
        # Turk Telecom was in 3/2014, but 12/2013 is as close as CAIDA has, for some reason
        ("Turk Telecom attacks DNS servers", "attacks/Turk Telecom.txt", "caida-data/20131201.as-rel.txt"),
        ("Opin Kerfi attacks CenturyTel", "attacks/Opin Kerfi.txt", "caida-data/20130701.as-rel.txt")
    ]


def get_content_providers() -> List[AS_ID]:
    # This list was from 2013. Major content providers have likely changed.
    # TODO: Get updated list.
    return [
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

def get_current_content_providers() -> List[AS_ID]:
    return [
        20940, # Akamai
        16509, # Amazon
        714,   # Apple
        32934, # Facebook
        15169, # Google
        8075,  # Microsoft
        2906   # Netflix
    ]

def target_content_provider_trials(nx_graph: nx.Graph, n_trials: int, providers: List[AS_ID]) -> List[Tuple[AS_ID, AS_ID]]:
    content_providers_set = set(providers)
    asyss_set = set(nx_graph.nodes)
    assert content_providers_set <= asyss_set

    as_ids: List[AS_ID] = list(asyss_set - content_providers_set)
    attackers = random.choices(as_ids, k=math.ceil(n_trials / len(providers)))
    return list(itertools.product(providers, attackers))

def uniform_random_trials(nx_graph: nx.Graph, n_trials: int) -> List[Tuple[AS_ID, AS_ID]]:
    as_ids: List[AS_ID] = list(nx_graph.nodes)
    return [random_pair(as_ids) for _ in range(n_trials)]

def figure2a(filename: str, nx_graph: nx.Graph, n_trials: int):
    trials = uniform_random_trials(nx_graph, n_trials)
    return figure2(filename, nx_graph, trials)

def figure2b(filename: str, nx_graph: nx.Graph, n_trials: int):
    """
    This one is a little weird. The paper says "We evaluated, for each victim content provider, the
    success rate of an attacker drawn uniformly at random." But the graph has only one line, so we
    assume the success rate is averaged over them.
    """
    trials = target_content_provider_trials(nx_graph, n_trials, get_content_providers())
    return figure2(filename, nx_graph, trials)

def figure2(filename: str, nx_graph: nx.Graph, trials: List[Tuple[AS_ID, AS_ID]]):
    #Here the percentage of deployment is set, current from 0 to full deployment by top ISP, incrementing by 10% everytime
    deployments = np.arange(0, 110, 10)

    line1_results = []
    for deployment in deployments:
        print(f"Next-AS (deployment = {deployment})")
        line1_results.append(fmean(experiments.figure2a_line_1_next_as(nx_graph, deployment, trials)))
    print("Next-AS: ", line1_results)

    #line2_results = []
    #for deployment in deployments:
    #    print(f"BGPsec in partial deployment (deployment = {deployment})")
    #    line2_results.append(fmean(experiments.figure2a_line_2_bgpsec_partial(nx_graph, deployment, trials)))
    #print("BGPsec in partial deployment: ", line2_results)

    #line3_results = fmean(experiments.figure2a_line_3_two_hop(nx_graph, trials))
    #print("2-hop: ", line3_results)

    line4_results = fmean(experiments.figure2a_line_4_rpki(nx_graph, trials))
    print("RPKI (full deployment): ", line4_results)

    line5_results = fmean(experiments.figure2a_line_5_bgpsec_med_full(nx_graph, trials))
    print("BGPsec (full deployment, legacy allowed): ", line5_results)

    line6_results = []
    for deployment in deployments:
        print(f"ASPA in partial deployment (deployment = {deployment})")
        line6_results.append(fmean(experiments.figure2a_line_6_aspa_partial(nx_graph, deployment, trials)))
    print("ASPA in partial deployment: ", line6_results)

    line7_results = fmean(experiments.figure2a_line_7_aspa_optimal(nx_graph, trials))
    print("ASPA (50% deployment) ", line7_results)

    line8_results = fmean(experiments.figure2a_line_8_aspa_full(nx_graph, trials))
    print("ASPA (full deployment) ", line8_results)

    plt.figure(figsize=(10, 7))
    plt.plot(deployments, line1_results, label="Path-end-validation (partial deployment)")
    #plt.plot(deployments, line2_results, label="BGPsec (partial deployment)")
    #plt.plot(deployments, np.repeat(line3_results, 11), label="2-hop")
    plt.plot(deployments, np.repeat(line4_results, 11), label="RPKI (full deployment)", linestyle="--")
    plt.plot(deployments, np.repeat(line5_results, 11), label="BGPsec (full deployment, legacy allowed)", linestyle="--")
    plt.plot(deployments, line6_results, label="ASPA (partial deployment)")
    plt.plot(deployments, np.repeat(line7_results, 11), label="ASPA (50% deployment)", linestyle="--")
    plt.plot(deployments, np.repeat(line8_results, 11), label="ASPA (full deployment)", linestyle="--")
    plt.legend()
    plt.xlabel("Deployment at number of top ISPs, ranked by customer count")
    plt.ylabel("Attacker's Success Rate (in %)")
    plt.savefig(filename)


def figure3a(filename: str, nx_graph: nx.Graph, n_trials: int):
    large_asyss = list(as_graph.asyss_by_customer_count(nx_graph, 250, None))
    stub_asyss = list(as_graph.asyss_by_customer_count(nx_graph, 0, 0))
    trials = [(random.choice(stub_asyss), random.choice(large_asyss)) for _ in range(n_trials)]
    return figure2(filename, nx_graph, trials)


def figure3b(filename: str, nx_graph: nx.Graph, n_trials: int):
    large_asyss = list(as_graph.asyss_by_customer_count(nx_graph, 250, None))
    stub_asyss = list(as_graph.asyss_by_customer_count(nx_graph, 0, 0))
    trials = [(random.choice(large_asyss), random.choice(stub_asyss)) for _ in range(n_trials)]
    return figure2(filename, nx_graph, trials)

def figure4(filename: str, nx_graph: nx.Graph, n_trials: int):
    trials = uniform_random_trials(nx_graph, n_trials)

    hops = np.arange(0, 11)

    line1_results = []
    for n_hops in hops:
        print(f"k-hop attacker (k={n_hops})")
        line1_results.append(fmean(experiments.figure4_k_hop(nx_graph, trials, n_hops)))
    print("k-hop attacker: ", line1_results)

    line2_results = fmean(experiments.figure2a_line_5_bgpsec_med_full(nx_graph, trials))
    print("BGPsec (full deployment, legacy allowed): ", line2_results)

    line3_results = fmean(experiments.figure2a_line_8_aspa_full(nx_graph, trials))
    print("ASPA (full deployment) ", line3_results)

    line4_results = fmean(experiments.figure2a_line_7_aspa_optimal(nx_graph, trials))
    print("ASPA (50% deployment) ", line4_results)


    plt.figure(figsize=(10, 5))
    plt.plot(hops, line1_results, label="k-hop attacker")
    plt.plot(hops, np.repeat(line2_results, 11), label="BGPsec (full deployment, legacy allowed)", linestyle="--")
    plt.plot(hops, np.repeat(line4_results, 11), label="ASPA (50% deployment)", linestyle="--")
    plt.plot(hops, np.repeat(line3_results, 11), label="ASPA (full deployment)", linestyle="--")
    plt.legend()
    plt.xlabel("Hops")
    plt.ylabel("Attacker's Success Rate (in %)")
    plt.savefig(filename)


def figure7a(filename: str, nx_graph: nx.Graph, n_trials: int):
    results = []
    attacks = get_attacks()

    for (label, filepath, as_rel_file) in attacks:
        nx_graph = as_graph.parse_as_rel_file(as_rel_file)
        print("Loaded graph for ", label)

        with open(filepath) as f:
            attackers = None
            targets = []
            # Expects 1 attacker, n victims, comments beginning with #
            for l in f:
                if l[0] == '#':
                    continue
                if attackers == None:
                    attackers = [int(l)]
                    continue
                targets.append(int(l))

        trials = list(itertools.product(targets, attackers))

        deployments = np.arange(0, 110, 10)

        attack_results = []
        for deployment in deployments:
            attack_results.append(fmean(experiments.figure7a(nx_graph, deployment, trials)))
        results.append(attack_results)
        print(label, attack_results)

    plt.figure(figsize=(10, 5))
    for i in range(len(results)):
        plt.plot(deployments, results[i], label=attacks[i][0])
    plt.legend()
    plt.xlabel("Deployment (top ISPs)")
    plt.ylabel("Attacker's Success Rate (in %)")
    plt.savefig(filename)


def figure7b(filename: str, nx_graph: nx.Graph, n_trials: int):
    results = []
    attacks = get_attacks()

    for (label, filepath, as_rel_file) in attacks:
        nx_graph = as_graph.parse_as_rel_file(as_rel_file)
        print("Loaded graph for ", label)

        with open(filepath) as f:
            attackers = None
            targets = []
            # Expects 1 attacker, n victims, comments beginning with #
            for l in f:
                if l[0] == '#':
                    continue
                if attackers == None:
                    attackers = [int(l)]
                    continue
                targets.append(int(l))

        trials = list(itertools.product(targets, attackers))

        deployments = np.arange(0, 110, 10)

        attack_results = []
        for deployment in deployments:
            attack_results.append(fmean(experiments.figure7b(nx_graph, deployment, trials)))
        results.append(attack_results)
        print(label, attack_results)
        
    plt.figure(figsize=(10, 5))
    for i in range(len(results)):
        plt.plot(deployments, results[i], label=attacks[i][0])
    plt.legend()
    plt.xlabel("Deployment (top ISPs)")
    plt.ylabel("Attacker's Success Rate (in %)")
    plt.savefig(filename)


def figure7c(filename: str, nx_graph: nx.Graph, n_trials: int):
    results = []
    attacks = get_attacks()

    for (label, filepath, as_rel_file) in attacks:
        nx_graph = as_graph.parse_as_rel_file(as_rel_file)
        print("Loaded graph for ", label)

        with open(filepath) as f:
            attackers = None
            targets = []
            # Expects 1 attacker, n victims, comments beginning with #
            for l in f:
                if l[0] == '#':
                    continue
                if attackers == None:
                    attackers = [int(l)]
                    continue
                targets.append(int(l))

        trials = list(itertools.product(targets, attackers))

        deployments = np.arange(0, 110, 10)

        attack_results = []
        for deployment in deployments:
            attack_results.append(fmean(experiments.figure7c(nx_graph, deployment, trials)))
        results.append(attack_results)
        print(label, attack_results)

    plt.figure(figsize=(10, 5))
    for i in range(len(results)):
        plt.plot(deployments, results[i], label=attacks[i][0])
    plt.legend()
    plt.xlabel("Deployment (top ISPs)")
    plt.ylabel("Attacker's Success Rate (in %)")
    plt.savefig(filename)


def figure7d(filename: str, nx_graph: nx.Graph, n_trials: int):
    results = []
    attacks = get_attacks()

    for (label, filepath, as_rel_file) in attacks:
        nx_graph = as_graph.parse_as_rel_file(as_rel_file)
        print("Loaded graph for ", label)

        with open(filepath) as f:
            attackers = None
            targets = []
            # Expects 1 attacker, n victims, comments beginning with #
            for l in f:
                if l[0] == '#':
                    continue
                if attackers == None:
                    attackers = [int(l)]
                    continue
                targets.append(int(l))

        trials = list(itertools.product(targets, attackers))

        deployments = np.arange(0, 110, 10)

        attack_results = []
        for deployment in deployments:
            attack_results.append(fmean(experiments.figure7d(nx_graph, deployment, trials)))
        results.append(attack_results)
        print(label, attack_results)

    plt.figure(figsize=(10, 5))
    for i in range(len(results)):
        plt.plot(deployments, results[i], label=attacks[i][0])
    plt.legend()
    plt.xlabel("Deployment (top ISPs)")
    plt.ylabel("Attacker's Success Rate (in %)")
    plt.savefig(filename)


def figure8(filename: str, nx_graph: nx.Graph, n_trials: int, p: float):
    trials = uniform_random_trials(nx_graph, n_trials)
    deployments = np.arange(0, 110, 10)

    rand_state = random.getstate()

    line1_results = []
    for deployment in deployments:
        print(f"Next-AS (deployment = {deployment})")
        random.setstate(rand_state)
        line1_results.append(fmean(experiments.figure8_line_1_next_as(nx_graph, deployment, p, trials)))
    print("Next-AS: ", line1_results)

    line2_results = []
    for deployment in deployments:
        print(f"BGPsec in partial deployment (deployment = {deployment})")
        random.setstate(rand_state)
        line2_results.append(fmean(experiments.figure8_line_2_bgpsec_partial(nx_graph, deployment, p, trials)))
    print("BGPsec in partial deployment: ", line2_results)

    # line3_results = fmean(experiments.figure2a_line_3_two_hop(nx_graph, trials))
    # print("2-hop: ", line3_results)

    line4_results = fmean(experiments.figure2a_line_4_rpki(nx_graph, trials))
    print("RPKI (full deployment): ", line4_results)

    line5_results = fmean(experiments.figure2a_line_5_bgpsec_med_full(nx_graph, trials))
    print("BGPsec (full deployment, legacy allowed): ", line5_results)

    line6_results = []
    for deployment in deployments:
        print(f"ASPA in partial deployment (deployment = {deployment})")
        random.setstate(rand_state)
        line6_results.append(fmean(experiments.figure8_line_3_aspa_partial(nx_graph, deployment, p, trials)))
    print("ASPA in partial deployment: ", line6_results)

    line7_results = fmean(experiments.figure2a_line_7_aspa_optimal(nx_graph, trials))
    print("ASPA (50% deployment): ", line7_results)


    plt.figure(figsize=(10, 7))
    plt.plot(deployments, line1_results, label="Next-AS")
    plt.plot(deployments, line2_results, label="BGPsec in partial deployment")
    # plt.plot(deployments, np.repeat(line3_results, 11), label="2-hop")
    plt.plot(deployments, np.repeat(line4_results, 11), label="RPKI (full deployment)", linestyle="--")
    plt.plot(deployments, np.repeat(line5_results, 11), label="BGPsec (full deployment, legacy allowed)", linestyle="--")
    plt.plot(deployments, line6_results, label="ASPA in partial deployment")
    plt.plot(deployments, np.repeat(line7_results, 11), label="ASPA (50% deployment)", linestyle="--")
    plt.legend()
    plt.xlabel("Expected Deployment (top ISPs)")
    plt.ylabel("Attacker's Success Rate (in %)")
    plt.savefig(filename)

def figure8a(filename: str, nx_graph: nx.Graph, n_trials: int):
    figure8(filename, nx_graph, n_trials, p=0.75)

def figure8b(filename: str, nx_graph: nx.Graph, n_trials: int):
    figure8(filename, nx_graph, n_trials, p=0.50)

def figure8c(filename: str, nx_graph: nx.Graph, n_trials: int):
    figure8(filename, nx_graph, n_trials, p=0.25)

def figure9a(filename: str, nx_graph: nx.Graph, n_trials: int):
    trials = uniform_random_trials(nx_graph, n_trials)
    return figure9(filename, nx_graph, trials)

def figure9b(filename: str, nx_graph: nx.Graph, n_trials: int):
    trials = target_content_provider_trials(nx_graph, n_trials, get_content_providers())
    return figure9(filename, nx_graph, trials)
   
def figure9b_update(filename: str, nx_graph: nx.Graph, n_trials: int):
    trials = target_content_provider_trials(nx_graph, n_trials, get_current_content_providers())
    return figure9(filename, nx_graph, trials)

def figure9(filename: str, nx_graph: nx.Graph, trials: List[Tuple[AS_ID, AS_ID]]):
    deployments = np.arange(0, 110, 10)

    line1_results = []
    for deployment in deployments:
        print(f"Prefix hijack (deployment = {deployment})")
        line1_results.append(fmean(experiments.figure9_line_1_rpki_partial(nx_graph, deployment, trials)))
    print("Prefix hijack: ", line1_results)

    line2_results = fmean(experiments.figure2a_line_4_rpki(nx_graph, trials))
    print("RPKI (full deployment): ", line2_results)

    plt.figure(figsize=(10, 5))
    plt.plot(deployments, line1_results, label="Prefix hijack")
    plt.plot(deployments, np.repeat(line2_results, 11), label="RPKI (full deployment)", linestyle="--")
    plt.legend()
    plt.xlabel("Deployment (top ISPs)")
    plt.ylabel("Attacker's Success Rate (in %)")
    plt.savefig(filename)


def figure10(filename: str, nx_graph: nx.Graph, n_trials:int, tierOne:int):
    trials = uniform_random_trials(nx_graph, n_trials)

    # Set more detailed eval by setting steps smaller then 10
    deployments = np.arange(0, 110, 10)

    line1_results = []
    for deployment in deployments:
        print(f"ASPA Tier2 (deployment = {deployment})")
        line1_results.append(fmean(experiments.figure10_aspa(nx_graph, [deployment, 5], trials, tierOne)))
    line2_results = []
    for deployment in deployments:
        print(f"ASPA Tier2 (deployment = {deployment})")
        line2_results.append(fmean(experiments.figure10_aspa(nx_graph, [deployment, 10], trials, tierOne)))
    line3_results = []
    for deployment in deployments:
        print(f"ASPA Tier2 (deployment = {deployment})")
        line3_results.append(fmean(experiments.figure10_aspa(nx_graph, [deployment, 20], trials, tierOne)))
    line4_results = []
    for deployment in deployments:
        print(f"ASPA Tier2 (deployment = {deployment})")
        line4_results.append(fmean(experiments.figure10_aspa(nx_graph, [deployment, 30], trials, tierOne)))
    line5_results = []
    for deployment in deployments:
        print(f"ASPA Tier2 (deployment = {deployment})")
        line5_results.append(fmean(experiments.figure10_aspa(nx_graph, [deployment, 50], trials, tierOne)))
    line6_results = []
    for deployment in deployments:
        print(f"ASPA Tier2 (deployment = {deployment})")
        line6_results.append(fmean(experiments.figure10_aspa(nx_graph, [deployment, 80], trials, tierOne)))

    plt.figure(figsize=(10, 7))
    plt.plot(deployments, line1_results, label="Tier3: 5%")
    plt.plot(deployments, line2_results, label="Tier3: 10%")
    plt.plot(deployments, line3_results, label="Tier3: 20%")
    plt.plot(deployments, line4_results, label="Tier3: 30%")
    plt.plot(deployments, line5_results, label="Tier3: 50%")
    plt.plot(deployments, line6_results, label="Tier3: 80%")

    plt.legend()
    plt.xlabel("Deployment at percentage of Tier2 providers")
    plt.ylabel("Attacker's Success Rate (in %)")
    plt.savefig(filename)

def figure10_3d(filename: str, nx_graph: nx.Graph, n_trials:int):
    large_asyss = list(as_graph.asyss_by_customer_count(nx_graph, 250, None))
    stub_asyss = list(as_graph.asyss_by_customer_count(nx_graph, 0, 0))
    trials = [(random.choice(stub_asyss), random.choice(large_asyss)) for _ in range(n_trials)]

    deploymentsTierThree = np.arange(0, 101, 10)
    deploymentsTierTwo = np.arange(0, 101, 10)
    deploymentsTierOne = np.arange(0, 101, 10)

    line1_results = []
    for deployment in deploymentsTierThree:
        for deployment2 in deploymentsTierTwo:
            for deployment3 in deploymentsTierOne:
                print(f"ASPA deployment = {deployment3, deployment2, deployment})")
                line1_results.append(fmean(experiments.figure10_aspa(nx_graph, [deployment, deployment2], trials, deployment3)))
        data_between = np.asarray(line1_results)
        np.savetxt(filename+'_backup'+str(deployment)+'.csv', data_between, delimiter=',')


    data = np.asarray(line1_results)
    np.savetxt(filename+'.csv', data, delimiter=',')

    print(line1_results)

    #eval.evaluate(data, filename, 10)




def figure10_100(filename: str, nx_graph: nx.Graph, n_trials: int):
    figure10(filename, nx_graph, n_trials, 100)


def figure10_80(filename: str, nx_graph: nx.Graph, n_trials: int):
    figure10(filename, nx_graph, n_trials, 80)


def figure10_50(filename: str, nx_graph: nx.Graph, n_trials: int):
    figure10(filename, nx_graph, n_trials, 50)


def figure10_20(filename: str, nx_graph: nx.Graph, n_trials: int):
    figure10(filename, nx_graph, n_trials, 20)


def fmean(vals: Sequence[Fraction]) -> float:
    return float(statistics.mean(vals))


def random_pair(as_ids: List[AS_ID]) -> Tuple[AS_ID, AS_ID]:
    [asn1, asn2] = random.sample(as_ids, 2)
    return (asn1, asn2)
