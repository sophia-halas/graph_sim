"""
Author:        Sophia Halasova
File:          isomorphism.py

This module defines the function `find_isomorphisms`, which determines
whether there exists an isomorphism between two graphs of type `Graph`.
It checks all permutations of vertex mappings and validates adjacency 
preservation.
This code is part of a bachelor thesis focused on fuzzy graph similarity
by Sophia Halasova at BUT FIT in 2025.
"""

from itertools import permutations
from collections import defaultdict
from backend.TWBackend import Graph, Vertex
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

def convert_to_networkx(my_graph):
    """
    Converts a Graph object to a networkx.Graph.
    """
    G = nx.Graph()
    for vertex in my_graph.vertices.values():
        for neighbor_name, _ in vertex.neighbors:
            G.add_edge(vertex.name, neighbor_name)
    return G

def find_isomorphisms(G1, G2):
    """
    Finds all isomorphisms between two graphs by considering their vertices and edges.

    This function checks if there exists a valid mapping between the vertices of two graphs such that
    the structure of the graphs (adjacency relations) is preserved.

    :param G1: First graph (Graph object)
    :param G2: Second graph (Graph object)
    :return: A tuple containing:
             - A boolean indicating if any isomorphism exists
             - A list of mappings where each mapping is a dictionary that 
               maps vertices from G1 to corresponding vertices in G2.
    """
    nx_g1 = convert_to_networkx(G1)
    nx_g2 = convert_to_networkx(G2)

    matcher = GraphMatcher(nx_g1, nx_g2)
    all_mappings = list(matcher.isomorphisms_iter())

    return len(all_mappings) > 0, all_mappings

