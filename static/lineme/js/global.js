/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/6/6
 * Time: 20:13
 */

//$('#info-panel').find('.box-body').on('mousewheel', function ( e ) {
//    var event = e.originalEvent,
//        d = event.wheelDelta || -event.detail;
//    //console.logs('wheel');
//    this.scrollTop += ( d < 0 ? 1 : -1 ) * 30;
//    e.preventDefault();
//});

$('#normal-mode').mouseover(function(){
    $(this).text('MAP MODE');
}).mouseout(function(){
    $(this).text('NORMAL MODE');
}).click(function(){
    $('#network').hide();
    $('#map').fadeIn().show();
    $(this).hide();
    $('#map-mode').show();
});
$('#map-mode').mouseover(function(){
    $(this).text('NORMAL MODE');
}).mouseout(function(){
    $(this).text('MAP MODE');
}).click(function(){
    $('#map').hide();
    $('#network').fadeIn().show();
    $(this).hide();
    $('#normal-mode').show();
});


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


var node, link, nodes, links, self;
var linkedIndex = {};

var defs = vis.append("defs").attr("id", "imgdefs");
//d3.json("/static/data/miserables.json", function(error, graph) {
d3.json("/ggraph/"+groupid+"/", function(error, graph) {
    if (error) {
        alert("Network error");
        throw error;
    }

    if (graph.nodes == null) return;

    nodes = graph.nodes;
    links = graph.links;

    //console.logs(nodes);
    //console.logs(links);

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
        .attr("class", function(d){
           if(d.status) return "link link-created";
           else return "link link-unconfirmed";
        });

    node = node.data(nodes, function(d){return d.id;});
    node.enter().append("g")
        .attr("class", "node")
        .attr("r", 25)
        .style("fill", function(d) { return color(d.group); })
        .style("stroke", function(d) { return color(d.group); })
        .on("mouseout", nodeMouseout)
        .on("mouseover", nodeMouseover)
        .call(drag);

    node.append("circle")
        .attr("r", 25);

    node.append("image")
        .attr('x', -25)
        .attr('y', -25)
        .attr('width', 50)
        .attr('height', 50)
        .attr("xlink:href", function(d) {
            if (d.userid != -1)
                return "/static/images/user_avatars/"+ d.userid+".png"
        })
        .attr("clip-path", "url(#clip-circle)");


    force.start();

}


function nodeMouseover(d, i) {
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
    //tip.style()
    tip.attr('class', 'd3-tip').show(d);
    tip.hide();
    node.style("stroke", function(n) { return color(n.group); });
    link.classed("link-selected", false);

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




var myChart = echarts.init(document.getElementById('info-degree'), 'roma');

disData = $.map(disData, function(value, key){
    return [[parseInt(key), value]]
});


var option = {
    title: {
        text: 'Degree Distribution',
        x: 'center'

    },
    tooltip: {
        padding: 8,
        borderColor: '#777',
        borderWidth: 1,

        formatter: function(obj) {
            return 'k : '+obj.value[0]+'</br>P(k) : '+obj.value[1].toFixed(2);
        }
    },

    xAxis: {
        name: 'k'
    },
    yAxis: {
        name: 'P(k)'
    },
    series: [{
        name: 'Degree',
        type: 'scatter',
        data: disData,
        symbolSize: 12
    }]
};
myChart.setOption(option);

$('#map').width(width).height(height);

var myMap = echarts.init(document.getElementById('map'), 'roma');

$.get("/gmap/"+groupid+"/", function(result){

    //console.logs(result.nodes);
    //console.logs(result.links);
    var option2 = {
        backgroundColor: '#404a59',

        tooltip : {
            trigger: 'item',
            padding: 10,
            borderColor: '#777',
            borderWidth: 1,
            formatter : function(obj){
                //console.logs(obj);
                if(obj.dataType == 'node' || obj.dataType == undefined)
                    return '<div style="border-bottom: 1px solid rgba(255,255,255,.3); font-size: 16px;padding-bottom: 7px;margin-bottom: 7px">'+obj.name+'</div>'+'Total : '+obj.value[2]+"</br>Friends : "+obj.value[3];
            }
        },

        geo: {
            map: 'china',
            label: {
                emphasis: {
                    show: false
                }
            },
            zoom: 1.2,
            roam: true,
            itemStyle: {
                normal: {
                    areaColor: '#323c48',
                    borderColor: '#111'
                },
                emphasis: {
                    areaColor: '#2a333d'
                }
            }
        },
        series : [
            {
                name: 'city',
                type: 'graph',
                coordinateSystem: 'geo',
                //data: convertData(data),
                data: result.nodes,
                //symbolSize: function (val) {
                //    return val[2] / 10;
                //},
                symbolSize: 20,
                label: {
                    emphasis : {
                        show: false
                    }
                },
                links: result.links,
                lineStyle: {
                    normal: {
                        opacity: 0.8,
                        width: 1.8,
                        curveness: 0.08,
                    },
                },
                itemStyle: {
                    normal: {
                        opacity: 0.8,
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowOffsetY: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)',
                        color: function(obj){
                            if(obj.value[3] == 0) return '#80F1BE';
                            else return '#61C0DE';
                        }
                    }
                }
            },
            {
                name: 'Hometown',
                type: 'effectScatter',
                coordinateSystem: 'geo',
                data: result.nodes.filter(function (d) {
                    return d.self == true;
                }),
                symbolSize: 35,
                showEffectOn: 'render',
                rippleEffect: {
                    brushType: 'stroke'
                },
                hoverAnimation: true,
                label: {
                    normal: {
                        formatter: 'Me',
                        position: 'right',
                        show: true,
                        textStyle: {
                            fontSize: 15
                        }
                    }
                },
                itemStyle: {
                    normal: {
                        color: '#f4e925',
                        opacity: 0.9,
                        shadowBlur: 30,
                        shadowOffsetX: 0,
                        shadowOffsetY: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)',
                    }
                },
                zlevel: 1
            }
        ]
    };

    myMap.setOption(option2);
});

