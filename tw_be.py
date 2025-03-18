import random
from itertools import combinations
from copy import deepcopy
import re

#from sqlalchemy.sql.operators import truediv

infinity = float('inf')

lowest_max_degree = float('inf')
best_sequences = []

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

def merge_operation(u_black, u_red, v_black, v_red, operation, tnorm):
    if operation == 'node_merge' or operation == 'black_edge_merge':
        if tnorm == 'min':
            return max(u_black, v_black)
        elif tnorm == 'prod':
            print(f"u_black: {u_black}, v_black: {v_black}, tnorm: {tnorm}")
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

class Vertex:
    def __init__(self, name, membership_function):
        self.name = name
        self.membershipFunction = membership_function
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


class Graph:
    def __init__(self):
        self.vertices = {}
        optimum_sequence = []
        twin_width_value = 0

    def add_vertex(self, vertex):
        self.vertices[vertex.name] = vertex

    def add_edge(self, u, v, weight = (0, 0)):
        if u in self.vertices and v in self.vertices:
            self.vertices[u].add_neighbor(v, weight)
            self.vertices[v].add_neighbor(u, weight)

    def find_vertex(self, vertex_name):
        for vertex in self.vertices:
            if vertex == vertex_name:
                return self.vertices[vertex]
        return None

    def merge_vertices(self, u, v, tnorm):
    
        # Creating a new graph to store the merged vertices
        newGraph = Graph()

        new_vertices = self.vertices.copy()
        #print(f'Vertices: {list(new_vertices)}')


        if u in self.vertices and v in self.vertices:

            # The new vertex will have the name of the first vertex
            membership = merge_operation(self.vertices[u].membershipFunction, 0, self.vertices[v].membershipFunction, 0, 'node_merge', tnorm)
            # The new vertex will be named as the concatenation of the names of the vertices
            # its membership function will be the maximum of the two
            digits1 = re.sub(r"\D", "", u)
            digits2 = re.sub(r"\D", "", v)
            new_node_name = f'Node{digits1}{digits2}'
            new_vertex = Vertex(new_node_name, membership)

            # The neighbors of the new vertex will be the union of the neighbors of the two vertices
            new_vertex.neighbors = self.vertices[u].neighbors + self.vertices[v].neighbors

            #print(f'NEW Vertex {new_vertex.name} Membership: {membership} Neighbors: {new_vertex.neighbors}')

            new_vertex.remove_neighbor(u)
            new_vertex.remove_neighbor(v)

            # If there is some duplicated neighbor, remove one of them
            # for neighbor in new_vertex.neighbors:
            #     if new_vertex.neighbors.count(neighbor) > 1:
            #         new_vertex.remove_neighbor(neighbor[0])

            # The neighbors of the new vertex will be updated
            u_neighbors = self.vertices[u].neighbors
            v_neighbors = self.vertices[v].neighbors

            for neighbor in new_vertex.neighbors:

                if [n[0] for n in new_vertex.neighbors].count(neighbor[0]) > 1:
                    new_vertex.remove_neighbor(neighbor[0])

                u_weight = (0, 0)

                v_weight = (0, 0)

                # find the weight of the edge between the new vertex and the given neighbor
                if neighbor[0] in [n[0] for n in u_neighbors]:
                    u_weight = u_neighbors[[n[0] for n in u_neighbors].index(neighbor[0])][1]
                    new_vertex.remove_neighbor(neighbor[0])
                if neighbor[0] in [n[0] for n in v_neighbors]:
                    v_weight = v_neighbors[[n[0] for n in v_neighbors].index(neighbor[0])][1]
                    new_vertex.remove_neighbor(neighbor[0])

                # red_degree = max(u_weight[0], v_weight[0]) - min(u_weight[0]-u_weight[1], v_weight[0]-v_weight[1])
                # new_weight = (max(u_weight[0], v_weight[0]), red_degree)
                red_degree = merge_operation(u_weight[0], u_weight[1], v_weight[0], v_weight[1], 'red_edge_merge', tnorm)
                edge_membership = merge_operation(u_weight[0], 0, v_weight[0], 0, 'black_edge_merge', tnorm)
                new_weight = (edge_membership, red_degree)

                new_vertex.add_neighbor(neighbor[0], new_weight)

                if neighbor[0] in new_vertices:
                    if (u, u_weight) in new_vertices[neighbor[0]].neighbors:
                        new_vertices[neighbor[0]].neighbors.remove((u, u_weight))
                    if (v, v_weight) in new_vertices[neighbor[0]].neighbors:
                        new_vertices[neighbor[0]].neighbors.remove((v, v_weight))
                    new_vertices[neighbor[0]].add_neighbor(new_vertex.name, new_weight)

            new_vertices[new_vertex.name] = new_vertex
            new_vertices.pop(u)
            new_vertices.pop(v)

            newGraph.vertices = new_vertices

            # if len(newGraph.vertices) == 1:
            #     print(f'Final graph: {list(newGraph.vertices.keys())} Neighbors: {newGraph.vertices[new_vertex.name].neighbors}')
            return newGraph

    def find_maximum_error_degree(self):
        max_error_degree = 0
        # max_error_degree_vertex = None
        for vertex in self.vertices:
            #print(f'Vertex: {vertex}')
            #print(f'Neighbors: {self.vertices[vertex].neighbors}')
            error_degree = 0
            for neighbor in self.vertices[vertex].neighbors:
                error_degree += neighbor[1][1]
                if error_degree > max_error_degree:
                    max_error_degree = error_degree
        #           max_error_degree_vertex = vertex
        #print (f'Maximum error degree: {max_error_degree} at vertex {max_error_degree_vertex}')
        return max_error_degree

