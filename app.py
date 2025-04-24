from flask import Flask, request, jsonify, render_template
from backend.tw_be import Graph, Vertex, twin_width  # Importuj svoje triedy a funkciu
from backend.isomorph import find_isomorphisms
from backend.similarity import compute_similarity
from flask_cors import CORS

app = Flask(__name__) # Initialize Flask app
CORS(app) # Allow cross-origin requests

def build_graph_from_json(data):
    """
    Converts JSON data into a Graph object.
    Returns None if the structure is invalid.
    """
    if not isinstance(data, dict) or 'nodes' not in data or 'edges' not in data:
        return None
    
    G = Graph()
    try:
        # Add nodes (vertices) to the graph
        for node in data["nodes"]:
            vertex = Vertex(node["name"], float(node["membershipFunction"]))
            G.add_vertex(vertex)

        # Add edges
        for edge in data["edges"]:
            u, v, weight = edge["source"], edge["target"], (float(edge["weight"]), 0)
            G.add_edge(u, v, weight)
        
        return G
    except (KeyError, ValueError, TypeError):
        return None # Return None if JSON structure is incorrect

@app.route('/', methods=['GET'])
def index():
    return "App is running!"

@app.route('/graph-sim', methods=['GET'])
def graph_sim():
    return render_template('graph_sim.html') # Render a front-end page 

@app.route('/get-tw', methods=['POST'])
def get_tw():
    """
    Computes the fuzzy Twin Width of a graph.
    """
    data = request.json  # awaiting json data
    if not data or "tnorm" not in data:
        return jsonify({'error': "Invalid input", 'tw': "X"}), 400
    tnorm = data["tnorm"]
    
    # Convert JSON to graph object
    G = build_graph_from_json(data)
    if not G:
        return jsonify({'error': "Invalid graph structure", 'tw': "X"}), 400

    # Compute twin-width
    tw_value, sequence = twin_width(G, tnorm) 

    # Handle invalid results
    if tw_value == float('inf'):
        tw_value = "X"  

    return jsonify({
        'tw': tw_value,
        'sequence': sequence 
    })


@app.route('/check-isomorphism', methods=['POST'])
def check_isomorphism():
    """
    Checks if two graphs are isomorphic and returns all valid mappings.
    """
    data = request.json

    if not data or "graph1" not in data or "graph2" not in data:
        return jsonify({'error': "Invalid input"}), 400

    # Convert JSON to Graph objects
    G1 = build_graph_from_json(data['graph1'])
    G2 = build_graph_from_json(data['graph2'])

    if not G1 or not G2:
        return jsonify({'error': "Invalid graph structure"}), 400
    
    # Find isomorphisms
    isomorphic, mappings = find_isomorphisms(G1, G2)

    return jsonify({
        'isomorphic': isomorphic,
        'mappings': mappings  
    })

@app.route('/get-similarity', methods=['POST'])
def get_similarity():
    """
    Computes the fuzzy similarity between two graphs.
    """
    data = request.json
    if not data or "graph1" not in data or "graph2" not in data or "tnorm" not in data:
        return jsonify({'error': "Invalid input"}), 400

    # Convert JSON to Graph objects
    G1 = build_graph_from_json(data['graph1'])
    G2 = build_graph_from_json(data['graph2'])
    if not G1 or not G2:
        return jsonify({'error': "Invalid graph structure"}), 400

    #vymazat!!!
    print(data['graph1'])
    print(data['graph2'])
    print(".................................")
    print(G1)
    print(G2)
    print("......isomorphism............")
    print(find_isomorphisms(G1, G2))


    # Compute similarity
    similarity = compute_similarity(G1, G2, data["tnorm"])
    return jsonify({'similarity': similarity})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) # Start Flask server
