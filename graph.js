let nodeId = 0;
var nodes = [];
var coloredNodesLeft = [];
var coloredNodesRight = [];

function getRandomRelativePosition() {
    let randomX = Math.random() * 0.8 + 0.1; // 10% až 90% šírky
    let randomY = Math.random() * 0.8 + 0.1; // 10% až 90% výšky
    return { x: randomX, y: randomY };
}

function getAbsolutePosition(graph, relPos) {
    let container = graph.container();
    let width = container.clientWidth;
    let height = container.clientHeight;

    return { x: relPos.x * width, y: relPos.y * height };
}
function createEmptyGraph(containerId) { 
    return cytoscape({
        container: document.getElementById(containerId),
        elements: [],
        style: [ 
            { selector: 'node', style: { 
                'label': 'data(label)',
                'background-color': 'blue', 
                'text-wrap': 'wrap',   // Povolenie zalomenia textu
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

function addNode(graph) { 
    document.getElementById("iso").disabled = true;
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

function removeFirstColoredNode(graphId) {
    let coloredNodes = (graphId == "cyLeft") ? coloredNodesLeft : coloredNodesRight;
    let node = coloredNodes.shift();  
    node.style('background-color', 'blue');  

}

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

function  addEdge(graph, graphId) {
    document.getElementById("iso").disabled = true;
    let coloredNodes = (graphId == "cyLeft") ? coloredNodesLeft : coloredNodesRight; 
    if(coloredNodes.length != 2) return;
    let degree = parseFloat(document.getElementById("edgeDegree").value);
    if(degree < 0) degree = 0;
    if (degree > Math.max(coloredNodes[0].data('fuzzy_value'), coloredNodes[1].data('fuzzy_value'))) degree = Math.max(coloredNodes[0].data('fuzzy_value'), coloredNodes[1].data('fuzzy_value'));
    graph.add({data: {id: coloredNodes[0].id().concat(coloredNodes[1].id()),source: coloredNodes[0].id(),target: coloredNodes[1].id(), label: `Degree: ${degree}`, fuzzy_value:  degree}});
    console.log("Added Edge: " + coloredNodes[0].id().concat(coloredNodes[1].id() +  `Degree: ${degree}`));
        
}

function deleteGraph(graph) {
    graph.$('node').remove();
    graph.$('edge').remove();
    console.log("Deleted" + graph);
    document.getElementById("iso").disabled = true;
    updateButtonState();
}

function getNodePositionAfterMoving(graph, node) {
    let absPos = node.position(); // Absolútna pozícia
    
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

function deleteObject(object) {
    object.remove(); 
    console.log('Object removed: ' + object.id());
    document.getElementById("iso").disabled = true;
}
function graphToJson(graph) {
    // Získanie uzlov
    const nodes = graph.nodes().map(node => {
        return {
            name: node.data('id'),
            membershipFunction: node.data('fuzzy_value') || 0  // Predpokladám, že "membershipFunction" je v date uzla
        };
    });

    // Získanie hrán
    const edges = graph.edges().map(edge => {
        return {
            source: edge.source().data('id'),
            target: edge.target().data('id'),
            weight: edge.data('fuzzy_value') || [0, 0]  // Predpokladám, že "weight" je v date hrany
        };
    });

    // Vytvorenie JSON objektu
    const graphData = {
        nodes: nodes,
        edges: edges
    };

    return graphData;
}

// TWIN WIDTH
async function getTwinWidth(graph, eleId) {
    const graphData = graphToJson(graph)
    graphData.tnorm = document.getElementById("tNorm").value;
    try {
        const response = await fetch('http://127.0.0.1:5000/get-tw', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(graphData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Twin-width:", data.tw);

        // Set to empty value if twin width is null or undefined
        //treba este zaokruhlit
        document.getElementById(eleId).value = data.tw !== null && data.tw !== undefined ? data.tw : "";

        return data.tw;
    } catch (error) {
        console.error("Chyba pri získavaní twin-width:", error);
        document.getElementById("tw1").value = ""; // Empty value when error
    }
}

async function getIsomorphisms(){
    fetch('http://127.0.0.1:5000/check-isomorphism', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph1: graphToJson(cyLeft), graph2: graphToJson(cyRight) })
    })
    .then(response => response.json())
    .then(data => {
        if (data.isomorphic) {
            console.log("Graphs are isomorphic.");
            console.log("Possible isomorphisms:", data.mappings);
            openPopup(data);
        } else {
            console.log("Graphs are not isomorphic.");
        }
    })
    .catch(error => console.error("Error:", error));
}

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

function closePopup() {
    document.getElementById("popup").style.display = "none";
}

async function getSimilarity(){
    fetch('http://127.0.0.1:5000/get-similarity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph1: graphToJson(cyLeft), graph2: graphToJson(cyRight), tnorm: document.getElementById("tNorm").value })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("sim").value = data.similarity;
        console.log("Graph similarity: " + data.similarity)
        if(data.similarity !== "X") document.getElementById("iso").disabled = false;
    })
    .catch(error => console.error("Error:", error));
}

function updateButtonState() {
    let button = document.getElementById("addEdgeLeft");
    button.disabled = (coloredNodesLeft.length !== 2);
    button = document.getElementById("addEdgeRight");
    button.disabled = (coloredNodesRight.length !== 2);
}

// Volanie funkcie vždy, keď sa `coloredNodes` zmení

var cyLeft = createEmptyGraph("cyLeft");
var cyRight = createEmptyGraph("cyRight");

document.getElementById("addNodeLeft").addEventListener("click", function() {addNode(cyLeft);});
document.getElementById("addNodeRight").addEventListener("click", function() { addNode(cyRight);});
document.getElementById("addEdgeLeft").addEventListener("click", function() {addEdge(cyLeft, "cyLeft");});
document.getElementById("addEdgeRight").addEventListener("click", function() { addEdge(cyRight, "cyRight");});
document.getElementById("deleteLeft").addEventListener("click", function() { deleteGraph(cyLeft);});
document.getElementById("deleteRight").addEventListener("click", function() { deleteGraph(cyRight);});
document.getElementById("compute").addEventListener("click", async function() { await getTwinWidth(cyLeft, "tw1"); await getTwinWidth(cyRight, "tw2"); await getSimilarity();});

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
cyLeft.on('cxttap', 'node', function(evt) {let node = evt.target; deleteObject(node);});
cyRight.on('cxttap', 'node', function(evt) {let node = evt.target; deleteObject(node);});
cyLeft.on('cxttap', 'edge', function(evt) {let edge = evt.target; deleteObject(edge);});
cyRight.on('cxttap', 'edge', function(evt) {let edge = evt.target; deleteObject(edge);});