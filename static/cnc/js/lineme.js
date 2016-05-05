/**
* Created with PyCharm.
* User: Freeeeeeeee
* Date: 2016/5/4
* Time: 14:29
*/

var sugNodeAdded = {};

function updateSugPanel(page) {

    $.get("/cnc/sugmember/"+groupid+"/"+page, function(data) {
        $('#sug-panel').html(data);

        $('#refresh').click(function() {
            updateSugPanel(1);
        });

        $('.widget-user-2')
            .addClass(function(){
                if (sugNodeAdded[sugId2Node($(this).attr("id")).id]) return "bg-gray";
                else return "bg-gray-light";
            });
        $('.widget-user-2.bg-gray-light')
            .mouseover(function(){
                $(this).removeClass("bg-gray-light").addClass("bg-gray");
            })
            .mouseout(function(){
                $(this).removeClass("bg-gray").addClass("bg-gray-light");
            })
            .click(function(){

                //后台一定要检测新node的正确性！！！！！！！！！！！！！！！

                var newNode = sugId2Node($(this).attr("id"));

                if (!sugNodeAdded[newNode.id]) {
                    nodes.push(newNode);
                    sugNodeAdded[newNode.id] = true;
                    $(this).removeClass("bg-gray-light").addClass("bg-gray").off('mouseout').off('mouseover');
                    start();
                }


            });

    });
}

function sugId2Node(id) {
    var ids = id.split('-');
    return {group: Math.floor(Math.random() * 10) + 1, name: ids[3], userid: ids[2] == ''? -1: parseInt(ids[2]), id: ids[1], creator: false}
}

updateSugPanel(1);


var width = $("#main-panel").width(),
    height = $("#main-panel").height();

var xScale = d3.scale.linear()
    .domain([0,width]).range([0,width]);
var yScale = d3.scale.linear()
    .domain([0,height]).range([0, height]);

var charge = -800;
var color = d3.scale.category10();


var zoomer = d3.behavior.zoom()
    .scaleExtent([0.1,10])
    .x(xScale)
    .y(yScale)
    .on("zoom", redraw);


var force = d3.layout.force()
    .charge(charge)
    .linkDistance(200)

    .size([width, height]);

var drag = force.drag()
    .origin(function(d) { return d; })
    .on("dragstart", dragstarted)
    .on("drag", dragged)
    .on("dragend", dragended);


var svg = d3.select("#network").append("svg")
    .attr("width", width)
    .attr("height", height)
    .call(zoomer)
    .on("dblclick.zoom", null);


function redraw() {
    if (d3.event.scale > 1)
        force.charge(charge* d3.event.scale*3).start();
    else
        force.charge(charge* d3.event.scale).start();
    vis.attr("transform",
        "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")");
}


var vis = svg.append("svg:g");

vis.attr('fill', 'red')
    .attr('stroke', 'black')
    .attr('stroke-width', 1)
    .attr('id', 'vis');


var node, link, nodes, links, self, nodesCopy, linksCopy;
var linkedIndex = {};

var defs = vis.append("defs").attr("id", "imgdefs");
//d3.json("/static/data/miserables.json", function(error, graph) {
d3.json("/cnc/graph/"+groupid+"/", function(error, graph) {
    if (error) {
        alert("Network error");
        throw error;
    }

    if (graph.nodes == null) return;

    nodes = graph.nodes;
    links = graph.links;

    nodesCopy = nodes.slice(0);
    linksCopy = links.slice(0);

    //console.log(nodes);
    //console.log(links);

    var nodeById = d3.map();

    nodes.forEach(function(node) {
        nodeById.set(node.id, node);
        if (node.self) self = node;
    });

    links.forEach(function(link) {
        link.source = nodeById.get(link.source);
        link.target = nodeById.get(link.target);
    });

    links.forEach(function(d) {
        linkedIndex[d.source.id + "," + d.target.id] = true;
    });



    //console.log(graph.nodes);
    link = vis.selectAll(".link");
    node = vis.selectAll(".node");
    start();


    var clipPath = defs.append('clipPath').attr('id', 'clip-circle')
        .append("circle")
        .attr("r", 25)
        .attr("cy", 0)
        .attr("cx", 0);


    force.on("tick", function() {
        link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

        node.attr("transform", function(d) {
            return "translate(" + d.x + "," + d.y + ")";
        });


    });

});


