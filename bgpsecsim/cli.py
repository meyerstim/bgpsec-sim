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
def figure2a(as_rel_file):
    nx_graph = as_graph.parse_as_rel_file(as_rel_file)

    graph = ASGraph(nx_graph)
    print("Loaded graph")

    origin_id = random.choice(list(graph.asyss.keys()))
    origin = graph.get_asys(origin_id)

    print(f"Finding routes to AS {origin_id}")
    graph.find_routes_to(origin)

    path_lengths = {}
    for asys in graph.asyss.values():
        if origin_id not in asys.routing_table:
            print(f"AS {asys.as_id} has no path to {origin_id}")
            continue
        path_len = asys.routing_table[origin.as_id].length
        if path_len not in path_lengths:
            path_lengths[path_len] = 0
        path_lengths[path_len] += 1
    for path_len, count in sorted(path_lengths.items()):
        print(f"path_length: {path_len}, count: {count}")

@cli.command()
def hello():
    click.echo('Hello world')

if __name__ == '__main__':
    cli()
