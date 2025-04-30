# twinwidth_backend.py
# The following code is a Python implementation of the (fuzzy) twin-width algorithm.
# It uses a representation of graph and vertices as classes.
# The algorithm and computation is based on Twin-Width Fuzzification by Marek Effenberger
# Created by Marek Effenberger as a part of his bachelor thesis, BUT FIT 2025

from itertools import combinations
from copy import deepcopy
import re

# Global constants, for basic computation, only the first three are used
infinity = float('inf')
lowest_max_degree = float('inf')
best_sequences = []

lowest_max_degree2 = float('inf')
best_sequences2 = []
lowest_max_degree3 = float('inf')
best_sequences3 = []

# Functions for t-norms and t-conorms
def drastic_tnorm(u, v):
    if u == 1:
        return v
    elif v == 1:
        return u
    else:
        return 0

def drastic_tconorm(u, v):
    if u == 0:
        return v
    elif v == 0:
        return u
    else:
        return 1

# Depending on the operation, the function will return the result of the operation
def merge_operation(u_black, u_red, v_black, v_red, operation, tnorm):
    if operation == 'node_merge' or operation == 'black_edge_merge':
        if tnorm == 'min':
            return max(u_black, v_black)
        elif tnorm == 'prod':
            return u_black + v_black - u_black * v_black
        elif tnorm == 'luk':
            return min(u_black + v_black, 1)
        elif tnorm == 'drast':
            return drastic_tconorm(u_black, v_black)

    else:
        if tnorm == 'min':
            return max(u_black, v_black) - min(u_black - u_red, v_black - v_red)
        elif tnorm == 'prod':
            return (u_black + v_black - u_black * v_black) - ((u_black - u_red) * (v_black - v_red))
        elif tnorm == 'luk':
            return min(u_black + v_black, 1) - max(0, u_black - u_red + v_black - v_red - 1)
        elif tnorm == 'drast':
            return drastic_tconorm(u_black, v_black) - drastic_tnorm(u_black - u_red, v_black - v_red)

# Class for the vertex of the graph, which contains the name of the vertex, its membership function and its neighbors
class Vertex:
    def __init__(self, name, membership_function):
        self.name = name
        self.membershipFunction = membership_function
        # Neighbors are stored as a list of tuples, where each tuple contains the name of the neighbor and (black, red) edge weights
        self.neighbors = list()

    def add_neighbor(self, vertex, weight=(0, 0)):
        if vertex not in [n[0] for n in self.neighbors]:
            self.neighbors.append((vertex, weight))
        else:
            for i, neighbor in enumerate(self.neighbors):
                if neighbor[0] == vertex:
                    self.neighbors[i] = (vertex, weight)
                    break

    def remove_neighbor(self, vertex_name):
        self.neighbors = [n for n in self.neighbors if n[0] != vertex_name]

