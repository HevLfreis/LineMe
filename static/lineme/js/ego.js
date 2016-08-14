/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/5/4
 * Time: 14:29
 */

// Todo: check
$(function() {
    //setTimeout(function () {$('.panel-text-bottom').fadeOut(500);}, 2000);

    $('.modal').on('show.bs.modal', function(e) {
        var $dialog = $(this).find('.modal-dialog');
        $dialog.css({
            'margin-top': function() {
                var modalHeight = $dialog.height();
                return ($(window).height() / 6 - (modalHeight / 2));
            }
        });
    });

    /**
        rcmd panel
     */

    var rcmdAddedNode = {};

    window.updateRcmdPanel = function(page) {

        $.get(rcmdUrl+'?page='+page, function(data) {
            $('#rcmd-panel').html(data);

            $('#refresh').click(function() {
                updateRcmdPanel(1);
            });

            $('.widget-user-2')
                .addClass(function(){
                    if (rcmdAddedNode[rcmdId2Node($(this).attr("id")).id]) return "bg-gray";
                    else return "bg-gray-light";
                });

            // if the item bg is gray-light, meaning the member is not in the graph
            // we bind click event to this item
            //
            $('.widget-user-2.bg-gray-light')
                .mouseover(function(){
                    $(this).removeClass("bg-gray-light").addClass("bg-gray");
                })
                .mouseout(function(){
                    $(this).removeClass("bg-gray").addClass("bg-gray-light");
                })
                .click(function(){

                    var newNode = rcmdId2Node($(this).attr("id"));

                    if (!nodeInGraph(newNode, nodes)) {
                        nodes.push(newNode);
                        rcmdAddedNode[newNode.id] = true;
                        $(this).removeClass("bg-gray-light")
                            .addClass("bg-gray")
                            .off('mouseout')
                            .off('mouseover')
                            .off('click');
                        start();
                    }
                });
        });
    };

    function rcmdId2Node(id) {
        var ids = id.split('-');
        return {group: Math.floor(Math.random() * 10) + 1,
            name: ids[3],
            userid: ids[2] == ''? -1: parseInt(ids[2]),
            id: parseInt(ids[1]),
            creator: false}
    }

    function nodeInGraph(node, nodes) {

        var res = false;
        $.each(nodes, function() {
            if (node.id === this.id && node.name === this.name) {
                res = res || true;
            }
        });

        return res;
    }

    updateRcmdPanel(1);


    /**
        d3 graph
     */

    var tip = d3.tip()
        .attr({'class': 'd3-tip'})
        .html(function(d) {
            if(d.self) return '<span> Me </span>';
            else return '<span>' + d.name + '</span>';
        })
        .direction('e').offset([0, -20]);

    var mp = $("#main-panel");
    var width = mp.width(),
        height = mp.height();

    var xScale = d3.scale.linear()
        .domain([0,width]).range([0,width]);
    var yScale = d3.scale.linear()
        .domain([0,height]).range([0, height]);

    var charge = -800;

    var color = d3.scale.category10();
    //var color = function(i){
    //    var c = ['#3498db','#1abc9c','#f1c40f','#9588b2','#ec7063','#9cc2cb','#af7ac5','#f39c12','#95a5a6'];
    //    return c[i%c.length]
    //};


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
        //.on("mouseover", function(d){
        //    return d3.select(this).call(zoomer);
        //})
        //.on("mouseout", function(d){
        //    return d3.select(this).on(".zoom", null);
        //})
        .call(zoomer)
        .on("dblclick.zoom", null);


    function redraw() {
        var scale = d3.event.scale;
        d3.event.sourceEvent.stopPropagation();
        if (scale > 1)
            force.charge(charge* scale*3).start();
        else
            force.charge(charge* scale).start();

        vis.attr("transform",
            "translate(" + d3.event.translate + ")" + " scale(" + scale + ")");

        tip.style({
            "height": 50*scale+'px',
            "font-size": 20*scale+'px',
            "padding": 14*scale+'px '+15*scale+'px '+15*scale+'px '+30*scale+'px'
        });
        tip.offset([0, -20*scale]);

    }

    var vis = svg.append("svg:g");

    vis.attr('fill', 'red')
        .attr('stroke', 'black')
        .attr('stroke-width', 1)
        .attr('id', 'vis')
        .call(tip);


    var node, link, nodes, links, self, nodesCopy, linksCopy;
    var linkedIndex = {}, linkedIndexCopy = {};

    var defs = vis.append("defs").attr("id", "imgdefs");
    //d3.json("/static/data/miserables.json", function(error, graph) {
    d3.json(eGraphUrl, function(error, graph) {
        if (error) {
            alert("Server Internal Error");
            throw error;
        }

        if (graph.nodes == null) return;

        nodes = graph.nodes;
        links = graph.links;

        nodesCopy = nodes.slice(0);
        linksCopy = links.slice(0);

        //console.logs(nodes);
        //console.logs(links);

        var nodeById = d3.map();

        nodes.forEach(function(node) {
            nodeById.set(node.id, node);
            if (node.self) self = node;

            //rcmdAddedNode[node.id] = true;
        });

        links.forEach(function(link) {
            link.source = nodeById.get(link.source);
            link.target = nodeById.get(link.target);
        });

        links.forEach(function(d) {
            linkedIndex[d.source.id + "," + d.target.id] = true;
        });

        linkedIndexCopy = $.extend({}, linkedIndex);


        //console.logs(graph.nodes);
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
            .attr("class",  function(d) {
                if(d.status == 3) return "link";
                else if(d.status == 4) return "link link-created";
                else if(d.status >= 0) return "link link-unconfirmed";
                else if(d.status < 0) return "link link-rejected";
            })
            .on("click", linkClick)
            .on("mouseout", linkMouseout)
            .on("mouseover", linkMouseover);

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
                    return "/static/images/avatars/"+ d.userid+".png"
            })
            .attr("clip-path", "url(#clip-circle)");

        //updateNodes.append("title")
        //    .text(function(d) { return d.name; });

        force.start();

    }


    function linkClick(d){
        if (selected) return;
        linkedIndex[d.source.id + "," + d.target.id] = false;
        //console.logs(links);
        links = links.filter(function(a) {
            return a.source.id + "," + a.target.id !== d.source.id + "," + d.target.id;
        });
        start();
    }

    var selected;
    function nodeClick(d){

        // prevent drag click
        if (d3.event.defaultPrevented) return;
        //console.log('Node click: ', d.name);
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
                //console.logs('New link:', selected, d);
                linkedIndex[selected.id + "," + d.id] = true;
                links.push({"source": selected, "target": d, "value": 1, "status": 4});
                start();
            }

            node.style("stroke", function(n) { return color(n.group); });
            link.classed("link-selected", false);
            selected = null;
        }
    }

    function nodeDbclick(d, i){
        //console.logs('Node dbclick: ', d.name, i);
        if (d == self) return;
        //console.logs(nodes);
        links = links.filter(function(a){
            if (d === a.source||d === a.target)
                linkedIndex[a.source.id + "," + a.target.id] = false;
            return d !== a.source&&d !== a.target;
        });

        nodes = nodes.filter(function(a) { return a !== d ;});

        rcmdAddedNode[d.id] = false;

        //console.logs(nodes);
        selected = null;
        start();
    }

    function nodeMouseover(d, i) {
        if (selected) return;
        //console.logs(d);
        tip.attr('class', 'd3-tip animate').show(d);
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
        //tip.style()
        tip.attr('class', 'd3-tip').show(d);
        tip.hide();
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
        //console.logs('drag start');
        d3.event.sourceEvent.stopPropagation();
    }

    function dragged(d) {
        d3.select(this).attr("cx", d.x = d3.event.x).attr("cy", d.y = d3.event.y);
    }

    function dragended(d) {
        d3.select(this).classed("dragging", false);
    }


    //function resetMenu() {
    //    var menu = document.getElementById( 'bt-menu' );
    //    classie.remove( menu, 'bt-menu-open' );
    //    classie.add( menu, 'bt-menu-close' );
    //}

    $('#submit').click(function() {

        var data = JSON.stringify(links.map(function(a){
            return {"source":a.source.id.toString(), "target":a.target.id.toString()};
        }));

        $.ajax({
            type: "POST",
            data: { links: data },
            url: updateGraphUrl,
            success: function(msg) {
                nodesCopy = nodes.slice(0);
                linksCopy = links.slice(0);
                linkedIndexCopy = $.extend({}, linkedIndex);

                if (msg == 0) $('#modal-success').modal('show');
                else alert("Update Failed");
                updateRcmdPanel(1);
                resetMenu();
            },
            error: function() {
                alert("Update Failed");
            }
        });
    });

    $('#lineme').click(function() {

        nodes.forEach(function(node) {
            if (node != self  && (!linkedIndex[self.id + "," + node.id]
                && !linkedIndex[node.id + "," + self.id])) {
                links.push({"source" : self, "target": node, "value": 1, "status": 4});
                linkedIndex[self.id + "," + node.id] = true;
            }
        });

        start();
        resetMenu();
    });

    $('#reset').click(function() {

        nodes = nodesCopy.slice(0);
        links = linksCopy.slice(0);
        linkedIndex = $.extend({}, linkedIndexCopy);

        start();
        rcmdAddedNode = {};
        updateRcmdPanel(1);
        resetMenu();
    });


    // Todo: implement clear
    $('#clear').click(function() {

        links = [];
        linkedIndex = {};

        start();
        resetMenu();

    });

    $('#search').autocomplete({
        type: 'member',
        groupid: groupid,
        onclick: function(d) {

            var id = $(d).attr("id"),
                nid = 'sug-'+id.substring(4, id.length),
                newNode = rcmdId2Node(id);


            if (!nodeInGraph(newNode, nodes)) {
                nodes.push(newNode);
                rcmdAddedNode[newNode.id] = true;
                //console.log("[id='"+nid+"']");
                $("[id='"+nid+"']").removeClass("bg-gray-light")
                    .addClass("bg-gray")
                    .off('mouseout')
                    .off('mouseover')
                    .off('click');
                start();
            }
        }
    });

});
