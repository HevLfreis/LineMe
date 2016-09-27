(function () {
    var VIZ = {};
    var camera, renderer, controls, scene = new THREE.Scene();
    var width = window.innerWidth, height = window.innerHeight;

    camera = new THREE.PerspectiveCamera(40, width / height, 1, 10000);
    camera.position.x = 800;
    camera.position.y = 600;
    camera.position.z = 2500;
    camera.setLens(30);

    VIZ.drawElements = function (datas) {

        VIZ.count = datas.length;

        var margin = {top: 17, right: 0, bottom: 16, left: 20},
            width = 800 - margin.left - margin.right,
            height = 600 - margin.top - margin.bottom;


        var color = d3.scale.ordinal()
            .range(['rgb(166,206,227)', 'rgb(31,120,180)', 'rgb(178,223,138)', 'rgb(51,160,44)', 'rgb(251,154,153)', 'rgb(227,26,28)', 'rgb(253,191,111)', 'rgb(255,127,0)']);

        var vis = d3.selectAll(".element").data(datas).enter().append('svg');

        vis.attr('fill', 'red')
            .attr('stroke', 'black')
            .attr('stroke-width', 1)
            .attr('class', 'element')
            .attr("width", width)
            .attr("height", height);

        var defs = vis.append("defs").attr("class", "imgdefs");

        vis.each(function () {
            var force = d3.layout.force()
                .charge(-100)
                .linkDistance(250)
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
                    return "link";
                });

            node = node.data(nodes, function (d) {
                return d.id;
            });

            node.enter().append("g")
                .attr("class", "node").attr("r", 20)
                .style("fill", function (d) {
                    return color(d.group);
                })
                .style("stroke", function (d) {
                    return color(d.group);
                });

            node.append("circle")
                .attr("r", 20);

            node.append("image")
                .attr('x', -20)
                .attr('y', -20)
                .attr('width', 40)
                .attr('height', 40)
                .attr("xlink:href", function (d) {
                    if (d.userid != -1)
                        return "/media/images/avatars/" + d.userid + ".png"
                })
                .attr("clip-path", "url(#clip-circle)");

            force.start()

            force.on("tick", function () {
                link.attr("x1", function (d) {
                        return d.source.x;
                    })
                    .attr("y1", function (d) {
                        return d.source.y;
                    })
                    .attr("x2", function (d) {
                        return d.target.x;
                    })
                    .attr("y2", function (d) {
                        return d.target.y;
                    });

                node.attr("transform", function (d) {
                    return "translate(" + d.x + "," + d.y + ")";
                });


            });

        });


        var clipPath = defs.append('clipPath').attr('id', 'clip-circle')
            .append("circle")
            .attr("r", 20)
            .attr("cy", 0)
            .attr("cx", 0);

        vis.each(setData);
        vis.each(objectify);
    }

    function objectify(d) {
        var object = new THREE.CSS3DObject(this);
        object.position = d.random.position;
        scene.add(object);
    }

    function setData(d, i) {
        var vector, phi, theta;

        var random = new THREE.Object3D();
        random.position.x = Math.random() * 4000 - 2000;
        random.position.y = Math.random() * 4000 - 2000;
        random.position.z = Math.random() * 4000 - 2000;
        d['random'] = random;

        var sphere = new THREE.Object3D();
        vector = new THREE.Vector3();
        phi = Math.acos(-1 + ( 2 * i ) / (VIZ.count - 1));
        theta = Math.sqrt((VIZ.count - 1) * Math.PI) * phi;
        sphere.position.x = 800 * Math.cos(theta) * Math.sin(phi);
        sphere.position.y = 800 * Math.sin(theta) * Math.sin(phi);
        sphere.position.z = 800 * Math.cos(phi);
        vector.copy(sphere.position).multiplyScalar(2);
        sphere.lookAt(vector);
        //camera.position.x += 1000;
        d['sphere'] = sphere;

        var helix = new THREE.Object3D();
        //vector = new THREE.Vector3();
        //phi = (i + 12) * 0.250 + Math.PI;
        //helix.position.x = 1000 * Math.sin(phi);
        //helix.position.y = - (i * 8) + 500;
        //helix.position.z = 1000 * Math.cos(phi);
        //vector.x = helix.position.x * 2;
        //vector.y = helix.position.y;
        //vector.z = helix.position.z * 2;
        //helix.lookAt(vector);
        helix.position.x = 0;
        helix.position.y = 0;
        helix.position.z = (Math.floor(i)) * 400 - 1500;

        d['helix'] = helix;

        var grid = new THREE.Object3D();
        //grid.position.x = (( i % 5 ) * 400) - 800;
        //grid.position.y = ( - ( Math.floor( i / 5 ) % 5 ) * 400 ) + 800;
        //grid.position.z = (Math.floor( i / 25 )) * 1000 - 2000;
        grid.position.x = (( i % 5 ) * 400) - 800;
        grid.position.y = ( -( Math.floor(i / 5) % 5 ) * 400 ) + 800;
        grid.position.z = (Math.floor(i / 25)) * 1000 - 2000;
        d['grid'] = grid;
    }

    VIZ.render = function () {
        renderer.render(scene, camera);
    };

    d3.select("#menu").selectAll('button')
        .data(['sphere', 'helix', 'grid']).enter()
        .append('button')
        .html(function (d) {
            return d;
        })
        .on('click', function (d) {
            //VIZ.transform(d);
            camera.position.z -= 100;
            VIZ.render();
        })

    VIZ.transform = function (layout) {
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
    }

    VIZ.animate = function () {
        requestAnimationFrame(VIZ.animate);
        TWEEN.update();
        controls.update();
    }

    renderer = new THREE.CSS3DRenderer();
    renderer.setSize(width, height);
    renderer.domElement.style.position = 'absolute';
    document.getElementById('container').appendChild(renderer.domElement);

    controls = new THREE.TrackballControls(camera, renderer.domElement);
    controls.rotateSpeed = 0.25;
    controls.minDistance = 0;
    controls.maxDistance = 5000;
    controls.addEventListener('change', VIZ.render);

    VIZ.onWindowResize = function () {
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
        VIZ.render();
    }
    window.VIZ = VIZ;
}())