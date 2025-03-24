// Global variables for node management
let nodeId = 0; // Unique identifier for each node
var nodes = []; // Stores all nodes with their positions
var coloredNodesLeft = []; // Stores selected nodes for graph "cyLeft"
var coloredNodesRight = []; // Stores selected nodes for graph "cyRight"

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
                'background-color': 'blue', 
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
    if(degree < 0) degree = 0;
    if (degree > 1) degree = 1;
    let newNodeId = 'Node' + ++nodeId;
    let relPos = getRandomRelativePosition();

    nodes.push({ id: newNodeId, relPos: relPos });

    let absPos = getAbsolutePosition(graph, relPos);
    graph.add({ data: { id: newNodeId, label: `${newNodeId} Degree: ${degree}`, fuzzy_value:  degree}, position: absPos });
    console.log("Added Node: " + newNodeId);
}

/**
 * Removes the first colored node from the selected graph and resets its color to blue.
 * @param {string} graphId - The ID of the graph ("cyLeft" or "cyRight").
 */
function removeFirstColoredNode(graphId) {
    let coloredNodes = (graphId == "cyLeft") ? coloredNodesLeft : coloredNodesRight;
    let node = coloredNodes.shift();  
    node.style('background-color', 'blue');  

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
            node.style('background-color', 'blue'); 
            console.log('Node colored back to blue: ' + node.id());
            coloredNodes.splice(i, 1);
            updateButtonState();
            return; 
        }
    }

    if (coloredNodes.length == 2) removeFirstColoredNode(graphId);

    node.style('background-color', 'lime');
    coloredNodes.push(node);
    console.log('Node colored: ' + node.id());
    updateButtonState();
}

/**
 * Adds an edge between two selected nodes in the given graph.
 * The edge is assigned a fuzzy degree value based on user input.
 * @param {Object} graph - The Cytoscape graph instance.
 * @param {string} graphId - The ID of the graph ("cyLeft" or "cyRight").
 */
function  addEdge(graph, graphId) {
    let coloredNodes = (graphId == "cyLeft") ? coloredNodesLeft : coloredNodesRight; 
    if(coloredNodes.length != 2) return;
    let degree = parseFloat(document.getElementById("edgeDegree").value);
    if(degree < 0) degree = 0;
    if (degree > Math.max(coloredNodes[0].data('fuzzy_value'), coloredNodes[1].data('fuzzy_value'))) degree = Math.max(coloredNodes[0].data('fuzzy_value'), coloredNodes[1].data('fuzzy_value'));
    graph.add({data: {id: coloredNodes[0].id().concat(coloredNodes[1].id()),source: coloredNodes[0].id(),target: coloredNodes[1].id(), label: `Degree: ${degree}`, fuzzy_value:  degree}});
    console.log("Added Edge: " + coloredNodes[0].id().concat(coloredNodes[1].id() +  `Degree: ${degree}`));
        
}

/**
 * Deletes all nodes and edges from the given graph.
 * Resets selection states and disables the isomorphism button.
 * @param {Object} graph - The Cytoscape graph instance.
 */
function deleteGraph(graph) {
    graph.$('node').remove();
    graph.$('edge').remove();
    console.log("Deleted" + graph);
    coloredNodesLeft, coloredNodesRight = [];
    updateButtonState();
}

/**
 * Updates the relative position of a node after it has been moved.
 * @param {Object} graph - The Cytoscape graph instance.
 * @param {Object} node - The Cytoscape node object.
 */
