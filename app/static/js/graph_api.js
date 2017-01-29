

function SvgGraph () {
    // Constructor instantiating img
    console.log("Constructor");
    this.svg = d3.select("#graph"),
    this.width = +this.svg.attr("width"),
    this.height = +this.svg.attr("height");
    this.color = d3.scaleOrdinal(d3.schemeCategory10);
    this.url1 =  "/graph_data";
    this.simulation = d3.forceSimulation()
      .force("link", d3.forceLink().id(function(d) { return d.id; }))
      .force("charge", d3.forceManyBody()  )
      .force("center", d3.forceCenter(this.width / 2, this.height / 2));
}

SvgGraph.prototype.gen_graph = function(){
  // generating graph from instantiated image
  console.log("IN");
  var $this = this;
  $.getJSON(this.url1).done([function(graph) {
    console.log("ping");
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
        .attr("r", 12)
        .attr("fill", function(d) { return $this.color(d.group); })
        .call(d3.drag()
            .on("start", $this.dragstarted.bind($this))
            .on("drag", $this.dragged)
            .on("end", $this.dragended.bind($this)))
            .on("click", function(d) {
              console.log( d);
              var url = d.url;
              // window.location.replace(url);
              document.getElementById("content").style.display = "block";
              document.getElementById("content").innerHTML = d.snippet + "\n"  + url;
              console.log( "click");
            });

      $this.simulation
          .nodes(graph.nodes)
          .on("tick", ticked);

    
      $this.simulation.force("link")
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
      var ii = false;
      setInterval(function(){
            // console.log("kkkekk");
             var circ = document.getElementsByTagName("circle");
          // console.log(circ[0]);
          if(ii==true){
            var text = $this.svg.selectAll("text")
                        .remove();

          }
          else{
            ii = true;
          }
          var text = $this.svg.selectAll("text")
                            .data(circ)
                            .enter()
                            .append("text");

          var textLabels = text
                .attr("x", function(d) { return d.getAttribute("cx"); })
                .attr("y", function(d) { return d.getAttribute("cy"); })
                .text( function (d,i) { return graph.nodes[i].id; })
                .attr("font-family", "sans-serif")
                .attr("font-size", "10px")
                .attr("fill", "white");
      }, 100)
  }]);
}

SvgGraph.prototype.dragstarted = function (d) {
  if (!d3.event.active) this.simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

SvgGraph.prototype.dragged =  function(d) {
  // helper static method
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

SvgGraph.prototype.dragended = function (d) {
  if (!d3.event.active) this.simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}

SvgGraph.prototype.search = function(){
  $this.svg.append("g").remove();
  console.log(document.getDocumentElementById("searcher"));
}