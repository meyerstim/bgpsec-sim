import click
import networkx as nx
import random

import as_graph
from as_graph import ASGraph

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
def figure2a(as_rel_file, target_asn):
    nx_graph = as_graph.parse_as_rel_file(as_rel_file)

    graph = ASGraph(nx_graph)
    print("Loaded graph")

    # origin_id = random.choice(list(graph.asyss.keys()))
    origin_id = int(target_asn)
    origin = graph.get_asys(origin_id)

    # path = nx.shortest_path(nx_graph, 205970, origin_id)
    print(f"Determining reachability to AS {origin_id}")
    reachable_from = graph.determine_reachability_one(origin_id)
    total_asyss = len(graph.asyss)
    print(f"AS {origin_id} is reachable from {reachable_from} / {total_asyss} ASs")

    print(f"Finding routes to AS {origin_id}")
    graph.find_routes_to(origin)

    path_lengths = {}
    for asys in graph.asyss.values():
        if origin_id in asys.routing_table:
            path_len = asys.routing_table[origin.as_id].length
        else:
            # print(f"AS {asys.as_id} has no path to {origin_id}")
            path_len = -1
        if path_len not in path_lengths:
            path_lengths[path_len] = 0
        path_lengths[path_len] += 1

    # Cross-check path routing results with reachability.
    assert path_lengths.get(-1, 0) + reachable_from == total_asyss

    for path_len, count in sorted(path_lengths.items()):
        print(f"path_length: {path_len}, count: {count}")


@cli.command()
def hello():
    click.echo('Hello world')

if __name__ == '__main__':
    cli()