def twin_width(graph, tnorm):
    global lowest_max_degree, best_sequences
    lowest_max_degree = float('inf')
    best_sequences = []
    merge_all_sequences(graph, 0, tnorm)
    return lowest_max_degree, best_sequences

def merge_all_sequences(graph, max_degree, tnorm, sequence=[]):
    global lowest_max_degree, best_sequences

    if len(graph.vertices) == 1:
        #print(f'Sequence: {sequence}')
        #print(f'Max degree: {max_degree}')
        if max_degree < lowest_max_degree:
            lowest_max_degree = max_degree
            best_sequences = [sequence]
        elif max_degree == lowest_max_degree:
            best_sequences.append(sequence)
            
        return

    for u, v in combinations(graph.vertices.keys(), 2):
        # TODO: might switch the two lines below, when brain works again
        newG = deepcopy(graph).merge_vertices(u, v, tnorm)
        maximum_degree = newG.find_maximum_error_degree()
        new_sequence = sequence + [(u, v)]
        merge_all_sequences(newG, max(max_degree, maximum_degree), tnorm, new_sequence)


def merge_all_possible_pairs(graph):
    vertices = list(graph.vertices.keys())
    for u, v in combinations(vertices, 2):
        newG = graph.merge_vertices(u, v)
        #print(f'Merged {u} and {v} into new graph with vertices: {list(newG.vertices.keys())}')

def merge_two_least_error(graph):
    vertices = list(graph.vertices.keys())
    min_error = float('inf')
    min_error_vertices = None
    graphCopy = deepcopy(graph)
    for u, v in combinations(vertices, 2):
        newG = graphCopy.merge_vertices(u, v, 'min')
        # error equals the sum of the red degrees of the neighbors of the merged vertices
        error = 0
        u_digit = re.sub(r"\D", "", u)
        v_digit = re.sub(r"\D", "", v)
        new_node_key = f'Node{u_digit}{v_digit}'
        for neighbor in newG.vertices[new_node_key].neighbors:
            error += neighbor[1][1]
        if error < min_error:
            min_error = error
            min_error_vertices = (u, v)
        graphCopy = deepcopy(graph)
    if min_error_vertices:
        newG = graph.merge_vertices(min_error_vertices[0], min_error_vertices[1], 'min')
        #print(f'Merged {min_error_vertices[0]} and {min_error_vertices[1]} into new graph with vertices: {list(newG.vertices.keys())}')
        return newG, min_error_vertices

