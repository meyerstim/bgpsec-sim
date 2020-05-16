import unittest
import os

import bgpsecsim.as_graph as as_graph
from bgpsecsim.as_graph import ASGraph

AS_REL_FILEPATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'as-rel.txt')

class TestASGraph(unittest.TestCase):

    def test_parse_as_rel_file(self):
        graph = as_graph.parse_as_rel_file(AS_REL_FILEPATH)
        for i in range(1, 14):
            assert i in graph.nodes, i
        assert graph.edges[(1, 2)]['customer'] == 2
        assert graph.edges[(2, 6)]['customer'] == 6
        assert graph.edges[(2, 3)]['customer'] is None

    def test_check_for_customer_provider_cycles(self):
        nx_graph = as_graph.parse_as_rel_file(AS_REL_FILEPATH)
        graph = ASGraph(nx_graph)
        assert not graph.any_for_customer_provider_cycles()

        # Create a customer-provider cycle
        nx_graph.add_edge(1, 6, customer=1)
        graph = ASGraph(nx_graph)
        assert graph.any_for_customer_provider_cycles()
