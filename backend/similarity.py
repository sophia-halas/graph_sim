"""
Author:        Sophia Halasova
File:          similarity.py

This module provides functions for computing the similarity between two 
fuzzy graphs. It includes support for multiple t-norm functions 
(Minimum t-norm, Product t-norm, Łukasiewicz t-norm, Drastic Product)
and uses graph isomorphisms as a prerequisite for similarity evaluation.
This code is part of a bachelor thesis focused on fuzzy graph similarity
by Sophia Halasova at BUT FIT in 2025.
"""
import numpy as np
from backend.isomorph import find_isomorphisms
from backend.TWBackend import Graph, Vertex

def t_norm(u, v, tnorm):
    """
    Computes the t-norm (triangular norm) for two values based on the selected t-norm type.
    
    :param u: First value (0 to 1)
    :param v: Second value (0 to 1)
    :param tnorm: Type of t-norm to use ('min', 'prod', 'luk', 'drast')
    :return: The computed t-norm value
    """
    match tnorm:
        case "min": # Minimum t-norm
            return min(u, v)
        case "prod": # Product t-norm
            return u*v
        case "luk": # Łukasiewicz t-norm
            return max(u + v - 1, 0)
        case "drast": # Drastic t-norm
            if u == 1:
                return v
            elif v == 1:
                return u
            else:
                return 0

def compute_similarity(G1, G2, tnorm):
    """
    Computes the fuzzy similarity between two fuzzy graphs.

    The function first finds all possible isomorphisms between the graphs. 
    If they are not isomorphic, similarity cannot be computed. 
    Otherwise, it calculates a similarity measure using t-norm operations.

    :param G1: First fuzzy graph (Graph object)
    :param G2: Second fuzzy graph (Graph object)
    :param tnorm: The t-norm used in the computation
    :return: Fuzzy similarity S(G1, G2) in the range [0,1] or "X" if isomorphism does not exist
    """
    # Find all isomorphisms between G1 and G2
    isomorphic, mappings = find_isomorphisms(G1, G2)
    if not isomorphic:
        return "X"  # If graphs are not isomorphic, return "X" to indicate that similarity cannot be computed

    r_k_values = []  # Stores all computed r_k values for each isomorphism
    num_edges = sum(len(vertex.neighbors) for vertex in G1.vertices.values()) // 2 # number of edges in G1
     # Iterate through all found isomorphisms
    for mapping in mappings:
        r_i = 0  # Initialize the similarity measure for the current isomorphism
        processed_edges = set() # Keep track of processed edges to avoid duplicates

        for vertex_name, vertex in G1.vertices.items():
            # Get the mapped vertex in G2 according to the current isomorphism
            mapped_vertex = G2.vertices[mapping[vertex_name]]
            

            # Iterate through all neighbors of the vertex in G1
            for neighbor, weight in vertex.neighbors:
                mapped_neighbor_name = mapping[neighbor]
                
                # Create an edge identifier (unordered) to ensure each edge is processed once
                edge_id = tuple(sorted([vertex_name, neighbor]))  
                if edge_id in processed_edges:
                    continue  # Skip if this edge has already been processed

                processed_edges.add(edge_id)

                # Find the corresponding edge in G2 and get its weight
                mapped_weight = None
                for mapped_n, mapped_w in mapped_vertex.neighbors:
                    if mapped_n == mapped_neighbor_name:
                        mapped_weight = mapped_w
                        break
                
                # ri += |hi - vi|^pow
                if mapped_weight is not None:
                    r_i += pow((abs(weight[0] - mapped_weight[0])), num_edges)
                    

        # Compute the n-th root of r_i
        r_i = r_i ** (1/num_edges)

        # Store the computed r_i for this isomorphism
        r_k_values.append(r_i)

    r = 1 # Initialize r to 1, as it is the neutral element in t-norms

    # Apply t-norm to all r_k values
    for r_k in r_k_values:
        r = t_norm(r, r_k, tnorm)

    return 1 - r # The final similarity measure is 1 minus the computed value