## Fuzzy Graph Similarity Application
This web application was created as part of a bachelor's thesis. It focuses on comparing two fuzzy graphs using a method based on fuzzy twin-width. The user can create two fuzzy graphs, calculate their similarity, and list isomorphisms between them if they exist.

The application has a web-based interface (frontend) and a backend that handles the computational logic. The frontend is built with HTML, CSS, JavaScript, and the Cytoscape.js library for a simple fuzzy graph manipulation. The backend is implemented in Python using Flask, and it communicates with the frontend through HTTP POST requests with data in JSON format.

### Project Structure
├── `app.py` &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;# Flask backend
├── `backend/`
│ ├── `similarity.py` &emsp;&emsp;&emsp;# Fuzzy graph similarity calculation
│ ├── `isomorphism.py` &emsp;&emsp;# Graph isomorphism detection
│ └── `TWBackend.py` &emsp;&emsp;&emsp;&emsp;&emsp;# Fuzzy twin-width computation by Marek Effenberger
├── `static/`
│ ├── `css/style.css` &emsp;&emsp;&emsp;# App styles
│ └── `js/graph.js` &emsp;&emsp;&emsp;&emsp;# Graph drawing and API communication
├── `templates/`
│ └── `graph_sim.html` &emsp; &emsp;# Main HTML interface
├── `requirements.txt` &emsp;&emsp;# Python dependencies
└── `README.md` &emsp;&emsp;&emsp;&emsp;&emsp;# This documentation file

### How to Run the Application Locally
1. Go to the root directory of the project
`cd graph_sim`
2. (Optional) Upgrade `pip`
`python -m pip install --upgrade pip`
3. Install the required Python packages:
`python -m pip install -r requirements.txt`
4. Start the Flask server
`python app.py`
5. Open your browser and go to
`http://localhost:5000/graph-sim`

### How to Use the Application
The app provides two interactive graph panels where users can create and edit fuzzy graphs.

#### Graph Creation
`Add Node`: Adds a new node to the graph. You can set its membership value before placing it.

`Add Edge`: Adds an edge between selected nodes. Edge membership values can be defined in the input panel.

`Right-click`: Deletes the selected node or edge.

`Delete Graph`: Clears the entire graph panel.

#### Graph Settings
**T-norm selection**: You can choose which t-norm to use for the similarity and fuzzy twin-width calculations.

#### Calculations
`Compute`: This button triggers all calculations:

**Fuzzy Graph Similarity** – similarity score between the two graphs.

**Fuzzy twin-width 1** – the fuzzy twin-width value for the left graph.

**Fuzzy twin-width 2** – the fuzzy twin-width value for the right graph.

If one of the graphs is missing or the graphs are not isomorphic, a value of `X` is shown instead of a numeric result.

#### Isomorphisms
`Show isomorphisms`: Displays all possible mappings between nodes of the two graphs, if the graphs are isomorphic.

The node and edge weights are not considered when generating isomorphism mappings.