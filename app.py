from flask import Flask, request, jsonify, render_template
from backend.tw_be import Graph, Vertex, twin_width  # Importuj svoje triedy a funkciu
from backend.isomorph import find_isomorphisms
from backend.similarity import compute_similarity
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def build_graph_from_json(data):
    """
    Creates Graph instance from json
    """
    G = Graph()
    # add nodes
    for node in data["nodes"]:
        vertex = Vertex(node["name"], float(node["membershipFunction"]))
        G.add_vertex(vertex)

    # add edges
    for edge in data["edges"]:
        u, v, weight = edge["source"], edge["target"], (float(edge["weight"]), 0)
        G.add_edge(u, v, weight)

    return G

@app.route('/', methods=['GET'])
def index():
    return "App is running!"

@app.route('/graph-sim', methods=['GET'])
def graph_sim():
    return render_template('graph_sim.html')

@app.route('/get-tw', methods=['POST'])
def get_tw():
    data = request.json  # awaiting json data
    tnorm = data["tnorm"]
 
    if 'nodes' not in data or 'edges' not in data:
        return ""

    # create graph
    G = build_graph_from_json(data)

    tw_value, sequence = twin_width(G, tnorm) 

    # invalid value
    if tw_value == float('inf'):
        tw_value = "X"  

    return jsonify({
        'tw': tw_value,
        'sequence': sequence 
    })


@app.route('/check-isomorphism', methods=['POST'])
def check_isomorphism():
    data = request.json

    if 'graph1' not in data or 'graph2' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    # create graphs
    G1 = build_graph_from_json(data['graph1'])
    G2 = build_graph_from_json(data['graph2'])

    # find all isomorphisms
    isomorphic, mappings = find_isomorphisms(G1, G2)

    return jsonify({
        'isomorphic': isomorphic,
        'mappings': mappings  
    })

@app.route('/get-similarity', methods=['POST'])
def get_similarity():
    data = request.json
    if 'graph1' not in data or 'graph2' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    G1 = build_graph_from_json(data['graph1'])
    G2 = build_graph_from_json(data['graph2'])
    tnorm = data["tnorm"]

    similarity = compute_similarity(G1, G2, tnorm)
    return jsonify({'similarity': similarity})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