function getNodePositionAfterMoving(graph, node) {
    let absPos = node.position(); 
    
    let relPos = {
        x: absPos.x / graph.width(),
        y: absPos.y / graph.height()
    };

    let nodeData = nodes.find(n => n.id === node.id());
    if (nodeData) {
        nodeData.relPos = relPos;
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
    if (index !== -1) coloredNodes.splice(index, 1);
    updateButtonState();
}

/**
 * Deletes a node or edge from the graph.
 * If the object is a selected node, it is also removed from the colored nodes list.
 * @param {Object} object - The Cytoscape node or edge to remove.
 * @param {string} [graph=null] - The ID of the graph ("cyLeft" or "cyRight"), if applicable.
 */
function deleteObject(object, graph = null) {
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
    const nodes = graph.nodes().map(node => {
        return {
            name: node.data('id'),
            membershipFunction: node.data('fuzzy_value') || 0 
        };
    });


    const edges = graph.edges().map(edge => {
        return {
            source: edge.source().data('id'),
            target: edge.target().data('id'),
            weight: edge.data('fuzzy_value') || [0, 0]  
        };
    });

    // create json object
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

    fetch('https://graph-sim.onrender.com/get-tw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(graphData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Twin-width:", data.tw);

        // Zaokrúhlenie hodnoty ak je číselná, inak nechaj prázdne
        document.getElementById(eleId).value = (data.tw !== null && data.tw !== undefined && data.tw != "X") 
            ? Math.round(data.tw * 10000) / 10000  // Zaokrúhlenie na 2 desatinné miesta
            : "X";
    })
    .catch(error => {
        console.error("Error while getiing Twin Width:", error);
        document.getElementById(eleId).value = ""; // Vyčistenie hodnoty pri chybe
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
    .catch(error => console.error("Error:", error));
}

/**
 * Displays a popup with the list of possible isomorphisms.
 * @param {Object} data - The response data containing isomorphism mappings.
 */
function openPopup(data) {
    let list = document.getElementById("isomorphismList");
    list.innerHTML = "";

    if (data.isomorphic) {
        data.mappings.forEach((mapping, index) => {
            let li = document.createElement("li");
            li.textContent = `${index + 1}: ${JSON.stringify(mapping)}`;
            list.appendChild(li);
        });
    } else {
        let li = document.createElement("li");
        li.textContent = "Graphs are not isomorphic.";
        list.appendChild(li);
    }

    document.getElementById("popup").style.display = "block";
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
 * Fetches and displays the similarity score between two graphs.
 * The result is shown in an input field.
 */
async function getSimilarity(){
    fetch('https://graph-sim.onrender.com/get-similarity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph1: graphToJson(cyLeft), graph2: graphToJson(cyRight), tnorm: document.getElementById("tNorm").value })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("sim").value = (data.similarity !== "X") ? Math.round(data.similarity * 10000) / 10000: "X";
        console.log("Graph similarity: " + data.similarity);
    })
    .catch(error => {
            console.error("Error:", error);
            showErrorMessage(error.message);
        });
}

/**
 * Displays an error message in the designated error box.
 * @param {string} message - The error message to display.
 */
function showErrorMessage(message) {
    const errorBox = document.getElementById("errorMessage");
    if (errorBox) {
        errorBox.innerHTML = `<p>${message}</p><button onclick="closeError()" style="margin-top: 10px; padding: 5px 10px;">Close</button>`;
        errorBox.style.display = "block";
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

function showLoading() {
    document.getElementById("loadingScreen").style.display = "flex";
}

function hideLoading() {
    document.getElementById("loadingScreen").style.display = "none";
}

var cyLeft = createEmptyGraph("cyLeft");
var cyRight = createEmptyGraph("cyRight");

document.getElementById("addNodeLeft").addEventListener("click", function() {addNode(cyLeft);});
document.getElementById("addNodeRight").addEventListener("click", function() { addNode(cyRight);});
document.getElementById("addEdgeLeft").addEventListener("click", function() {addEdge(cyLeft, "cyLeft");});
document.getElementById("addEdgeRight").addEventListener("click", function() { addEdge(cyRight, "cyRight");});
document.getElementById("deleteLeft").addEventListener("click", function() { deleteGraph(cyLeft);});
document.getElementById("deleteRight").addEventListener("click", function() { deleteGraph(cyRight);});
document.getElementById("compute").addEventListener("click", () => { showLoading(); setTimeout(async () => { await getTwinWidth(cyLeft, "tw1"); await getTwinWidth(cyRight, "tw2"); await getSimilarity(); hideLoading(); }, 100); });
window.addEventListener("resize", function() {nodes.forEach(node => {let absPos = getAbsolutePosition(cyLeft, node.relPos);cyLeft.getElementById(node.id).position(absPos);});});

//input limit
document.getElementById("nodeDegree").addEventListener("input", function() {let value = parseFloat(this.value); if (value < 0) this.value = 0; if (value > 1) this.value = 1;});
document.getElementById("edgeDegree").addEventListener("input", function() {let value = parseFloat(this.value); if (value < 0) this.value = 0; if (value > 1) this.value = 1;});

// prepisat !
document.getElementById("iso").addEventListener("click", async function() { await getIsomorphisms();});

cyLeft.on('tap', 'node', function(evt) {let node = evt.target; changeNodeColor(node, "cyLeft");});
cyRight.on('tap', 'node', function(evt) {let node = evt.target; changeNodeColor(node, "cyRight");});
cyLeft.on('dragfree', 'node', function(evt) {let node = evt.target; getNodePositionAfterMoving(cyLeft,node);});
cyRight.on('dragfree', 'node', function(evt) {let node = evt.target; getNodePositionAfterMoving(cyRight,node);});
cyLeft.on('cxttap', 'node', function(evt) {let node = evt.target; deleteObject(node, "cyLeft");});
cyRight.on('cxttap', 'node', function(evt) {let node = evt.target; deleteObject(node, "cyRight");});
cyLeft.on('cxttap', 'edge', function(evt) {let edge = evt.target; deleteObject(edge);});
cyRight.on('cxttap', 'edge', function(evt) {let edge = evt.target; deleteObject(edge);});