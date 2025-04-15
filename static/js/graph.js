// Global variables for node management
let nodeId = 0; // Unique identifier for each node
var nodes = []; // Stores all nodes with their positions
var coloredNodesLeft = []; // Stores selected nodes for graph "cyLeft"
var coloredNodesRight = []; // Stores selected nodes for graph "cyRight"

/**
 * Returns the value of the t-norm based on the given tnorm type and two values x and y.
 * 
 * @param {string} tnorm - The type of t-norm, can be minimum, lukasiewicz, product, or drastic product.
 * @param {number} x - The first value for the t-norm.
 * @param {number} y - The second value for the t-norm.
 * @returns {number} - The result of applying the t-norm to values x and y.
 */
function getTNormValue(tnorm, x, y) {
    switch (tnorm) {
        case "min":
            return Math.min(x, y);
        case "luk":
            return Math.max(x + y - 1, 0);
        case "prod":
            return x * y;
        case "drast":
            return Math.max(x, y) === 1 ? Math.min(x, y) : 0;
    }
}

/**
 * Generates a random relative position within the graph container.
 * Ensures nodes are placed within 10% to 90% of the container's width and height.
 * @returns {Object} Relative position { x, y }
 */
function getRandomRelativePosition() {
    let randomX = Math.random() * 0.8 + 0.1; // 10% - 90% of width
    let randomY = Math.random() * 0.8 + 0.1; // 10% - 90% of height
    return { x: randomX, y: randomY };
}

/**
 * Converts a relative position to an absolute position within the graph container.
 * @param {Object} graph - The Cytoscape graph instance.
 * @param {Object} relPos - The relative position { x, y }.
 * @returns {Object} Absolute position { x, y } in pixels.
 */
function getAbsolutePosition(graph, relPos) {
    let container = graph.container();
    let width = container.clientWidth;
    let height = container.clientHeight;

    return { x: relPos.x * width, y: relPos.y * height };
}


/**
 * Creates an empty Cytoscape graph inside the specified container.
 * @param {string} containerId - The ID of the HTML element to contain the graph.
 * @returns {Object} Cytoscape graph instance.
 */
function createEmptyGraph(containerId) { 
    return cytoscape({
        container: document.getElementById(containerId),
        elements: [],
        style: [ 
            { selector: 'node', style: { 
                'label': 'data(label)',
                'background-color': 'blue', // Default color for nodes
                'text-wrap': 'wrap',  
                'text-max-width': 70,
                'width':30,
                'height':30, 
                'font-size': 12
            }},
            { selector: 'edge', style: { 'label': 'data(label)','width': 2, 'line-color': 'black', 'target-arrow-shape': 'triangle', 'font-size': 12, 'text-rotation': 'autorotate', 'text-margin-y': -15,} }
        ],
        layout: { name: 'grid' } 
    });
}

/**
 * Adds a new node to the specified graph.
 * The node's position is randomized, and its fuzzy degree value is set by user input.
 * @param {Object} graph - The Cytoscape graph instance.
 */
function addNode(graph) { 
    let degree = parseFloat(document.getElementById("nodeDegree").value);
    if(degree < 0) degree = 0; // Ensure degree is not negative
    if (degree > 1) degree = 1; // Ensure degree is not greater than 1
    let newNodeId = 'Node' + ++nodeId;
    let relPos = getRandomRelativePosition(); // Generate random relative position

    nodes.push({ id: newNodeId, relPos: relPos });

    let absPos = getAbsolutePosition(graph, relPos); // Convert to absolute position
    graph.add({ data: { id: newNodeId, label: `${newNodeId} Degree: ${degree}`, fuzzy_value:  degree}, position: absPos });
    console.log("Added Node: " + newNodeId);
}

/**
 * Removes the first colored node from the selected graph and resets its color to blue.
 * @param {string} graphId - The ID of the graph ("cyLeft" or "cyRight").
 */
function removeFirstColoredNode(graphId) {
    let coloredNodes = (graphId == "cyLeft") ? coloredNodesLeft : coloredNodesRight;
    let node = coloredNodes.shift();   // Remove first colored node
    node.style('background-color', 'blue');  // Reset its color to blue

}

/**
 * Changes the color of a node to indicate selection.
 * If a node is already selected, it resets to blue; otherwise, it turns lime.
 * @param {Object} node - The Cytoscape node object.
 * @param {string} graphId - The ID of the graph ("cyLeft" or "cyRight").
 */
