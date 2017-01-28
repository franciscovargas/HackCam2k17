

function SvgGraph () {
    this.svg = d3.select("#graph"),
    this.width = +this.svg.attr("width"),
    this.height = +this.svg.attr("height");
    this.color = d3.scaleOrdinal(d3.schemeCategory20);
    this.url1 =  "/graph_data";
}

SvgGraph.prototype.gen_graph = function(){
 
  var simulation = d3.forceSimulation()
      .force("link", d3.forceLink().id(function(d) { return d.id; }))
      .force("charge", d3.forceManyBody())
      .force("center", d3.forceCenter(this.width / 2, this.height / 2));
  console.log(this.svg + "");
  local_svg = this.svg;
  var $this = this;
  $.getJSON(this.url1).done([function(graph) {

    var link = $this.svg.append("g")
        .attr("class", "links")
      .selectAll("line")
      .data(graph.links)
      .enter().append("line")
        .attr("stroke-width", function(d) { return Math.sqrt(d.value); });

    var node = $this.svg.append("g")
        .attr("class", "nodes")
      .selectAll("circle")
      .data(graph.nodes)
      .enter().append("circle")
        .attr("r", 5)
        .attr("fill", function(d) { return $this.color(d.group); })
        .call(d3.drag()
            .on("start", this.dragstarted)
            .on("drag", this.dragged)
            .on("end", this.dragended));

    node.append("title")
        .text(function(d) { return d.id; });

    simulation
        .nodes(graph.nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(graph.links);

    function ticked() {
      link
          .attr("x1", function(d) { return d.source.x; })
          .attr("y1", function(d) { return d.source.y; })
          .attr("x2", function(d) { return d.target.x; })
          .attr("y2", function(d) { return d.target.y; });

      node
          .attr("cx", function(d) { return d.x; })
          .attr("cy", function(d) { return d.y; });
    }
  }]);
}

SvgGraph.prototype.dragstarted = function (d) {
  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

SvgGraph.prototype.dragged =  function(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

SvgGraph.prototype.dragended = function (d) {
  if (!d3.event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}