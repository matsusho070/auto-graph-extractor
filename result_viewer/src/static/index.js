let extractionEditor = null;

let connectorLines = [];

let extractionWidgets = [];
let extractionMarkers = [];

const q = document.querySelector.bind(document);

function clearExtractionHighlights() {
  for (let widget of extractionWidgets) {
    widget.remove();
  }
  extractionWidgets = [];

  for (let marker of extractionMarkers) {
    marker.clear();
  }
  extractionMarkers = [];
}

function setMarginForExtractionWidget(widget) {
  // Set margin to avoid the bounding box of the widget to stick out of the editor
  let parentWidth = widget.parentElement.offsetWidth;
  let widgetWidth = widget.offsetWidth;
  let left = widget.offsetLeft;
  const margin = 10;
  if (parentWidth - left < widgetWidth + margin) {
    widget.style.marginLeft = `${parentWidth - left - widgetWidth - margin}px`;
  }
}

function updatePositionOfConnectorLines() {
  let canvas = document.getElementById("lineCanvas");
  canvas.innerHTML = "";

  for (let connectorLine of connectorLines) {
    let line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    const { from, to } = connectorLine;
    const rect1 = from.getBoundingClientRect();
    const rect2 = to.getBoundingClientRect();
    const parentRect = canvas.getBoundingClientRect();

    const x1 = rect1.left + rect1.width / 2 - parentRect.left;
    const y1 = rect1.top + rect1.height / 2 - parentRect.top;
    const x2 = rect2.left + rect2.width / 2 - parentRect.left;
    const y2 = rect2.top + rect2.height / 2 - parentRect.top;
    line.setAttribute("x1", x1);
    line.setAttribute("y1", y1);
    line.setAttribute("x2", x2);
    line.setAttribute("y2", y2);
    line.setAttribute("strokeWidth", 1);
    line.setAttribute("stroke", "yellow");
    canvas.appendChild(line);
  }
}

function updateExtractedGraph(name) {
  fetch("/graph/" + name, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((graph) => {
      document.getElementById("original-json").textContent = JSON.stringify(
        graph,
        null,
        2
      );
      extractionEditor.setValue(graph.article);
      clearExtractionHighlights();
      const markerMap = {};
      let occupiedRanges = [];
      for (let node of graph.nodes) {
        let cursor = extractionEditor.getSearchCursor(node.original_phrase);
        if (cursor.findNext()) {
          let { line: bubbleStartLine, ch: bubbleStartCh } = cursor.from();
          let overlapped = null;
          while (
            (overlapped = occupiedRanges.find(
              ({ startLine, startCh, text }) =>
                bubbleStartLine === startLine &&
                Math.abs(bubbleStartCh - startCh) < text.length + node.id.length
            ))
          ) {
            bubbleStartCh += overlapped.text.length + node.id.length;
            console.log("Occupied range, moving to", bubbleStartCh);
          }
          extractionMarkers.push(
            extractionEditor.markText(cursor.from(), cursor.to(), {
              className: "extracted-line",
            })
          );
          occupiedRanges.push({
            startLine: bubbleStartLine,
            startCh: bubbleStartCh,
            text: node.id,
          });
          let bubble = document.createElement("div");
          bubble.innerText = node.id;
          bubble.className = "extraction-bubble";
          extractionEditor.addWidget(
            {
              line: bubbleStartLine,
              ch: bubbleStartCh,
            },
            bubble,
            false
          );
          extractionWidgets.push(bubble);
          markerMap[node.id] = bubble;
          setMarginForExtractionWidget(bubble);
        }
      }
      connectorLines = [];
      for (let edge of graph.edges) {
        connectorLines.push({
          from: markerMap[edge.from],
          to: markerMap[edge.to],
        });
      }
      updatePositionOfConnectorLines();
    });
}

window.onload = () => {
  extractionEditor = CodeMirror.fromTextArea(q("#extract-textarea"), {
    viewportMargin: 300,
    theme: "neat",
    lineWrapping: true,
    search: {
      bottom: true,
    },
  });

  q("#graph-select").addEventListener("change", (evt) => {
    updateExtractedGraph(evt.target.value);
  });

  fetch("/graph").then((response) => {
    response.json().then((graphs) => {
      for (let graph of graphs) {
        q("#graph-select").options.add(new Option(graph, graph));
      }
      updateExtractedGraph(graphs[0]);
    });
  });
};

window.addEventListener("resize", updatePositionOfConnectorLines);
window.addEventListener("scroll", updatePositionOfConnectorLines);