# Graph class, which contains the vertices and edges of the graph
class Graph:
    def __init__(self):
        self.vertices = {}
        optimum_sequence = []
        twin_width_value = 0

    # Function to add a vertex to the graph
    def add_vertex(self, vertex):
        self.vertices[vertex.name] = vertex

    # Function to add an edge to the graph
    def add_edge(self, u, v, weight = (0, 0)):
        if u in self.vertices and v in self.vertices:
            self.vertices[u].add_neighbor(v, weight)
            self.vertices[v].add_neighbor(u, weight)

    # Function to remove an edge from the graph
    def find_vertex(self, vertex_name):
        for vertex in self.vertices:
            if vertex == vertex_name:
                return self.vertices[vertex]
        return None

    # Function to merge two vertices, constructing a new graph
    def merge_vertices(self, u, v, tnorm):

        # Creating a new graph to store the merged vertices
        newGraph = Graph()

        # Copying the vertices of the original graph to the new graph
        new_vertices = self.vertices.copy()

        # If the vertices to be merged are in the graph
        if u in self.vertices and v in self.vertices:

            # We first compute the new sigma of the merged vertex according to the thesis
            membership = merge_operation(self.vertices[u].membershipFunction, 0, self.vertices[v].membershipFunction, 0, 'node_merge', tnorm)
            # The new vertex will be named as the concatenation of the names of the vertices
            digits1 = re.sub(r"\D", "", u)
            digits2 = re.sub(r"\D", "", v)
            new_node_name = f'Node{digits1}{digits2}'
            new_vertex = Vertex(new_node_name, membership)

            # The neighbors of the new vertex will be the union of the neighbors of the two vertices
            new_vertex.neighbors = self.vertices[u].neighbors + self.vertices[v].neighbors

            # From the neighbors of the new vertex, we remove the vertices u and v
            new_vertex.remove_neighbor(u)
            new_vertex.remove_neighbor(v)

            # For each neighbour of the union, we compute the new edge values
            u_neighbors = self.vertices[u].neighbors
            v_neighbors = self.vertices[v].neighbors
            for neighbor in new_vertex.neighbors:

                # Prevention of double edges
                if [n[0] for n in new_vertex.neighbors].count(neighbor[0]) > 1:
                    new_vertex.remove_neighbor(neighbor[0])

                # Default values for the edge weights
                u_weight = (0, 0)
                v_weight = (0, 0)

                # Find the weight of the edge between the new vertex and the given neighbor
                if neighbor[0] in [n[0] for n in u_neighbors]:
                    u_weight = u_neighbors[[n[0] for n in u_neighbors].index(neighbor[0])][1]
                    new_vertex.remove_neighbor(neighbor[0])
                if neighbor[0] in [n[0] for n in v_neighbors]:
                    v_weight = v_neighbors[[n[0] for n in v_neighbors].index(neighbor[0])][1]
                    new_vertex.remove_neighbor(neighbor[0])

                # Compute the new edge weights, namely (\mu_T, and \mu_R) (the \mu_B is a subtraction of the two)
                red_degree = merge_operation(u_weight[0], u_weight[1], v_weight[0], v_weight[1], 'red_edge_merge', tnorm)
                edge_membership = merge_operation(u_weight[0], 0, v_weight[0], 0, 'black_edge_merge', tnorm)
                # The new edge weight is a tuple of the form (total, red)
                new_weight = (edge_membership, red_degree)
                # Add the new edge to the new vertex
                new_vertex.add_neighbor(neighbor[0], new_weight)

                # If the neighbor is not u or v, we need to update the neighbor's edge weights
                if neighbor[0] in new_vertices:
                    if (u, u_weight) in new_vertices[neighbor[0]].neighbors:
                        new_vertices[neighbor[0]].neighbors.remove((u, u_weight))
                    if (v, v_weight) in new_vertices[neighbor[0]].neighbors:
                        new_vertices[neighbor[0]].neighbors.remove((v, v_weight))
                    new_vertices[neighbor[0]].add_neighbor(new_vertex.name, new_weight)

            # Add the new vertex to the new graph and remove the merged vertices
            new_vertices[new_vertex.name] = new_vertex
            new_vertices.pop(u)
            new_vertices.pop(v)

            newGraph.vertices = new_vertices

            return newGraph

    # Function to find the maximum error degree of the graph
    def find_maximum_error_degree(self):
        max_error_degree = 0
        for vertex in self.vertices:
            error_degree = 0
            for neighbor in self.vertices[vertex].neighbors:
                error_degree += neighbor[1][1]
                if error_degree > max_error_degree:
                    max_error_degree = error_degree

        return max_error_degree

# Function which sets the variables needed for the computation and runs the recursive function
def twin_width(graph, tnorm):
    global lowest_max_degree, best_sequences
    lowest_max_degree = float('inf')
    best_sequences = []
    merge_all_sequences(graph, 0, tnorm)
    return lowest_max_degree, best_sequences

# The actual recursive function which computes the twin-width of the graph
# It merges all possible pairs of vertices and computes the maximum error degree of the new graph
# For each sequence it computes the width, and if it is lower than the current minimum, it updates the minimum
def merge_all_sequences(graph, max_degree, tnorm, sequence=[]):
    global lowest_max_degree, best_sequences

    if len(graph.vertices) == 1:
        if max_degree < lowest_max_degree:
            lowest_max_degree = max_degree
            best_sequences = [sequence]
        elif max_degree == lowest_max_degree:
            best_sequences.append(sequence)
        return

    for u, v in combinations(graph.vertices.keys(), 2):
        newG = deepcopy(graph).merge_vertices(u, v, tnorm)
        maximum_degree = newG.find_maximum_error_degree()
        new_sequence = sequence + [(u, v)]
        merge_all_sequences(newG, max(max_degree, maximum_degree), tnorm, new_sequence)

# Function to merge all possible pairs of vertices in the graph
def merge_all_possible_pairs(graph):
    vertices = list(graph.vertices.keys())
    for u, v in combinations(vertices, 2):
        newG = graph.merge_vertices(u, v)

if __name__ == '__main__':
    # Example usage
    g = Graph()
    g.add_vertex(Vertex('Node1', 0.5))
    g.add_vertex(Vertex('Node2', 0.5))
    g.add_vertex(Vertex('Node3', 0.5))
    g.add_edge('Node1', 'Node2', (0.5, 0.5))
    g.add_edge('Node2', 'Node3', (0.5, 0.5))
    g.add_edge('Node1', 'Node3', (0.5, 0.5))

    result = twin_width(g, 'min')
    print(f"Lowest max degree: {result[0]}")
    print(f"Best sequences: {result[1]}")
