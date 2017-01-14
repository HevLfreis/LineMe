/**
 * Created by hevlhayt@foxmail.com
 * Date: 2017/1/12
 * Time: 12:33
 */
$(function() {

    var camera, tick = 0,
        scene, renderer, clock = new THREE.Clock(true), container,
        width, height,
        optionsBlue, optionsYellow, optionsGreen,
        spawnerOptions, particleBlue, particleYellow, particleGreen;

    if(window.supportsWebGL&&(!window.mobileAndTabletcheck())) {
        init();
        animate();
    }
    else {
        console.log("no support");
        $('#particle').remove();
        $('#layer-container').remove();
    }

    function init() {

        container = $('#particle');
        width = window.innerWidth;
        height = window.innerHeight - $('.main-header').height();

        camera = new THREE.PerspectiveCamera(30, width / height, 1, 10000);
        camera.position.z = 100;
        scene = new THREE.Scene();
        //scene.background = new THREE.Color(0xff0000);
        // The GPU Particle system extends THREE.Object3D, and so you can use it
        // as you would any other scene graph component.	Particle positions will be
        // relative to the position of the particle system, but you will probably only need one
        // system for your whole scene
        particleBlue= new THREE.GPUParticleSystem({
            maxParticles: 250000
        });
        particleYellow = new THREE.GPUParticleSystem({
            maxParticles: 250000
        });
        particleGreen = new THREE.GPUParticleSystem({
            maxParticles: 250000
        });
        scene.add(particleBlue);
        scene.add(particleYellow);
        scene.add(particleGreen);

        var rectLight = new THREE.RectAreaLight(0xFFFFFF, undefined, 2, 10);
                    rectLight.matrixAutoUpdate = true;
                    rectLight.intensity = 80.0;
                    rectLight.position.set(5, 5, -5);
                    scene.add(rectLight);
        //var light = new THREE.PointLight(0xffffff);
        //light.position.set(10,10,1000);
        //scene.add(light);

        var loader = new THREE.FontLoader();
        loader.load( '/static/data/parisish_regular.json', function (response) {
            var font = response;
            var material = new THREE.MeshPhongMaterial({
                color: 0xffffff
            });

            var textGeom = new THREE.TextGeometry('LineMe', {
                size: 10,
                height: 5,
                curveSegments: 4,
                bevelThickness: 5,
                bevelSize: 1.5,
                bevelSegments: 3,
                font: font // Must be lowercase!
            });
            var textMesh = new THREE.Mesh(textGeom, material);

            textGeom.computeBoundingBox();
            textGeom.computeVertexNormals();

            var textWidth = textGeom.boundingBox.max.x - textGeom.boundingBox.min.x;

            textMesh.position.set(-0.5*textWidth, 0, -5);

            scene.add(textMesh);
        });

        //var img = new THREE.MeshBasicMaterial({ //CHANGED to MeshBasicMaterial
        //    map:THREE.ImageUtils.loadTexture('/media/images/logot.png')
        //});
        ////img.map.needsUpdate = true; //ADDED
        //
        //var plane = new THREE.Mesh(new THREE.PlaneGeometry(40, 16),img);
        //plane.position.z = -5;
        //plane.overdraw = true;
        //scene.add(plane);
        //
        //// plane
        //var cube = new THREE.BoxBufferGeometry( 20, 8, 5 );
        ////plane.overdraw = true;
        //var mesh = new THREE.Mesh(cube, new THREE.MeshLambertMaterial( { color: 0x000 } ));
        //scene.add(mesh);

        //setTimeout(function (){
        //    scene.add(particleSystem2);
        //    var sphere;
        //
        //    sphere = new THREE.Mesh(
        //         new THREE.SphereGeometry(10,10),                //width,height,depth
        //         new THREE.MeshLambertMaterial({color: 0xff0000}) //材质设定
        //    );
        //    scene.add(sphere);
        //    sphere.position.set(0,0,-10);
        //
        //    console.log(scene.children)
        //}, 2000);


        // options passed during each spawned
        optionsBlue = {
            position: new THREE.Vector3(),
            positionRandomness: .3,
            velocity: new THREE.Vector3(),
            velocityRandomness: .5,
            color: 0x3498db,
            colorRandomness: .2,
            turbulence: .5,
            lifetime: 2,
            size: 5,
            sizeRandomness: 1
        };
        optionsYellow = {
            position: new THREE.Vector3(),
            positionRandomness: .3,
            velocity: new THREE.Vector3(),
            velocityRandomness: .5,
            color: 0xf39c12,
            colorRandomness: .2,
            turbulence: .5,
            lifetime: 2,
            size: 5,
            sizeRandomness: 1
        };
        optionsGreen = {
            position: new THREE.Vector3(),
            positionRandomness: .3,
            velocity: new THREE.Vector3(),
            velocityRandomness: .5,
            color: 0x1abc9c,
            colorRandomness: .2,
            turbulence: .5,
            lifetime: 2,
            size: 5,
            sizeRandomness: 1
        };
        spawnerOptions = {
            spawnRate: 15000,
            horizontalSpeed: 1.5,
            verticalSpeed: 1.33,
            timeScale: 1
        };

        renderer = new THREE.WebGLRenderer({alpha: true});
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(width, height);
        document.getElementById('particle').appendChild(renderer.domElement);

        window.addEventListener('resize', onWindowResize, false);
    }
    function onWindowResize() {
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    }
    function animate() {
        requestAnimationFrame(animate);

        var delta = clock.getDelta() * spawnerOptions.timeScale;
        tick += delta;
        if (tick < 0) tick = 0;
        if (delta > 0) {
            optionsBlue.position.x = Math.sin(tick * spawnerOptions.horizontalSpeed) * 20;
            optionsBlue.position.y = Math.sin(tick * spawnerOptions.verticalSpeed) * 10;
            optionsBlue.position.z = Math.sin(tick * spawnerOptions.horizontalSpeed + spawnerOptions.verticalSpeed) * 10;
            optionsYellow.position.x = Math.sin(tick * spawnerOptions.horizontalSpeed) * -20;
            optionsYellow.position.y = Math.sin(tick * spawnerOptions.verticalSpeed) * 18;
            optionsYellow.position.z = Math.sin(tick * spawnerOptions.horizontalSpeed + spawnerOptions.verticalSpeed) * 8;
            optionsGreen.position.x = Math.cos(tick * spawnerOptions.horizontalSpeed) * 20;
            optionsGreen.position.y = Math.sin(tick * spawnerOptions.verticalSpeed) * -15;
            optionsGreen.position.z = Math.sin(tick * spawnerOptions.horizontalSpeed + spawnerOptions.verticalSpeed) * -8;
            for (var x = 0; x < spawnerOptions.spawnRate * delta; x++) {
                // Yep, that's really it.	Spawning particles is super cheap, and once you spawn them, the rest of
                // their lifecycle is handled entirely on the GPU, driven by a time uniform updated below
                particleBlue.spawnParticle(optionsBlue);
                particleYellow.spawnParticle(optionsYellow);
                particleGreen.spawnParticle(optionsGreen);
            }
        }
        particleBlue.update(tick);
        particleYellow.update(tick);
        particleGreen.update(tick);
        render();
    }
    function render() {
        renderer.render(scene, camera);
    }

});