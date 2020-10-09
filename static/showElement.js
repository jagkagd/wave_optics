var threeList = new Array();
var braceList = new Array();
var ttlz = 0, w = 0;
var scene, renderer, camera;

function updateThree(){
    ttlz = 0;
    for(var i = 0; i < threeList.length; i++){
        scene.remove(threeList[i]);
        scene.remove(braceList[i]);
    }
    threeList = new Array();
    braceList = new Array();
    for(var i = 0; i < elemListForShow.length; i++){
        w = 0;
        var m = createObject(i, elemListForShow[i]);
        if(m === 0){
            continue;
        }
        scene.add(m[0]);
        m[0].position.z = (ttlz + w) / 3;
        if($.type(m[1]) !== 'string'){
            scene.add(m[1]);
            m[1].position.z = (ttlz + w) / 3;
            m[1].position.y = -(25 + 25);
        }
        threeList.push(m[0]);
        braceList.push(m[1]);
    }
    renderer.render(scene, camera);
}

function createObject(i, obj){
    var geom, material, map1;
    var geom1, material1, map2;
    var mesh1;
    if(obj.length === 0){
        return 0;
    }else if($.inArray(obj[0], ['PlaneWave']) > -1){
        geom = new THREE.PlaneGeometry(50, 50);
        material = new THREE.MeshLambertMaterial();
        mesh1 = 'a';
    }else if($.inArray(obj[0], ['SphereWave']) > -1){
        geom = new THREE.SphereGeometry(2);
        material = new THREE.MeshLambertMaterial();
        w = JSON.parse(obj[1]['pos']['default'])[2];
        mesh1 = 'a';
    }else if($.inArray(obj[0], ['SimpleFreeSpace']) > -1){
        geom = new THREE.Geometry();
        geom.vertices.push(new THREE.Vector3(0, 0, -JSON.parse(obj[1]['z']['default'])));
        geom.vertices.push(new THREE.Vector3(0, 0, 0));
        ttlz += JSON.parse(obj[1]['z']['default']);
        material = new THREE.LineBasicMaterial();
        mesh1 = 'a';
    }else{
        geom = new THREE.PlaneGeometry(50, 50);
        map1 = new THREE.ImageUtils.loadTexture('/texture/' + i.toString() + '.png?' + parseInt(Math.random()*1000000+1).toString());
        material = new THREE.MeshBasicMaterial({map: map1, side: THREE.DoubleSide, transparent: true});
        geom1 = new THREE.PlaneGeometry(50, 50);
        map2 = new THREE.ImageUtils.loadTexture('/static/brace.png');
        material1 = new THREE.MeshBasicMaterial({map: map2, side: THREE.DoubleSide, transparent: true});
        mesh1 = new THREE.Mesh(geom1, material1);
    }
    var mesh = new THREE.Mesh(geom, material);
    return [mesh, mesh1];
}
$(document).ready(function(){
    h = $('#three').height();
    w = $('#three').width();
    camera = new THREE.PerspectiveCamera(45, w/h, 1, 10000);
    camera.position.x = 0;
    camera.position.y = 0;
    camera.position.z = 600;
    camera.up.x = 0;
    camera.up.y = 1;
    camera.up.z = 0;
    scene = new THREE.Scene();
    scene.add(camera);
    var light = new THREE.AmbientLight(0xFFFFFF);
    light.position.set(100, 100, 200);
    scene.add(light);
    light = new THREE.PointLight(0x00FF00);
    light.position.set(0, 0, 300);
    scene.add(light);
    var axes = new THREE.AxisHelper(100);
    scene.add(axes);
    renderer = new THREE.WebGLRenderer();
    renderer.setSize(w, h);
    renderer.render(scene, camera);
    renderer.setClearColor(0xeeeeee, 1.0);
    var container = document.getElementById('three');
    var controls = new THREE.OrbitControls( camera, container);
    controls.addEventListener('change', function(){renderer.render(scene, camera)});
    document.getElementById('three').appendChild(renderer.domElement);
    renderer.render(scene, camera);
});
