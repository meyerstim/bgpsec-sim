from collections import deque

import bgpsecsim.error as error
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
    asyss: List[AS]

    def __init__(self):
        pass

    def identify_top_isps(self, n: int) -> List[AS]:
        pass

    def check_for_customer_provider_cycles(self) -> AS:
        # Run Floyd-Warshall
        pass

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