def merge_two_least_error_graphcheck(graph):
    vertices = list(graph.vertices.keys())
    min_error = float('inf')
    min_error_vertices = None
    graphCopy = deepcopy(graph)
    for u, v in combinations(vertices, 2):
        newG = graphCopy.merge_vertices(u, v, 'min')
        # error equals the sum of the red degrees of the neighbors of the merged vertices
        error = 0
        u_digit = re.sub(r"\D", "", u)
        v_digit = re.sub(r"\D", "", v)
        new_node_key = f'Node{u_digit}{v_digit}'
        error = newG.find_maximum_error_degree()
        #print(f'Error: {error}, Min error: {min_error}, Merged vertices: {u}, {v}')
        if error < min_error:
            min_error = error
            min_error_vertices = (u, v)
        graphCopy = deepcopy(graph)

    if min_error_vertices:
        newG = graph.merge_vertices(min_error_vertices[0], min_error_vertices[1], 'min')
        #print(f'Merged {min_error_vertices[0]} and {min_error_vertices[1]} into new graph with vertices: {list(newG.vertices.keys())}')
        return newG, min_error_vertices

def path_test():

    ftw_min = 0
    ftw_prod = 0
    ftw_luk = 0

    sequence_min = []
    sequence_prod = []
    sequence_luk = []

    max_len = 10
    num_vertices = 1

    running = True

    while running:
        # Construct the graph, the vertices and the edges
        # There should always be generated new vertex and connected to the previous one forming path -> Node0 to Node1 to Node2 etc.
        # Another permutation shall be generation of the edge memberships, they shall be random -> so one iteration Node0 0.1 Node1 0.2 Node2 0.3 Node3, next iteration Node0 0.3 Node1 0.1 Node2 0.2 Node3
        # Trying all combinations +0.1

        graph = Graph()

        for i in range(num_vertices):
            vertex = Vertex(f'Node{i}', 1)
            graph.add_vertex(vertex)

        for i in range(num_vertices - 1):
            random_membership = random.random()
            rounded = round(random_membership, 1)
            graph.add_edge(f'Node{i}', f'Node{i+1}', (rounded, 0))

        graphCopy = deepcopy(graph)
        secondGraphCopy = deepcopy(graph)

        print (f'Vertices: {list(graph.vertices.keys())}')
        for vertex in graph.vertices:
            print(f'Vertex: {vertex} Neighbors: {graph.vertices[vertex].neighbors}')

        twin_width(graph, 'min')
        ftw_min = lowest_max_degree
        sequence_min = best_sequences

        twin_width(graphCopy, 'prod')
        ftw_prod = lowest_max_degree
        sequence_prod = best_sequences

        twin_width(secondGraphCopy, 'luk')
        ftw_luk = lowest_max_degree
        sequence_luk = best_sequences

        if ftw_min != ftw_prod or ftw_min != ftw_luk or ftw_prod != ftw_luk:
            print(f'FTW min: {ftw_min} FTW prod: {ftw_prod} FTW luk: {ftw_luk}')
            print(f'Sequence min: {sequence_min}')
            print(f'Sequence prod: {sequence_prod}')
            print(f'Sequence luk: {sequence_luk}')
            running = False

        if num_vertices == max_len:
            running = False

        ftw_min = 0
        ftw_prod = 0
        ftw_luk = 0

        sequence_min = []
        sequence_prod = []
        sequence_luk = []

        num_vertices += 1

