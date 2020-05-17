import unittest
import sys
import os

import as_graph
from asys import Relation
from as_graph import ASGraph

AS_REL_FILEPATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'as-rel.txt')

class TestASGraph(unittest.TestCase):

    def test_parse_as_rel_file(self):
        graph = bgpsecsim.as_graph.parse_as_rel_file(AS_REL_FILEPATH)
        for i in range(1, 14):
            assert i in graph.nodes
        assert graph.edges[(1, 2)]['customer'] == 2
        assert graph.edges[(2, 6)]['customer'] == 6
        assert graph.edges[(2, 3)]['customer'] is None

    def test_ASGraph_constructor(self):
        graph = ASGraph(as_graph.parse_as_rel_file(AS_REL_FILEPATH))
        for i in range(1, 14):
            assert i in graph.asyss
        assert graph.get_asys(1).get_relation(graph.get_asys(2)) == Relation.CUSTOMER
        assert graph.get_asys(2).get_relation(graph.get_asys(1)) == Relation.PROVIDER
        assert graph.get_asys(2).get_relation(graph.get_asys(6)) == Relation.CUSTOMER
        assert graph.get_asys(6).get_relation(graph.get_asys(2)) == Relation.PROVIDER
        assert graph.get_asys(2).get_relation(graph.get_asys(3)) == Relation.PEER
        assert graph.get_asys(3).get_relation(graph.get_asys(2)) == Relation.PEER

    def test_check_for_customer_provider_cycles(self):
        nx_graph = as_graph.parse_as_rel_file(AS_REL_FILEPATH)
        graph = ASGraph(nx_graph)
        self.assertFalse(graph.any_customer_provider_cycles())

        # Create a customer-provider cycle
        nx_graph.add_edge(1, 6, customer=1)
        graph = ASGraph(nx_graph)
        self.assertTrue(graph.any_customer_provider_cycles())

    def test_learn_routes(self):
        graph = ASGraph(as_graph.parse_as_rel_file(AS_REL_FILEPATH))
        asys_8 = graph.get_asys(8)
        for asys in graph.asyss.values():
            graph.find_routes_to(asys_8)

        for asys in graph.asyss.values():
            assert 8 in asys.routing_table
            route = asys.routing_table[8]
            assert route.final == asys

if __name__ == '__main__':
    unittest.main()