function changeNodeColor(node, graphId) {
    let coloredNodes = (graphId == "cyLeft") ? coloredNodesLeft : coloredNodesRight;
    for (var i = 0; i < coloredNodes.length; i++) {
        if (coloredNodes[i].id() == node.id()) {
            node.style('background-color', 'blue'); // Reset color to blue
            console.log('Node colored back to blue: ' + node.id());
            coloredNodes.splice(i, 1);  // Remove from selected nodes list
            updateButtonState(); // Update "Add Edge" button state after change
            return; 
        }
    }

    if (coloredNodes.length == 2) removeFirstColoredNode(graphId); // Ensure only 2 nodes are selected

    node.style('background-color', 'lime'); // Change selected node color to lime
    coloredNodes.push(node);  // Add to the selected nodes list
    console.log('Node colored: ' + node.id());
    updateButtonState();// Update "Add Edge" button state after change
}

/**
 * Adds an edge between two selected nodes in the given graph.
 * The edge is assigned a fuzzy degree value based on user input.
 * @param {Object} graph - The Cytoscape graph instance.
 * @param {string} graphId - The ID of the graph ("cyLeft" or "cyRight").
 */
function  addEdge(graph, graphId) {
    let coloredNodes = (graphId == "cyLeft") ? coloredNodesLeft : coloredNodesRight; 
    if(coloredNodes.length != 2) return; // Ensure exactly two nodes are selected to connect
    let degree = parseFloat(document.getElementById("edgeDegree").value);
    if(degree < 0) degree = 0; // Ensure degree is not negative
    max_allowed_edge_degree = getTNormValue(document.getElementById("tNorm").value, coloredNodes[0].data('fuzzy_value'), coloredNodes[1].data('fuzzy_value'));
    if (degree > max_allowed_edge_degree) degree = max_allowed_edge_degree;  // Ensure degree is not greater than the tnorm value of the 2 nodes
    // Add edge between the two selected nodes with the specified fuzzy degree
    graph.add({data: {id: coloredNodes[0].id().concat(coloredNodes[1].id()),source: coloredNodes[0].id(),target: coloredNodes[1].id(), label: `Degree: ${degree}`, fuzzy_value:  degree}});
    console.log("Added Edge: " + coloredNodes[0].id().concat(coloredNodes[1].id() +  `Degree: ${degree}`));
        
}

/**
 * Deletes all nodes and edges from the given graph.
 * Resets selection states and disables the isomorphism button.
 * @param {Object} graph - The Cytoscape graph instance.
 */
function deleteGraph(graph) {
    graph.$('node').remove(); // Remove all nodes
    graph.$('edge').remove(); // Remove all edges
    console.log("Deleted" + graph);
    // Clear the selected nodes list
    coloredNodesLeft = [];
    coloredNodesRight = [];
    updateButtonState(); // Update "Add Edge" button state after deletion
}

/**
 * Updates the relative position of a node after it has been moved.
 * @param {Object} graph - The Cytoscape graph instance.
 * @param {Object} node - The Cytoscape node object.
 */
function getNodePositionAfterMoving(graph, node) {
    let absPos = node.position(); // Get node's current absolute position
    
    let relPos = {
        x: absPos.x / graph.width(),
        y: absPos.y / graph.height()
    }; // Convert absolute position to relative position

    let nodeData = nodes.find(n => n.id === node.id());// Find the node data
    if (nodeData) {
        nodeData.relPos = relPos; // Update relative position in nodes list
        console.log(`Updated ${node.id()} -> relPos:`, relPos);
    }
}


/**
 * Removes an object from the list of colored nodes if it has been deleted from graph.
 * @param {Object} object - The node or edge to check.
 * @param {string} graph - The ID of the graph ("cyLeft" or "cyRight").
 */
function removeFromColoredNodesIfNecessary(object, graph){
    coloredNodes = graph === "cyLeft" ? coloredNodesLeft : coloredNodesRight;
    const index = coloredNodes.indexOf(object);
    if (index !== -1) coloredNodes.splice(index, 1);// Remove object from colored nodes if present
    updateButtonState(); // Update "Ad Edge" button state after removal
}

/**
 * Deletes a node or edge from the graph.
 * If the object is a selected node, it is also removed from the colored nodes list.
 * @param {Object} object - The Cytoscape node or edge to remove.
 * @param {string} [graph=null] - The ID of the graph ("cyLeft" or "cyRight"), if applicable.
 */