def path_test_v2():

    method_a = True
    method_b = True

    sequence_a = []
    sequence_b = []

    max_len = 10
    num_vertices = 1

    while method_a or method_b and num_vertices < max_len:
        # Construct the graph, the vertices and the edges
        # There should always be generated new vertex and connected to the previous one forming path -> Node0 to Node1 to Node2 etc.
        # Another permutation shall be generation of the edge memberships, they shall be random -> so one iteration Node0 0.1 Node1 0.2 Node2 0.3 Node3, next iteration Node0 0.3 Node1 0.1 Node2 0.2 Node3
        # Trying all combinations +0.1

        graph = Graph()

        for i in range(num_vertices):
            vertex = Vertex(f'Node{i}', 1)
            graph.add_vertex(vertex)

        for i in range(num_vertices - 1):
            random_membership = random.random()
            rounded = round(random_membership, 1)
            graph.add_edge(f'Node{i}', f'Node{i+1}', (rounded, 0))

        graphCopy = deepcopy(graph)
        secondGraphCopy = deepcopy(graph)

        print (f'Vertices: {list(graph.vertices.keys())}')
        for vertex in graph.vertices:
            print(f'Vertex: {vertex} Neighbors: {graph.vertices[vertex].neighbors}')

        while len(graphCopy.vertices) > 1:
            graphCopy, vertices = merge_two_least_error(graphCopy)
            sequence_a.append(vertices)

        while len(secondGraphCopy.vertices) > 1:
            secondGraphCopy, vertices = merge_two_least_error_graphcheck(secondGraphCopy)
            sequence_b.append(vertices)

        twin_width(graph, 'min')

        if sequence_a not in best_sequences:
            method_a = False
            print(f'Method A failed at {num_vertices} vertices')
            print(f'Best sequences: {best_sequences}')
            print(f'Sequence A: {sequence_a}')
        if sequence_b not in best_sequences:
            method_b = False
            print(f'Method B failed at {num_vertices} vertices')
            print(f'Best sequences: {best_sequences}')
            print(f'Sequence B: {sequence_b}')

        sequence_a = []
        sequence_b = []
        num_vertices += 1

def path_test_tnorm():

    ftw_min = 0
    ftw_prod = 0
    ftw_luk = 0

    sequence_min = []
    sequence_prod = []
    sequence_luk = []

    max_len = 10
    num_vertices = 1

    running = True

    while running:
        # Construct the graph, the vertices and the edges
        # There should always be generated new vertex and connected to the previous one forming path -> Node0 to Node1 to Node2 etc.
        # Another permutation shall be generation of the edge memberships, they shall be random -> so one iteration Node0 0.1 Node1 0.2 Node2 0.3 Node3, next iteration Node0 0.3 Node1 0.1 Node2 0.2 Node3
        # Trying all combinations +0.1

        graph = Graph()

        for i in range(num_vertices):
            vertex = Vertex(f'Node{i}', 1)
            graph.add_vertex(vertex)

        for i in range(num_vertices - 1):
            random_membership = random.random()
            rounded = round(random_membership, 1)
            graph.add_edge(f'Node{i}', f'Node{i+1}', (rounded, 0))

        graphCopy = deepcopy(graph)
        secondGraphCopy = deepcopy(graph)

        print (f'Vertices: {list(graph.vertices.keys())}')
        for vertex in graph.vertices:
            print(f'Vertex: {vertex} Neighbors: {graph.vertices[vertex].neighbors}')

        twin_width(graph, 'min')
        ftw_min = lowest_max_degree
        sequence_min = best_sequences

        twin_width(graphCopy, 'prod')
        ftw_prod = lowest_max_degree
        sequence_prod = best_sequences

        twin_width(secondGraphCopy, 'luk')
        ftw_luk = lowest_max_degree
        sequence_luk = best_sequences

        if ftw_min > ftw_prod or ftw_min > ftw_luk or ftw_prod > ftw_luk:
            print(f'FTW min: {ftw_min} FTW prod: {ftw_prod} FTW luk: {ftw_luk}')
            print(f'Sequence min: {sequence_min}')
            print(f'Sequence prod: {sequence_prod}')
            print(f'Sequence luk: {sequence_luk}')
            running = False

        if num_vertices == max_len:
            running = False

        ftw_min = 0
        ftw_prod = 0
        ftw_luk = 0

        sequence_min = []
        sequence_prod = []
        sequence_luk = []

        num_vertices += 1

if __name__ == '__main__':

     path_test_tnorm()