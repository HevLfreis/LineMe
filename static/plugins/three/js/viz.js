(function () {
    var VIZ = {};
    var camera, renderer, scene = new THREE.Scene();
    var $mp = $("#main-panel");
    var width = $mp.width(),
        height = $mp.height(),
        zLookAt = -500;

    camera = new THREE.PerspectiveCamera(20, width / height, 1, 10000);
    camera.position.x = 1200;
    camera.position.y = 750;
    camera.position.z = 1000;
    camera.lookAt(new THREE.Vector3(0, 25, zLookAt));

    VIZ.drawElements = function (datas) {

        VIZ.count = datas.length;

        var margin = {top: 17, right: 0, bottom: 16, left: 20},
            width = 800 - margin.left - margin.right,
            height = 600 - margin.top - margin.bottom,
            radius = 2;

        var color = d3.scale.ordinal()
            .range(['rgb(166,206,227)', 'rgb(31,120,180)', 'rgb(178,223,138)', 'rgb(51,160,44)', 'rgb(251,154,153)', 'rgb(227,26,28)', 'rgb(253,191,111)', 'rgb(255,127,0)']);

        var vis = d3.selectAll(".element").data(datas).enter().append('svg');

        vis.attr('fill', 'red')
            .attr('stroke', 'black')
            .attr('stroke-width', 1)
            .attr('class', 'element')
            .attr("width", width)
            .attr("height", height);

        var defs = vis.append("defs").attr("id", "imgdefs");

        vis.each(function () {
            var force = d3.layout.force()
                .charge(-50)
                .linkDistance(100)
                .size([width, height]);

            var $vis = d3.select(this);

            var node = $vis.selectAll(".node");
            var link = $vis.selectAll(".link");

            var nodes = $vis.datum().nodes;
            var links = $vis.datum().links;

            var nodeById = d3.map();

            nodes.forEach(function (node) {
                nodeById.set(node.id, node);
            });

            links.forEach(function (link) {
                link.source = nodeById.get(link.source);
                link.target = nodeById.get(link.target);
            });

            force.nodes(nodes)
                .links(links);

            link = link.data(links, function (d) {
                return d.source.id + "," + d.target.id;
            });
            link.enter().insert("line", ".node")
                .attr("class", function (d) {
                    return "link-unconfirmed";
                });

            node = node.data(nodes, function (d) {
                return d.id;
            });

            node.enter().append("g")
                .attr("class", "node").attr("r", 10)
                .style("fill", function (d) {
                    return color(d.group);
                })
                .style("stroke", function (d) {
                    return color(d.group);
                });

            node.append("circle")
                .attr("class", "small-circle")
                .attr("r", 10);

            node.append("image")
                .attr('x', -10)
                .attr('y', -10)
                .attr('width', 20)
                .attr('height', 20)
                .attr("xlink:href", function (d) {
                    if (d.userid != -1)
                        return "/media/images/avatars/" + d.userid + ".png"
                })
                .attr("clip-path", "url(#clip-circle2)");

            force.start();

            force.on("tick", function () {
                link.attr("x1", function (d) { return d.source.x; })
                    .attr("y1", function (d) { return d.source.y; })
                    .attr("x2", function (d) { return d.target.x; })
                    .attr("y2", function (d) { return d.target.y; });

                node.attr("transform", function (d) {
                    return "translate(" + d.x + "," + d.y + ")";
                });

                node.attr("cx", function(d) { return d.x = Math.max(radius, Math.min(width - radius, d.x)); })
                    .attr("cy", function(d) { return d.y = Math.max(radius, Math.min(height - radius, d.y)); });

            });

        });

        // clip-circle2 avoid conflict
        var clipPath = defs.append('clipPath').attr('id', 'clip-circle2')
            .append("circle").attr("class", "small-circle")
            .attr("r", 10)
            .attr("cy", 0)
            .attr("cx", 0);

        vis.each(setData);
        vis.each(objectify);
    };

    function objectify(d) {
        var object = new THREE.CSS3DObject(this);
        object.position = d.random.position;
        scene.add(object);
    }

    function setData(d, i) {

        var random = new THREE.Object3D();
        random.position.x = Math.random() * 4000 - 2000;
        random.position.y = Math.random() * 4000 - 2000;
        random.position.z = Math.random() * 4000 - 2000;
        d['random'] = random;

        var flow = new THREE.Object3D();
        flow.position.x = 0;
        flow.position.y = 0;
        flow.position.z = -(Math.floor(i)) * 400;

        d['flow'] = flow;
    }

    VIZ.render = function () {
        renderer.render(scene, camera);
    };

    var prevLayout = 'random';
    VIZ.transform = function (layout) {

        if (prevLayout == layout) return;
        else prevLayout = layout;

        var duration = 1000;

        TWEEN.removeAll();

        scene.children.forEach(function (object) {
            var newPos = object.element.__data__[layout].position;
            var coords = new TWEEN.Tween(object.position)
                .to({x: newPos.x, y: newPos.y, z: newPos.z}, duration)
                .easing(TWEEN.Easing.Sinusoidal.InOut)
                .start();

            var newRot = object.element.__data__[layout].rotation;
            var rotate = new TWEEN.Tween(object.rotation)
                .to({x: newRot.x, y: newRot.y, z: newRot.z}, duration)
                .easing(TWEEN.Easing.Sinusoidal.InOut)
                .start();
        });

        var update = new TWEEN.Tween(this)
            .to({}, duration)
            .onUpdate(VIZ.render)
            .start();
    };

    VIZ.animate = function () {
        requestAnimationFrame(VIZ.animate);
        TWEEN.update();
    };

    renderer = new THREE.CSS3DRenderer();
    renderer.setSize(width, height);
    renderer.domElement.style.position = 'absolute';
    document.getElementById('three').appendChild(renderer.domElement);

    VIZ.onWindowResize = function () {
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
        VIZ.render();
    };
    window.VIZ = VIZ;

    document.getElementById('three').addEventListener('mousewheel', function(event) {

        event.preventDefault();
		event.stopPropagation();

        var delta = 0, p = 0.1, s = 400;

		if (event.wheelDelta) { // WebKit / Opera / Explorer 9
			delta = event.wheelDelta / 40;
		} else if (event.detail) { // Firefox
			delta = - event.detail / 3;
		}

        if (zLookAt - delta * p * s > 0 || zLookAt - delta * p * s < -400 * VIZ.count) return;
        camera.position.z -= delta * p * s;
        zLookAt -= delta * p * s;
        camera.lookAt({x:0, y:25, z:zLookAt });
        VIZ.render();
        VIZ.animate();
    });

}());