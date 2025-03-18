import numpy as np
from isomorph import find_isomorphisms
from tw_be import Graph, Vertex

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
    Vypočíta podobnosť fuzzy grafov G1 a G2 podľa definovanej metriky.
    
    :param G1: Prvý fuzzy graf (Graph objekt)
    :param G2: Druhý fuzzy graf (Graph objekt)
    :param tnorm: Funkcia t-normy
    :return: Hodnota similarity S(G1, G2) v rozsahu [0, 1]
    """
    # Najdi všetky izomorfizmy
    isomorphic, mappings = find_isomorphisms(G1, G2)
    if not isomorphic:
        return "X"  # Ak nie sú izomorfné, similarity je 0

    r_values = []  # Uchovávame všetky r_k hodnoty

    for mapping in mappings:
        r_k_values = []
        processed_edges = set()

        for vertex_name, vertex in G1.vertices.items():
            mapped_vertex = G2.vertices[mapping[vertex_name]]
            

            # Prechádzame cez všetkých susedov v G1
            for neighbor, weight in vertex.neighbors:
                mapped_neighbor_name = mapping[neighbor]
                
                edge_id = tuple(sorted([vertex_name, neighbor]))  # Napr. ('A', 'C') alebo ('C', 'A')
                if edge_id in processed_edges:
                    continue  # Túto hranu sme už spracovali

                processed_edges.add(edge_id)

                # Nájdeme hranu v G2 a zistíme jej váhu
                mapped_weight = None
                for mapped_n, mapped_w in mapped_vertex.neighbors:
                    if mapped_n == mapped_neighbor_name:
                        mapped_weight = mapped_w
                        break
                
                if mapped_weight is not None:
                    r_k_values.append(abs(weight[0] - mapped_weight[0]))

        # S-norma na všetkých rozdieloch
        r_k = 0  # Začína od 0 (pre S-normu min je 0)
 
        for diff in r_k_values:
            r_k = s_norm(r_k, diff, tnorm)

        r_values.append(r_k)

    # T-norma na všetkých r_k hodnotách
    r = 1 # Začína od 1 (pre T-normu max je 1)
    for r_k in r_values:
        r = t_norm(r, r_k, tnorm)
        print(r_k)
    return 1 - r
