from itertools import permutations
from collections import defaultdict
from backend.tw_be import Graph, Vertex
import itertools
import numpy as np
import networkx as nx

def find_isomorphisms(G1, G2):
    """
    Finds all isomorphisms between two graphs by considering their vertices and edges.

    This function checks if there exists a valid mapping between the vertices of two graphs such that
    the structure of the graphs (i.e., adjacency relations) is preserved.

    :param G1: First graph (Graph object)
    :param G2: Second graph (Graph object)
    :return: A tuple containing:
             - A boolean indicating if any isomorphism exists
             - A list of mappings where each mapping is a dictionary that 
               maps vertices from G1 to corresponding vertices in G2.
    """
    # Check if the graphs have the same number of vertices, as isomorphisms are only possible in this case
    if len(G1.vertices) != len(G2.vertices):
        return False, []

    # Create lists of vertex names for both graphs to generate all possible permutations of G2's vertices
    vertex_names_G1 = list(G1.vertices.keys())
    vertex_names_G2 = list(G2.vertices.keys())
    all_mappings = []

    # Generate all permutations of G2's vertex names and try each as a possible mapping
    for perm in itertools.permutations(vertex_names_G2):
        # Create a mapping from G1 vertices to G2 vertices based on the current permutation
        mapping = {vertex_names_G1[i]: perm[i] for i in range(len(perm))}

         # Check if the mapping maintains the adjacency structure
        valid = True
        for v1 in G1.vertices.values():
            # Get the corresponding vertex in G2 based on the current mapping
            mapped_v1 = mapping[v1.name]

            # For each neighbor of v1 in G1, check if the corresponding neighbor exists in G2
            for neighbor, _ in v1.neighbors:
                mapped_neighbor = mapping[neighbor.name]
                
                # Find the corresponding vertex in G2 and check if an edge exists between them
                g2_v1 = G2.vertices[mapped_v1]
                found = any(n[0] == mapped_neighbor for n in g2_v1.neighbors)

                if not found:
                    valid = False
                    break
            
            if not valid:
                break
        # If the mapping is valid, add it to the list of valid mappings
        if valid:
            all_mappings.append(mapping)
            
    # Return a boolean indicating if there are any valid isomorphisms and the list of valid mappings
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
