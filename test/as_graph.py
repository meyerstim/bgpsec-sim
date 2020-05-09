import unittest
import os

import bgpsecsim.as_graph as as_graph

AS_REL_FILEPATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'as-rel.txt')

class TestASGraph(unittest.TestCase):

    def test_parse_as_rel_file(self):
        graph = as_graph.parse_as_rel_file(AS_REL_FILEPATH)
        for i in range(1, 14):
            assert i in graph.nodes, i
        assert graph.edges[(1, 2)]['customer'] == 2
        assert graph.edges[(2, 6)]['customer'] == 6
        assert graph.edges[(2, 3)]['customer'] is None
