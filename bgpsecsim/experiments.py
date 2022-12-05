import abc
from fractions import Fraction
import multiprocessing as mp
import multiprocessing.synchronize as mpsync
import networkx as nx
import random
import signal
import warnings
from typing import List, Tuple

from bgpsecsim.asys import AS, AS_ID
from bgpsecsim.as_graph import ASGraph
from bgpsecsim.routing_policy import (
    DefaultPolicy, RPKIPolicy, PathEndValidationPolicy,
    BGPsecHighSecPolicy, BGPsecMedSecPolicy, BGPsecLowSecPolicy, ASPAPolicy
)

PARALLELISM = 1

def figure2a_line_1_next_as(
        nx_graph: nx.Graph,
        deployment: int,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=RPKIPolicy())
    for asys in graph.identify_top_isps(deployment):
        asys.policy = PathEndValidationPolicy()
    return figure2a_experiment(graph, trials, n_hops=1)

def figure2a_line_2_bgpsec_partial(
        nx_graph: nx.Graph,
        deployment: int,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=RPKIPolicy())
    for asys in graph.identify_top_isps(deployment):
        asys.policy = BGPsecMedSecPolicy()
    return figure2a_experiment(graph, trials, n_hops=1)

def figure2a_line_3_two_hop(
        nx_graph: nx.Graph,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=PathEndValidationPolicy())
    return figure2a_experiment(graph, trials, n_hops=2)

def figure2a_line_4_rpki(
        nx_graph: nx.Graph,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=RPKIPolicy())
    return figure2a_experiment(graph, trials, n_hops=1)

def figure2a_line_5_bgpsec_low_full(
        nx_graph: nx.Graph,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=BGPsecLowSecPolicy())
    for asys in graph.asyss.values():
        asys.bgp_sec_enabled = True
    return figure2a_experiment(graph, trials, n_hops=1)

def figure2a_line_5_bgpsec_med_full(
        nx_graph: nx.Graph,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=BGPsecMedSecPolicy())
    for asys in graph.asyss.values():
        asys.bgp_sec_enabled = True
    return figure2a_experiment(graph, trials, n_hops=1)

def figure2a_line_5_bgpsec_high_full(
        nx_graph: nx.Graph,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=BGPsecHighSecPolicy())
    for asys in graph.asyss.values():
        asys.bgp_sec_enabled = True
    return figure2a_experiment(graph, trials, n_hops=1)

def figure2a_line_6_aspa_partial(
        nx_graph: nx.Graph,
        deployment: int,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=RPKIPolicy())
    for asys in graph.identify_top_isps(deployment):
        asys.policy = ASPAPolicy()
    return figure2a_experiment(graph, trials, n_hops=1)
def figure2a_line_6_aspa(
        nx_graph: nx.Graph,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=ASPAPolicy())
    for asys in graph.asyss.values():
        asys.aspa_enabled = True
    return figure2a_experiment(graph, trials, n_hops=1)

def figure2a_line_7_none(
        nx_graph: nx.Graph,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=DefaultPolicy())
    return figure2a_experiment(graph, trials, n_hops=1)

def run_trial(graph, victim_id, attacker_id, n_hops):
    victim = graph.get_asys(victim_id)
    if victim is None:
        raise ValueError(f"No AS with ID {victim_id}")
    attacker = graph.get_asys(attacker_id)
    if attacker is None:
        raise ValueError(f"No AS with ID {attacker_id}")

    graph.find_routes_to(victim)
    graph.hijack_n_hops(victim, attacker, n_hops)

    result = attacker_success_rate(graph, attacker, victim)

    # Avoid using unnecesary memory
    graph.clear_routing_tables()

    return result

def figure2a_experiment(
        graph: ASGraph,
        trials: List[Tuple[AS_ID, AS_ID]],
        n_hops: int
) -> List[Fraction]:
    trial_queue: mp.Queue = mp.Queue()
    result_queue: mp.Queue = mp.Queue()
    workers = [Figure2aExperiment(trial_queue, result_queue, graph, n_hops)
               for _ in range(PARALLELISM)]

    for worker in workers:
        worker.start()

    for trial in trials:
        trial_queue.put(trial)

    results = []
    for _ in range(len(trials)):
        result = result_queue.get()
        results.append(result)

    for worker in workers:
        worker.stop()
    for worker in workers:
        trial_queue.put(None)
    for worker in workers:
        worker.join()

    return results

def figure4_k_hop(nx_graph: nx.Graph, trials: List[Tuple[AS_ID, AS_ID]], n_hops: int) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=DefaultPolicy())
    return figure2a_experiment(graph, trials, n_hops)

def figure7a(
        nx_graph: nx.Graph,
        deployment: int,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=RPKIPolicy())
    for asys in graph.identify_top_isps(deployment):
        asys.policy = PathEndValidationPolicy()
    return figure2a_experiment(graph, trials, n_hops=1)

