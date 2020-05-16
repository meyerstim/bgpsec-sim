from collections import deque
from typing import Dict, List, Optional

import bgpsecsim.error as error
from bgpsecsim.asys import AS, AS_ID, Relation
import networkx as nx

def parse_as_rel_file(filename: str) -> nx.Graph:
    with open(filename, 'r') as f:
        graph = nx.Graph()

        for line in f:
            # Ignore lines starting with #
            if line.startswith('#'):
                continue

            # The 'serial-1' as-rel files contain p2p and p2c relationships. The format is:
            # <provider-as>|<customer-as>|-1
            # <peer-as>|<peer-as>|0
            items = line.split('|')
            if len(items) != 3:
                raise error.InvalidASRelFile(filename, f"bad line: {line}")

            [as1, as2, rel] = map(int, items)
            if as1 not in graph:
                graph.add_node(as1)
            if as2 not in graph:
                graph.add_node(as2)

            customer = as2 if rel == -1 else None
            graph.add_edge(as1, as2, customer=customer)

    return graph

class ASGraph(object):
    __slots__ = ['asyss', 'graph']

    asyss: Dict[AS_ID, AS]

    def __init__(self, graph: nx.Graph):
        self.asyss = {}
        for as_id in graph.nodes:
            self.asyss[as_id] = AS(as_id)
        for (as_id1, as_id2) in graph.edges:
            as1 = self.asyss[as_id1]
            as2 = self.asyss[as_id2]
            customer = graph.edges[(as_id1, as_id2)]['customer']
            if customer is None:
                as1.add_peer(as2)
                as2.add_peer(as1)
            elif customer == as_id1:
                as1.add_provider(as2)
                as2.add_customer(as1)
            elif customer == as_id2:
                as1.add_customer(as2)
                as2.add_provider(as1)

    def identify_top_isps(self, n: int) -> List[AS]:
        pass

    def any_for_customer_provider_cycles(self) -> Optional[AS]:
        graph = nx.DiGraph()
        for asys in self.asyss.values():
            graph.add_node(asys.as_id)
        for asys in self.asyss.values():
            for neighbor, relation in asys.neighbors.items():
                if relation == Relation.CUSTOMER:
                    weight = -1
                elif relation == Relation.PEER:
                    weight = 0
                elif relation == Relation.PROVIDER:
                    weight = 1
                graph.add_edge(asys.as_id, neighbor.as_id, weight=weight)
        return nx.negative_edge_cycle(graph, weight)

    def clear_routing_tables(self):
        for asys in self.asyss:
            asys.clear_routing_table()

    def find_routes_to(self, target: AS):
        routes = dequeue()
        for neighbor in target.neighbors:
            routes.append(target.originate_route(neighbor))

        while routes:
            route = routes.popleft()
            asys = route.last_asys
            for neighbor in asys.learn_route(route):
                routes.append(asys.forward_route(route, neighbor))

    def hijack_n_hops(self, victim: AS, attacker: AS, n: int):
        pass
