from fractions import Fraction
import networkx as nx
import random
from typing import List, Tuple

from bgpsecsim.asys import AS, AS_ID
from bgpsecsim.as_graph import ASGraph
from bgpsecsim.routing_policy import RPKIPolicy, BGPsecHighSecPolicy, BGPsecLowSecPolicy

def attacker_success_rate(graph: ASGraph, attacker: AS, victim: AS) -> Fraction:
    n_bad_routes = 0
    n_total_routes = 0
    for asys in graph.asyss.values():
        route = asys.get_route(victim.as_id)
        if route:
            n_total_routes += 1
            if attacker in route.path:
                n_bad_routes += 1
    return Fraction(n_bad_routes, n_total_routes)

def figure2a_line_4_rpki(nx_graph: nx.Graph, trials: List[Tuple[AS_ID, AS_ID]]) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=RPKIPolicy())
    results = []
    for victim_id, attacker_id in trials:
        victim = graph.get_asys(victim_id)
        if victim is None:
            raise ValueError(f"No AS with ID {victim_id}")
        attacker = graph.get_asys(attacker_id)
        if attacker is None:
            raise ValueError(f"No AS with ID {attacker_id}")

        graph.find_routes_to(victim)
        graph.hijack_n_hops(victim, attacker, 1)
        results.append(attacker_success_rate(graph, attacker, victim))

        # Avoid using unnecesary memory
        graph.clear_routing_tables()
    return results

def figure2a_line_5_bgpsec(nx_graph: nx.Graph, trials: List[Tuple[AS_ID, AS_ID]]) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=BGPsecLowSecPolicy())
    for asys in graph.asyss.values():
        asys.bgp_sec_enabled = True

    results = []
    for victim_id, attacker_id in trials:
        victim = graph.get_asys(victim_id)
        if victim is None:
            raise ValueError(f"No AS with ID {victim_id}")
        attacker = graph.get_asys(attacker_id)
        if attacker is None:
            raise ValueError(f"No AS with ID {attacker_id}")

        attacker.bgp_sec_enabled = False
        graph.find_routes_to(victim)
        graph.hijack_n_hops(victim, attacker, 1)
        attacker.bgp_sec_enabled = True

        results.append(attacker_success_rate(graph, attacker, victim))

        # Avoid using unnecesary memory
        graph.clear_routing_tables()
    return results
