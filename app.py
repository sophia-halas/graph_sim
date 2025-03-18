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
    # Pridanie vrcholov
    for node in data["nodes"]:
        vertex = Vertex(node["name"], float(node["membershipFunction"]))
        G.add_vertex(vertex)

    # Pridanie hrán
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
    data = request.json  # Očakávame JSON dáta
    tnorm = data["tnorm"]
 
    if 'nodes' not in data or 'edges' not in data:
        return ""

    # Vytvorenie grafu
    G = build_graph_from_json(data)

    # Výpočet twin-width
    tw_value, sequence = twin_width(G, tnorm)  # Funkcia teraz vracia aj postupnosť

    # Ošetrenie nekonečna
    if tw_value == float('inf'):
        tw_value = "X"  # Môžeš použiť aj nejaké veľké číslo, napr. 1e9

    return jsonify({
        'tw': tw_value,
        'sequence': sequence  # Zaslanie optimálnej postupnosti
    })


@app.route('/check-isomorphism', methods=['POST'])
def check_isomorphism():
    data = request.json

    if 'graph1' not in data or 'graph2' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    # Vytvorenie grafov
    G1 = build_graph_from_json(data['graph1'])
    G2 = build_graph_from_json(data['graph2'])

    # Nájdeme všetky izomorfizmy
    isomorphic, mappings = find_isomorphisms(G1, G2)

    return jsonify({
        'isomorphic': isomorphic,
        'mappings': mappings  # Zoznam všetkých možných mapovaní vrcholov
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