function deleteObject(object, graph = null) {
    // If the object to be deleted is a colored node (lime node) delete it from coloredNodes array
    if(graph) removeFromColoredNodesIfNecessary(object, graph);
    object.remove(); 
    console.log('Object removed: ' + object.id());
}

/**
 * Converts a Cytoscape graph into a JSON representation.
 * @param {Object} graph - The Cytoscape graph instance.
 * @returns {Object} JSON representation of the graph.
 */
function graphToJson(graph) {
    // Map nodes to JSON format with membership function
    const nodes = graph.nodes().map(node => {
        return {
            name: node.data('id'),
            membershipFunction: node.data('fuzzy_value') || 0 
        };
    });

    // Map edges to JSON format with weights (fuzzy values)
    const edges = graph.edges().map(edge => {
        return {
            source: edge.source().data('id'),
            target: edge.target().data('id'),
            weight: edge.data('fuzzy_value') || [0, 0]  
        };
    });

    // Create JSON object containing nodes and edges
    const graphData = {
        nodes: nodes,
        edges: edges
    };

    return graphData;
}


/**
 * Fetches the twin-width value of a given graph from a remote server.
 * @param {Object} graph - The Cytoscape graph instance.
 * @param {string} eleId - The ID of the HTML input element to display the result.
 */
function getTwinWidth(graph, eleId) {
    const graphData = graphToJson(graph);
    graphData.tnorm = document.getElementById("tNorm").value;

    // Send the graph data to the server to get the twin-width value
    fetch('https://graph-sim.onrender.com/get-tw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(graphData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`); // Handle error response
        }
        return response.json(); // Parse the response as JSON
    })
    .then(data => {
        console.log("Twin-width:", data.tw);

        // Round the twin-width value if numeric and update the result input
        document.getElementById(eleId).value = (data.tw !== null && data.tw !== undefined && data.tw != "X") 
            ? Math.round(data.tw * 10000) / 10000  // Round to 2 decimals
            : "X"; // Display "X" if no valid twin-width
    })
    .catch(error => {
        showErrorMessage(error.message);
        console.error("Error while getting Twin Width:", error);
        document.getElementById(eleId).value = "X"; 
    });
}



/**
 * Fetches and displays possible isomorphisms between two graphs.
 * The result is shown in a popup after clicking "Show isomorphisms" button.
 */
async function getIsomorphisms(){
    fetch('https://graph-sim.onrender.com/check-isomorphism', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph1: graphToJson(cyLeft), graph2: graphToJson(cyRight) })
    })
    .then(response => response.json())
    .then(data => {
        if (data.isomorphic) {
            console.log("Graphs are isomorphic.");
            console.log("Possible isomorphisms:", data.mappings);
            
        } else {
            console.log("Graphs are not isomorphic.");
        }
        openPopup(data);
    })
    .catch(error => {
        showErrorMessage(error.message);
        console.error("Error:", error);
    });
}

/**
 * Fetches and displays the similarity score between two graphs.
 * The result is shown in an input field.
 */
async function getSimilarity(){
    // Send request to server to get the similarity between two graphs
    fetch('https://graph-sim.onrender.com/get-similarity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph1: graphToJson(cyLeft), graph2: graphToJson(cyRight), tnorm: document.getElementById("tNorm").value })
    })
    .then(response => response.json())// Parse the response as JSON
    .then(data => {
        document.getElementById("sim").value = (data.similarity !== "X") ? Math.round(data.similarity * 10000) / 10000: "X";  // Update similarity input
        console.log("Graph similarity: " + data.similarity);
    })
    .catch(error => {
            console.error("Error:", error);
            showErrorMessage(error.message);
        });
}

/**
 * Displays a popup with the list of possible isomorphisms.
 * @param {Object} data - The response data containing isomorphism mappings.
 */
function openPopup(data) {
    let list = document.getElementById("isomorphismList");
    list.innerHTML = "";// Clear previous list items

    // If graphs are isomorphic, display the mappings
    if (data.isomorphic) {
        data.mappings.forEach((mapping, index) => {
            let li = document.createElement("li");
            li.textContent = `${index + 1}: ${JSON.stringify(mapping)}`;  // Display mapping index and data
            list.appendChild(li);
        });
    } else {
        let li = document.createElement("li");
        li.textContent = "Graphs are not isomorphic.";   // Display message if not isomorphic
        list.appendChild(li);
    }

    document.getElementById("popup").style.display = "block"; // Show the popup
}


/**
 * Closes the error message box.
 */
function closeError(){
    document.getElementById("errorMessage").style.display = "none";

}

