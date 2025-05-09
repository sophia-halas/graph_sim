## Fuzzy Graph Similarity Application
##### *Bachelor's Thesis, 2025 – Sophia Halasova (BUT FIT)*
This web application was created as part of a bachelor's thesis by Sophia Halasova. It focuses on comparing two fuzzy graphs using a method based on fuzzy twin-width. The user can create two fuzzy graphs, calculate their similarity, and list isomorphisms between them if they exist.

The application has a web-based interface - frontend and a backend that handles the computational logic. The frontend is built with HTML, CSS, JavaScript, and the Cytoscape.js library for a simple fuzzy graph manipulation. The backend is implemented in Python using Flask, and it communicates with the frontend through HTTP POST requests with data in JSON format.

The fuzzy twin-width computation was done by Marek Effenberger as a part of his bachelor's thesis. Some of the CSS styles were created with the help of ChatGPT to assist in designing the user interface.

### Project Structure
```
├── app.py              # Flask backend
├── backend/
│ ├── similarity.py     # Fuzzy graph similarity calculation
│ ├── isomorphism.py    # Graph isomorphism detection
│ └── TWBackend.py      # Fuzzy twin-width computation by Marek Effenberger
├── static/
│ ├── css/style.css     # App styles
│ └── js/graph.js       # Graph drawing and API communication
├── templates/
│ └── graph_sim.html    # Main HTML interface
├── requirements.txt    # Python dependencies
└── README.md           # This documentation file
```
### How to Run the Application Locally
1. Go to the root directory of the project
```bash
cd graph_sim
```
2. (Optional) Upgrade `pip`
```bash
python -m pip install --upgrade pip
```
3. Install the required Python packages
```bash
python -m pip install -r requirements.txt
```
4. Start the Flask server
```bash
python app.py
```
5. Open your browser and go to
```bash
http://localhost:5000/graph-sim
```

The app is also accessible online at https://graph-sim.onrender.com/graph-sim

### How to Use the Application
The app provides two interactive graph panels where users can create and edit fuzzy graphs.

#### Graph Creation
`Add Node`: Adds a new node to the graph. You can set its membership value before placing it.

`Add Edge`: Adds an edge between selected nodes. Edge membership values can be defined in the input panel.

`Right-click`: Deletes the selected node or edge.

`Delete Graph`: Clears the entire graph panel.

#### Graph Settings
*T-norm selection*: You can choose which t-norm to use for the similarity and fuzzy twin-width calculations.

#### Calculations
`Compute`: This button triggers all calculations:

*Fuzzy Graph Similarity* – similarity score between the two graphs.

*Fuzzy twin-width 1* – the fuzzy twin-width value for the left graph.

*Fuzzy twin-width 2* – the fuzzy twin-width value for the right graph.

If one of the graphs is missing or the graphs are not isomorphic, a value of `X` is shown instead of a numeric result.

#### Isomorphisms
`Show isomorphisms`: Displays all possible mappings between nodes of the two graphs, if the graphs are isomorphic.

The node and edge weights are not considered when generating isomorphism mappings.