function start(){
    force.nodes(nodes)
        .links(links);

    link = link.data(links, function(d){return d.source.id + "," + d.target.id;});
    link.enter().insert("line", ".node")
        .attr("class",  function(d) { return d.status == 3 ? "link":"link link-unconfirmed";})
        .on("click", linkClick)
        .on("mouseout", linkMouseout).on("mouseover", linkMouseover);
    link.exit().remove();

    node = node.data(nodes, function(d){return d.id;});
    node.enter().append("g")
        .attr("class", "node")
        .attr("r", 25)
        .style("fill", function(d) { return color(d.group); })
        .style("stroke", function(d) { return color(d.group); })
        .on("click", nodeClick)
        .on("dblclick", nodeDbclick)
        .on("mouseout", nodeMouseout)
        .on("mouseover", nodeMouseover)

        .call(drag);
    node.exit().remove();

    var updateNodes = node.filter(function(d){
        return d3.select(this).select("circle").empty();
    });

    updateNodes.append("circle")
        .attr("r", 25);

    updateNodes.append("image")
        .attr('x', -25)
        .attr('y', -25)
        .attr('width', 50)
        .attr('height', 50)
        .attr("xlink:href", function(d) {
            if (d.userid != -1)
                return "/static/pic/avatar/"+ d.userid+".png"
        })
        .attr("clip-path", "url(#clip-circle)");

    updateNodes.append("title")
        .text(function(d) { return d.name; });

    force.start();

}


function linkClick(d){
    if (selected) return;
    linkedIndex[d.source.id + "," + d.target.id] = false;
    console.log(links);
    links = links.filter(function(a) { return a.source.id + "," + a.target.id !== d.source.id + "," + d.target.id; });
    start();
}

var selected;
function nodeClick(d){

    if (d3.event.defaultPrevented) return;
    console.log('Node click: ', d.name);
    if(!selected){
        selected = d;
        d3.select(this).style('stroke', '#cd3b23');
    }
    else if (selected&&selected == d) {

        d3.select(this).style('stroke', function(d) { return color(d.group); });
        selected = null;
    }
    else {

        if (!linkedIndex[selected.id + "," + d.id]&&!linkedIndex[d.id + "," + selected.id]&&selected!= d) {
            console.log('New link:', selected, d);
            linkedIndex[selected.id + "," + d.id] = true;
            links.push({"source": selected, "target": d, "value": 1});
            start();
        }

        node.style("stroke", function(n) { return color(n.group); });
        link.classed("link-selected", false);
        selected = null;
    }
}

function nodeDbclick(d, i){
    console.log('Node dbclick: ', d.name, i);
    if (d == self) return;
    console.log(nodes);
    links = links.filter(function(a){
        if (d === a.source||d === a.target)
            linkedIndex[a.source.id + "," + a.target.id] = false;
        return d !== a.source&&d !== a.target;
    });

    nodes = nodes.filter(function(a) { return a !== d ;});

    sugNodeAdded[d.id] = false;

    console.log(nodes);
    selected = null;
    start();
}



function nodeMouseover(d, i) {
    if (selected) return;

    node.style("stroke", function(n) {

        if (linkedIndex[d.id + "," + n.id]||linkedIndex[n.id + "," + d.id])
            return "#38363a";
        else
            return color(n.group);
    });
    d3.select(this).style("stroke","#38363a");
    link.each(function(n) {
        if (n.source.id == d.id || n.target.id == d.id) {
            d3.select(this).classed("link-selected", true);
        }
        else d3.select(this).classed("link-selected", false);
    });
}

function nodeMouseout(d, i) {
    if (selected) return;

    node.style("stroke", function(n) { return color(n.group); });
    link.classed("link-selected", false);

}



function linkMouseover(d) {
    if (selected) return;
    d3.select(this).classed("link-selected", true);
}

function linkMouseout(d) {
    if (selected) return;
    d3.select(this).classed("link-selected", false);
}

function dragstarted(d) {
    //console.log('drag start');
    d3.event.sourceEvent.stopPropagation();
}

function dragged(d) {
    d3.select(this).attr("cx", d.x = d3.event.x).attr("cy", d.y = d3.event.y);
}

function dragended(d) {
    d3.select(this).classed("dragging", false);
}


function resetMenu() {
    var menu = document.getElementById( 'bt-menu' );
    classie.remove( menu, 'bt-menu-open' );
    classie.add( menu, 'bt-menu-close' );
}

$('#submit').click(function() {

    var data = JSON.stringify(links.map(function(a){
        return {"source":a.source.id.toString(), "target":a.target.id.toString()};
    }));

    $.ajax({
        type: "POST",
        data: { links: data },
        url: "/cnc/links/"+groupid+"/",
        success: function(msg){
            nodesCopy = nodes.slice(0);
            linksCopy = links.slice(0);
            alert(msg);
            updateSugPanel(1);
            resetMenu();
        }
    });
});

$('#lineme').click(function() {

    nodes.forEach(function(node) {
        if (node != self  && (!linkedIndex[self.id + "," + node.id]
            && !linkedIndex[node.id + "," + self.id])) {
            links.push({"source" : self, "target": node, "value": 1});
            linkedIndex[self.id + "," + node.id] = true;
        }
    });

    start();
    resetMenu();
});

$('#reset').click(function() {


    nodes = nodesCopy.slice(0);
    links = linksCopy.slice(0);

    start();
    sugNodeAdded = {};
    updateSugPanel(1);
    resetMenu();
});

//}
