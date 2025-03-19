from itertools import permutations
from collections import defaultdict
from backend.tw_be import Graph, Vertex
import itertools
import numpy as np
import networkx as nx

def find_isomorphisms(G1, G2):
    """
    Finds all isomorphisms regardless the node/edge weights
    
    :param G1: First graph
    :param G2: Second graph
    :return: (bool, list of mappings)
    """
    if len(G1.vertices) != len(G2.vertices):
        return False, []  # must have same vertices count

    # all possible vertices mappings
    vertex_names_G1 = list(G1.vertices.keys())
    vertex_names_G2 = list(G2.vertices.keys())
    all_mappings = []

    for perm in itertools.permutations(vertex_names_G2):
        mapping = {vertex_names_G1[i]: perm[i] for i in range(len(perm))}

        # check if the mapping corresponds with topology structure
        valid = True
        for v1 in G1.vertices.values():
            mapped_v1 = mapping[v1.name]
            for neighbor, _ in v1.neighbors:
                mapped_neighbor = mapping[neighbor]
                
                # check if the same edge exists in G2
                g2_v1 = G2.vertices[mapped_v1]
                found = any(n[0] == mapped_neighbor for n in g2_v1.neighbors)

                if not found:
                    valid = False
                    break
            
            if not valid:
                break
        
        if valid:
            all_mappings.append(mapping)

    return len(all_mappings) > 0, all_mappings


# G1 = Graph()
# G1.add_vertex(Vertex("A", 0.8))
# G1.add_vertex(Vertex("B", 0.6))
# G1.add_vertex(Vertex("C", 0.9))
# G1.add_edge("A", "B", (1, 0))
# G1.add_edge("B", "C", (0, 1))

# G2 = Graph()
# G2.add_vertex(Vertex("X", 0.8))
# G2.add_vertex(Vertex("Y", 0.6))
# G2.add_vertex(Vertex("Z", 0.9))
# G2.add_edge("X", "Y", (1, 0))
# G2.add_edge("Y", "Z", (0, 1))

# print("Are graphs isomorphic?", find_isomorphisms(G1, G2))
