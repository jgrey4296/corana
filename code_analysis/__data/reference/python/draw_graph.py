#!/usr/bin/env python3
import networkx as nx
import matplotlib.pyplot as plt
import pygraphviz as pgv

def draw_graph(graph):
    # Convert graph into edgelist for data
    # Draw graph
    # prog=[‘neato’|’dot’|’twopi’|’circo’|’fdp’|’nop’]
    if bool(graph):
        pgv_graph = nx.nx_agraph.to_agraph(graph)
        pgv_graph.layout(prog='dot')
        pgv_graph.draw(join('analysis',
                            "{}.png".format(split(splitext(filename)[0])[1])))


    return list(nx.generate_edgelist(graph, data=False))