def figure7b(
        nx_graph: nx.Graph,
        deployment: int,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=RPKIPolicy())
    for asys in graph.identify_top_isps(deployment):
        asys.policy = BGPsecMedSecPolicy()
    return figure2a_experiment(graph, trials, n_hops=1)

def figure8_line_1_next_as(
        nx_graph: nx.Graph,
        deployment: int,
        p: float,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    results = []
    for _ in range(20):
        graph = ASGraph(nx_graph, policy=RPKIPolicy())
        for asys in graph.identify_top_isps(int(deployment / p)):
            if random.random() < p:
                asys.policy = PathEndValidationPolicy()
        results.extend(figure2a_experiment(graph, trials, n_hops=1))
    return results

def figure8_line_2_bgpsec_partial(
        nx_graph: nx.Graph,
        deployment: int,
        p: float,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    results = []
    for _ in range(20):
        graph = ASGraph(nx_graph, policy=RPKIPolicy())
        for asys in graph.identify_top_isps(int(deployment / p)):
            if random.random() < p:
                asys.policy = BGPsecMedSecPolicy()
        results.extend(figure2a_experiment(graph, trials, n_hops=1))
    return results

def figure8_line_3_aspa_partial(
        nx_graph: nx.Graph,
        deployment: int,
        p: float,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    results = []
    for _ in range(20):
        graph = ASGraph(nx_graph, policy=RPKIPolicy())
        for asys in graph.identify_top_isps(int(deployment / p)):
            if random.random() < p:
                asys.policy = ASPAPolicy()
        results.extend(figure2a_experiment(graph, trials, n_hops=1))
    return results

def figure9_line_1_rpki_partial(
        nx_graph: nx.Graph,
        deployment: int,
        trials: List[Tuple[AS_ID, AS_ID]]
) -> List[Fraction]:
    graph = ASGraph(nx_graph, policy=DefaultPolicy())
    for asys in graph.identify_top_isps(deployment):
        asys.policy = RPKIPolicy()
    return figure2a_experiment(graph, trials, n_hops=0)

#Result is a fraction, shows the ratio of successfull attacks to not attacked routes
def attacker_success_rate(graph: ASGraph, attacker: AS, victim: AS) -> Fraction:
    n_bad_routes = 0
    n_total_routes = 0
    for asys in graph.asyss.values():
        route = asys.get_route(victim.as_id)
        if route:
            n_total_routes += 1
            if attacker in route.path:
                n_bad_routes += 1
    #Fraction creates a "Bruch" with the first value as numerator and the second as denominator
    return Fraction(n_bad_routes, n_total_routes)

class Experiment(mp.Process, abc.ABC):
    input_queue: mp.Queue
    output_queue: mp.Queue
    _stopped: mpsync.Event

    def __init__(self, input_queue: mp.Queue, output_queue: mp.Queue):
        super().__init__(daemon=True)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self._stopped = mp.Event()

    def stop(self):
        self._stopped.set()

    def run(self):
        signal.signal(signal.SIGINT, lambda _signo, _frame: self.stop())

        while not self._stopped.is_set():
            trial = self.input_queue.get()

            # A None input is just used to stop blocking on the queue, so we can check stopped.
            if trial is None:
                continue

            self.output_queue.put(self.run_trial(trial))

    #Creates an abstract class which has to be definded later on
    @abc.abstractmethod
    #raise is used to give own errors, in this case if anythin happens where now error was created for
    def run_trial(self, trial):
        raise NotImplementedError()

class Figure2aExperiment(Experiment):
    graph: ASGraph
    n_hops: int

    def __init__(self, input_queue: mp.Queue, output_queue: mp.Queue, graph: ASGraph, n_hops: int):
        super().__init__(input_queue, output_queue)
        self.graph = graph
        self.n_hops = n_hops

    def run_trial(self, trial: Tuple[(AS_ID, AS_ID)]):
        graph = self.graph
        n_hops = self.n_hops
        #Takes the value passed by the function call by "trial" and assigns them to victim and attacker
        victim_id, attacker_id = trial

        #Takes the desired AS as victim out of the full graph by its ID
        victim = graph.get_asys(victim_id)
        if victim is None:
            warnings.warn(f"No AS with ID {victim_id}")
            return Fraction(0, 1)

        #Takes AS of attacker out of graph, like did for the victim
        attacker = graph.get_asys(attacker_id)
        if attacker is None:
            warnings.warn(f"No AS with ID {attacker_id}")
            return Fraction(0, 1)
        
        #starts to find a new routing table and executes the attack onto it by n hops
        graph.clear_routing_tables()
        graph.find_routes_to(victim)
        graph.hijack_n_hops(victim, attacker, n_hops)
        
        result = attacker_success_rate(graph, attacker, victim)

        return result