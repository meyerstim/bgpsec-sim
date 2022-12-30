import click
import networkx as nx
import random

import bgpsecsim.as_graph as as_graph
import bgpsecsim.experiments as experiments
import bgpsecsim.graphs as graphs
import bgpsecsim.routing_policy as routing_policy
from bgpsecsim.as_graph import ASGraph
import other.evaluation as eval

@click.group()
def cli():
    pass

@cli.command()
@click.argument('as-rel-file')
def check_graph(as_rel_file):
    nx_graph = as_graph.parse_as_rel_file(as_rel_file)

    if not nx.is_connected(nx_graph):
        print("Graph is not fully connected!")
    else:
        print("Graph is fully connected")

    graph = ASGraph(nx_graph)
    print("Checking for customer-provider cycles")
    if graph.any_customer_provider_cycles():
        print("Graph has a customer-provider cycle!")
    else:
        print("Graph has no cycles")

@cli.command()
@click.argument('as-rel-file')
@click.argument('origin-asn', type=int)
@click.argument('final-asn', type=int)
def find_route(as_rel_file, origin_asn, final_asn):
    nx_graph = as_graph.parse_as_rel_file(as_rel_file)

    graph = ASGraph(nx_graph)
    print("Loaded graph")

    origin = graph.get_asys(origin_asn)
    final = graph.get_asys(final_asn)

    print(f"Finding routes to AS {origin_asn}")
    graph.find_routes_to(origin)

    print(final.routing_table.get(origin_asn, None))

@cli.command()
@click.argument('as-rel-file')
@click.argument('target-asn', type=int)
def get_path_lengths(as_rel_file, target_asn):
    nx_graph = as_graph.parse_as_rel_file(as_rel_file)

    graph = ASGraph(nx_graph, policy=routing_policy.RPKIPolicy())
    print("Loaded graph")

    origin_id = int(target_asn)
    origin = graph.get_asys(origin_id)

    print(f"Determining reachability to AS {origin_id}")
    reachable_from = graph.determine_reachability_one(origin_id)
    total_asyss = len(graph.asyss)
    print(f"AS {origin_id} is reachable from {reachable_from} / {total_asyss} ASs")

    print(f"Finding routes to AS {origin_id}")
    graph.find_routes_to(origin)

    path_lengths = {}
    for asys in graph.asyss.values():
        route = asys.get_route(origin.as_id)
        path_len = route.length if route else -1
        if path_len not in path_lengths:
            path_lengths[path_len] = 0
        path_lengths[path_len] += 1

    # Cross-check path routing results with reachability.
    assert path_lengths.get(-1, 0) + reachable_from == total_asyss

    for path_len, count in sorted(path_lengths.items()):
        print(f"path_length: {path_len}, count: {count}")

@cli.command()
@click.option('-s', '--seed', type=int)
@click.option('--trials', type=int, default=1)
@click.argument('figure')
@click.argument('as-rel-file')
@click.argument('output-file')
def generate(seed, trials, figure, as_rel_file, output_file):
    import sys
    sys.setrecursionlimit(100000)

    if seed is not None:
        random.seed(seed)

    nx_graph = as_graph.parse_as_rel_file(as_rel_file)
    print(as_rel_file)
    print("Loaded graph")

    func = getattr(graphs, figure)
    func(output_file, nx_graph, trials)


@cli.command()
@click.argument('input-file')
@click.argument('output-file')
@click.option('--threshold', '-t', type=float, default=0.005)
def evaluate(input_file, output_file, threshold):
    eval.evaluate(input_file, output_file, threshold)

if __name__ == '__main__':
    cli()
