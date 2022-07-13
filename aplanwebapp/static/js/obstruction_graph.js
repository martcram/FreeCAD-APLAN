class ObstructionGraph {
    constructor(fileLocation) {
        var fileLocation = fileLocation;
    }

    run() {
        d3.json("/aplan/config_params", function (jsonData) {
            const params = jsonData;

            var width = window.innerWidth,
                height = window.innerHeight;

            var i = 0;
            var firstSelectedNode = null;
            var secondSelectedNode = null;
            var nodeSelected = false;

            var scale = parseFloat(params.force_simulation.init_scale);
            var tx = -width / 2 * scale + width / 2,
                ty = -height / 2 * scale + height / 2;

            var svg = d3.select("div#container")
                .append("div")
                .classed("svg-container", true)
                .append("svg")
                .attr("viewBox", `${-width / 2} ${-height / 2} ${width * 2} ${height * 2}`)
                .classed("svg-content-responsive", true)
                .on('wheel.zoom', zoom)
                .append('g')
                .attr('transform', `translate(${tx}, ${ty}) scale(${scale})`);

            svg.append('defs').append('marker')
                .attr('id', 'arrowHead')
                .attr('viewBox', '-0 -5 10 10')
                .attr('refX', params.arrow_head.default.ref_x)
                .attr('refY', params.arrow_head.default.ref_y)
                .attr('orient', 'auto')
                .attr('markerWidth', params.arrow_head.default.marker_width)
                .attr('markerHeight', params.arrow_head.default.marker_height)
                .attr('xoverflow', 'visible')
                .append('svg:path')
                .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
                .attr('fill', params.arrow_head.default.fill)
                .style('stroke', 'none');

            svg.append('defs').append('marker')
                .attr('id', 'highlightedArrowHead')
                .attr('viewBox', '-0 -5 10 10')
                .attr('refX', params.arrow_head.highlight.ref_x)
                .attr('refY', params.arrow_head.highlight.ref_y)
                .attr('orient', 'auto')
                .attr('markerWidth', params.arrow_head.highlight.marker_width)
                .attr('markerHeight', params.arrow_head.highlight.marker_height)
                .attr('xoverflow', 'visible')
                .append('svg:path')
                .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
                .attr('fill', params.arrow_head.highlight.fill)
                .style('stroke', 'none');

            svg.append('defs').append('marker')
                .attr('id', 'selectedArrowHead')
                .attr('viewBox', '-0 -5 10 10')
                .attr('refX', params.arrow_head.select.ref_x)
                .attr('refY', params.arrow_head.select.ref_y)
                .attr('orient', 'auto')
                .attr('markerWidth', params.arrow_head.select.marker_width)
                .attr('markerHeight', params.arrow_head.select.marker_height)
                .attr('xoverflow', 'visible')
                .append('svg:path')
                .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
                .attr('fill', params.arrow_head.select.fill)
                .style('stroke', 'none');

            var force = d3.layout.force()
                .gravity(params.force_simulation.gravity)
                .distance(params.force_simulation.distance)
                .charge(params.force_simulation.charge)
                .size([width, height])
                .on("tick", tick);

            var adjacentNodesDict = {};
            var adjacentLinksDict = {};
            var nodes = null;
            var links = null;

            d3.json(`/aplan/obstruction_graph/js?fileLoc=${fileLocation}`, function (json) {
                let data = preprocessData(json);
                nodes = data.nodes;
                links = data.links;
                adjacentNodesDict = data.adjacentNodesDict;
                adjacentLinksDict = data.adjacentLinksDict;

                force
                    .nodes(nodes)
                    .links(links)
                    .start();

                var link = svg.selectAll(".link")
                    .data(links)
                    .enter().append("line")
                    .attr("class", "link")
                    .attr('marker-end', `url(#${params.link.default.marker_end})`)
                    .on("click", clickLink)
                    .on("mouseover", hoverLink)
                    .on("mouseout", function () {
                        defaultLinks(links);
                    });

                var node = svg.selectAll(".node")
                    .data(nodes)
                    .enter().append("g")
                    .attr("class", "node")
                    .attr("id", function (n) {
                        return n.id || (n.id = i++);
                    })
                    .on("click", function (n) {
                        if (d3.event.ctrlKey) {
                            ctrlClickNode(n);
                        }
                    })
                    .on("mouseover", hoverNode)
                    .on("mouseout", function () {
                        let selectedNodes = [firstSelectedNode, secondSelectedNode];
                        let unselectedNodes = nodes.filter(n => !selectedNodes.includes(n));
                        defaultNodes(unselectedNodes);
                        defaultLinks(links);
                    })
                    .call(force.drag);

                node.append("circle")
                    .attr("r", params.node.default.radius);

                node.append("text")
                    .attr("dx", params.label.default.dx)
                    .attr("dy", params.label.default.dy)
                    .text(function (n) { return n.name });
                
                restart();
            });

            function preprocessData(json) {
                let nodes = json.nodes;
                let links = json.links;

                let nodeNameIdMapping = {};
                let adjacentNodesDict = {};
                let adjacentLinksDict = {};
                nodes.forEach(function (node, id) {
                    nodeNameIdMapping[node.name] = id;
                    adjacentNodesDict[node.name] = [];
                    adjacentLinksDict[node.name] = [];
                });

                let processedLinks = [];
                links.forEach(function (link) {
                    let processedLink = {
                        source: nodeNameIdMapping[link.source],
                        target: nodeNameIdMapping[link.target]
                    };
                    let linkExists = processedLinks.some(link => (JSON.stringify(processedLink) === JSON.stringify(link)));
                    if (!linkExists) {
                        processedLinks.push(processedLink);
                        let adjacentNodesSource = adjacentNodesDict[link.source];
                        if (!adjacentNodesSource.includes(link.target)) {
                            adjacentNodesDict[link.source].push(link.target);
                            adjacentLinksDict[link.source].push(link);
                        }
                    }
                });

                return {
                    nodes: nodes,
                    links: processedLinks,
                    adjacentNodesDict: adjacentNodesDict,
                    adjacentLinksDict: adjacentLinksDict
                };
            }

            // source: https://gist.github.com/KarolAltamirano/b54c263184be0516a59d6baf7f053f3e
            function zoom() {
                // prevent default event behaviour
                d3.event.preventDefault();

                // set zooming
                var factor = 1.1;
                var center = d3.mouse(document.querySelector('svg'));
                var newTx, newTy, newScale;

                // calculate new scale
                if (d3.event.deltaY < 0) {
                    newScale = scale * factor;
                } else {
                    newScale = scale / factor;
                }

                // calculate new translate position
                // [current mouse position] = ([current mouse position] - [current translate]) * magnification
                newTx = center[0] - (center[0] - tx) * newScale / scale;
                newTy = center[1] - (center[1] - ty) * newScale / scale;

                // set new scale and translate position
                scale = newScale;
                tx = newTx;
                ty = newTy;

                svg.attr('transform', `translate(${tx}, ${ty}) scale(${scale})`);
            }

            function clickLink(link, i) {
                defaultNodes(nodes);
                defaultLinks(links);

                links.splice(i, 1);

                adjacentNodesDict[link.source.name] = adjacentNodesDict[link.source.name].filter(n => (n != link.target.name));
                adjacentLinksDict[link.source.name] = adjacentLinksDict[link.source.name].filter(l => !(l.source === link.source.name && l.target === link.target.name));

                restart();
            }

            function hoverNode(node, _) {
                if (!nodeSelected) {
                    let highlightedNodes = adjacentNodesDict[node.name].map((x) => x); // shallow copy
                    postSelectedObstructions(node.name, adjacentNodesDict[node.name]);

                    highlightedNodes.push(node.name); // also highlight the selected node
                    let highlightedLinks = adjacentLinksDict[node.name];

                    fetch("/aplan/animations")
                        .then((response) => {
                            return response.json();
                        })
                        .then(data => {
                            if (data.enabled === "True") {
                                highlightNodes(highlightedNodes);
                                highlightLinks(highlightedLinks);
                            }
                        });
                }
            }

            function hoverLink(l, _) {
                selectLinks([l]);
            }

            function ctrlClickNode(n) {
                if (firstSelectedNode != null && n.id == firstSelectedNode.id) {
                    firstSelectedNode = null;
                    defaultNodes([firstSelectedNode]);
                    nodeSelected = false;
                } else if (firstSelectedNode == null && secondSelectedNode == null) {
                    firstSelectedNode = n;
                    selectNodes([firstSelectedNode]);
                    nodeSelected = true;
                } else if (firstSelectedNode != null && n.id != firstSelectedNode.id && secondSelectedNode == null) {
                    secondSelectedNode = n;
                    let newLink = {
                        source: firstSelectedNode,
                        target: secondSelectedNode
                    };
                    let linkExist = false;
                    links.forEach(function (l) {
                        if (l.source == newLink.source && l.target == newLink.target) {
                            linkExist = true;
                        }
                    });
                    if (!linkExist) {
                        links.push(newLink);
                        let newLinkNames = {
                            source: newLink.source.name,
                            target: newLink.target.name
                        };
                        adjacentNodesDict[newLink.source.name].push(newLink.target.name);
                        adjacentLinksDict[newLink.source.name].push(newLinkNames);
                        restart();
                    }
                    selectNodes([firstSelectedNode, secondSelectedNode]);
                    nodeSelected = false;
                    firstSelectedNode = null;
                    secondSelectedNode = null;
                }
                defaultLinks(links);
            }

            function selectNodes(nodeList) {
                d3.selectAll('.node')
                    .each(function (n) {
                        if (nodeList.includes(n)) {
                            d3.select(this).select("circle")
                                .style("stroke", params.node.select.colour)
                                .style("stroke-width", params.node.select.stroke_width)
                                .style("stroke-opacity", params.node.select.stroke_opacity);
                            d3.select(this).select("text")
                                .style("fill", params.label.select.colour)
                                .style("font-weight", params.label.select.font_weight)
                                .style("opacity", params.label.select.opacity);
                        }
                        let unselectedNodes = nodes.filter(n => !nodeList.includes(n));
                        defaultNodes(unselectedNodes);
                    });
            }

            function selectLinks(linkList) {
                d3.selectAll('.link')
                    .each(function (l) {
                        if (linkList.includes(l)) {
                            d3.select(this)
                                .style("stroke", params.link.select.colour)
                                .style("stroke-width", params.link.select.width)
                                .attr('marker-end', `url(#${params.link.select.marker_end})`);
                        }
                        let unselectedLinks = links.filter(l => !linkList.includes(l));
                        defaultLinks(unselectedLinks);
                    });
            }

            function highlightNodes(nodeList) {
                d3.selectAll('.node')
                    .each(function (node) {
                        if (nodeList.includes(node.name)) {
                            d3.select(this).select("circle")
                                .style("stroke", params.node.highlight.colour)
                                .style("stroke-width", params.node.highlight.stroke_width)
                                .style("stroke-opacity", params.node.highlight.stroke_opacity);
                            d3.select(this).select("text")
                                .style("fill", params.label.highlight.colour)
                                .style("font-weight", params.label.highlight.font_weight)
                                .style("opacity", params.label.highlight.opacity);
                        } else {
                            d3.select(this).select("circle")
                                .style("stroke", params.node.unhighlight.colour)
                                .style("stroke-width", params.node.unhighlight.stroke_width)
                                .style("stroke-opacity", params.node.unhighlight.stroke_opacity);
                            d3.select(this).select("text")
                                .style("fill", params.label.unhighlight.colour)
                                .style("font-weight", params.label.unhighlight.font_weight)
                                .style("opacity", params.label.unhighlight.opacity);
                        }
                    });
            }

            function highlightLinks(linkList) {
                d3.selectAll('.link')
                    .each(function (link) {
                        let containsLink = linkList.some(l => l.source === link.source.name && l.target === link.target.name);
                        if (containsLink) {
                            d3.select(this)
                                .style("stroke", params.link.highlight.colour)
                                .style("stroke-width", params.link.highlight.width)
                                .style("opacity", params.link.highlight.opacity)
                                .attr('marker-end', `url(#${params.link.highlight.marker_end})`);
                        } else {
                            d3.select(this)
                                .style("stroke", params.link.unhighlight.colour)
                                .style("stroke-width", params.link.unhighlight.width)
                                .style("opacity", params.link.unhighlight.opacity)
                                .attr('marker-end', `url(#${params.link.unhighlight.marker_end})`);
                        }
                    });
            }

            function defaultNodes(nodeList) {
                d3.selectAll('.node')
                    .each(function (n) {
                        if (nodeList.includes(n)) {
                            d3.select(this).select("circle")
                                .style("stroke", params.node.default.colour)
                                .style("stroke-width", params.node.default.stroke_width)
                                .style("stroke-opacity", params.node.default.stroke_opacity);
                            d3.select(this).select("text")
                                .style("fill", params.label.default.colour)
                                .style("font-weight", params.label.default.font_weight)
                                .style("opacity", params.label.default.opacity);
                        }
                    });
            }

            function defaultLinks(linkList) {
                d3.selectAll('.link')
                    .each(function (l) {
                        if (linkList.includes(l)) {
                            d3.select(this)
                                .style("stroke", params.link.default.colour)
                                .style("stroke-width", params.link.default.width)
                                .style("opacity", params.link.default.opacity)
                                .attr('marker-end', `url(#${params.link.default.marker_end})`);
                        }
                    });
            }

            function tick() {
                svg.selectAll(".link")
                    .attr("x1", function (l) { return l.source.x; })
                    .attr("y1", function (l) { return l.source.y; })
                    .attr("x2", function (l) { return l.target.x; })
                    .attr("y2", function (l) { return l.target.y; });

                svg.selectAll(".node")
                    .attr("transform", function (n) { return "translate(" + n.x + "," + n.y + ")"; });
            }

            function postObstructionGraph() {
                let processedGraph = {
                    nodes: [],
                    links: []
                }

                nodes.forEach(function (node) {
                    processedGraph.nodes.push({ name: node.name });
                });

                links.forEach(function (link) {
                    processedGraph.links.push({
                        source: link.source.name,
                        target: link.target.name
                    });
                });

                fetch("/aplan/obstruction_graph/js", {
                    method: "POST",
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(processedGraph)
                });
            }

            function postSelectedObstructions(source, targets) {
                fetch("/aplan/obstruction_graph/selected_obstructions", {
                    method: "POST",
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        source: source,
                        targets: targets
                    })
                });
            }

            function restart() {
                var link = svg.selectAll(".link").data(links);

                link.enter().insert("line", ".node")
                    .attr("class", "link")
                    .attr('marker-end', `url(#${params.link.default.marker_end})`)
                    .on("click", clickLink)
                    .on("mouseover", hoverLink)
                    .on("mouseout", function () {
                        defaultLinks(links);
                    });

                link.exit()
                    .remove();

                postObstructionGraph();
                
                force.start();
            }
        });
    }
}