/**
 * Closes the popup.
 */
function closePopup() {
    document.getElementById("popup").style.display = "none";
}


/**
 * Displays an error message in the designated error box.
 * @param {string} message - The error message to display.
 */
function showErrorMessage(message) {
    const errorBox = document.getElementById("errorMessage");
    if (errorBox) {
        errorBox.innerHTML = `<p>${message}</p><button onclick="closeError()" style="margin-top: 10px; padding: 5px 10px;">Close</button>`;
        errorBox.style.display = "block"; // Display the error box
    }
}

/**
 * Updates the state of the "Add Edge" buttons.
 * Enables the button only if exactly two nodes are selected.
 */
function updateButtonState() {
    let button = document.getElementById("addEdgeLeft");
    button.disabled = (coloredNodesLeft.length !== 2);
    button = document.getElementById("addEdgeRight");
    button.disabled = (coloredNodesRight.length !== 2);
}

/**
 * Opens the help modal.
 */
function openModal() {
    document.getElementById("helpModal").style.display = "block";
}


/**
 * Closes the help modal.
 */
function closeModal() {
    document.getElementById("helpModal").style.display = "none";
}

/**
 * Shows loading screen.
 */
function showLoading() {
    document.getElementById("loadingScreen").style.display = "flex";
}

/**
 * Hides loading screen.
 */
function hideLoading() {
    document.getElementById("loadingScreen").style.display = "none";
}

// Graph instances for left and right graphs
var cyLeft = createEmptyGraph("cyLeft");
var cyRight = createEmptyGraph("cyRight");

// Event listeners for various actions on the left and right graphs
document.getElementById("addNodeLeft").addEventListener("click", function() {addNode(cyLeft);});
document.getElementById("addNodeRight").addEventListener("click", function() { addNode(cyRight);});
document.getElementById("addEdgeLeft").addEventListener("click", function() {addEdge(cyLeft, "cyLeft");});
document.getElementById("addEdgeRight").addEventListener("click", function() { addEdge(cyRight, "cyRight");});
document.getElementById("deleteLeft").addEventListener("click", function() { deleteGraph(cyLeft);});
document.getElementById("deleteRight").addEventListener("click", function() { deleteGraph(cyRight);});
//document.getElementById("compute").addEventListener("click", () => { showLoading(); setTimeout(async () => { await getTwinWidth(cyLeft, "tw1"); await getTwinWidth(cyRight, "tw2"); await getSimilarity(); hideLoading(); }, 100); });
document.getElementById("compute").addEventListener("click", async () => {
    showLoading();

    // nechaj browser "vymaľovať" loading screen
    await new Promise(resolve => setTimeout(resolve, 0));

    await getTwinWidth(cyLeft, "tw1");
    await getTwinWidth(cyRight, "tw2");
    await getSimilarity();

    hideLoading();
});

document.getElementById("iso").addEventListener("click", async function() { await getIsomorphisms();});

window.addEventListener("resize", function() {nodes.forEach(node => {let absPos = getAbsolutePosition(cyLeft, node.relPos);cyLeft.getElementById(node.id).position(absPos);});});

// Input validation for node and edge degree
document.getElementById("nodeDegree").addEventListener("input", function() {let value = parseFloat(this.value); if (value < 0) this.value = 0; if (value > 1) this.value = 1;});
document.getElementById("edgeDegree").addEventListener("input", function() {let value = parseFloat(this.value); if (value < 0) this.value = 0; if (value > 1) this.value = 1;});

// Handle node interactions for left and right graphs
cyLeft.on('tap', 'node', function(evt) {let node = evt.target; changeNodeColor(node, "cyLeft");});
cyRight.on('tap', 'node', function(evt) {let node = evt.target; changeNodeColor(node, "cyRight");});
cyLeft.on('dragfree', 'node', function(evt) {let node = evt.target; getNodePositionAfterMoving(cyLeft,node);});
cyRight.on('dragfree', 'node', function(evt) {let node = evt.target; getNodePositionAfterMoving(cyRight,node);});
cyLeft.on('cxttap', 'node', function(evt) {let node = evt.target; deleteObject(node, "cyLeft");});
cyRight.on('cxttap', 'node', function(evt) {let node = evt.target; deleteObject(node, "cyRight");});
cyLeft.on('cxttap', 'edge', function(evt) {let edge = evt.target; deleteObject(edge);});
cyRight.on('cxttap', 'edge', function(evt) {let edge = evt.target; deleteObject(edge);});