import numpy as np
from backend.isomorph import find_isomorphisms
from backend.tw_be import Graph, Vertex

def t_norm(u, v, tnorm):
    match tnorm:
        case "min":
            return min(u, v)
        case "prod":
            return u*v
        case "luk":
            return max(u + v - 1, 0)
        case "drast":
            if u == 1:
                return v
            elif v == 1:
                return u
            else:
                return 0
            
def s_norm(u, v, tnorm):
    match tnorm:
        case "min":
            return max(u, v)
        case "prod":
            return u + v - u * v
        case "luk":
            return min(u + v, 1)
        case "drast":
            if u == 0:
                return v
            elif v == 0:
                return u
            else:
                return 1

def compute_similarity(G1, G2, tnorm):
    """
    Computes fuzzy similarity of 2 fuzzy graphs
    
    :param G1: first fuzzy graph (Graph object)
    :param G2: second fuzzy graph (Graph object)
    :param tnorm: t-norm
    :return: Fuzzy similarity S(G1, G2) -> [0,1]
    """
    # find all isomorphisms
    isomorphic, mappings = find_isomorphisms(G1, G2)
    if not isomorphic:
        return "X"  # not possible to compute similarity

    r_values = []  # Uchovávame všetky r_k hodnoty

    for mapping in mappings:
        r_k_values = []
        processed_edges = set()

        for vertex_name, vertex in G1.vertices.items():
            mapped_vertex = G2.vertices[mapping[vertex_name]]
            

            # iterate through all neighbors in G1
            for neighbor, weight in vertex.neighbors:
                mapped_neighbor_name = mapping[neighbor]
                
                edge_id = tuple(sorted([vertex_name, neighbor]))  # for example ('A', 'C') or ('C', 'A')
                if edge_id in processed_edges:
                    continue  # the edge was processed already

                processed_edges.add(edge_id)

                # find edge in G2 and its weight
                mapped_weight = None
                for mapped_n, mapped_w in mapped_vertex.neighbors:
                    if mapped_n == mapped_neighbor_name:
                        mapped_weight = mapped_w
                        break
                
                # |hi - vi|
                if mapped_weight is not None:
                    r_k_values.append(abs(weight[0] - mapped_weight[0]))

        r_k = 0  # 0 is a neutral element in s-norms
 
        # apply s-norm on |hi - vi| values
        for diff in r_k_values:
            r_k = s_norm(r_k, diff, tnorm)

        r_values.append(r_k)

    r = 1 # 1 is a neutral element in t-norms

    # apply t-norm on all r_k values
    for r_k in r_values:
        r = t_norm(r, r_k, tnorm)
        print(r_k)
    return 1 - r
