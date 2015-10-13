var elemListElement = new Array()
var threeList = new Array();
var ttlz = 0, w = 0;
var scene, renderer, camera;

function updateThree(){
    console.log(elemListElement);
    ttlz = 0;
    for(var i = 0; i < threeList.length; i++){
        scene.remove(threeList[i]);
    }
    threeList = new Array();
    for(var i = 0; i < elemListElement.length; i++){
        w = 0;
        var m = createObject(i, elemListElement[i]);
        scene.add(m);
        m.position.z = (ttlz + w) / 3;
        threeList.push(m);
    }
    renderer.render(scene, camera);
}

function createObject(i, obj){
    var geom, material, map;
    if(obj.length === 0){
        
    }else if($.inArray(obj[0], ['PlaneWave']) > -1){
        geom = new THREE.PlaneGeometry(50, 50);
        material = new THREE.MeshLambertMaterial();
    }else if($.inArray(obj[0], ['SphereWave']) > -1){
        geom = new THREE.SphereGeometry(2);
        material = new THREE.MeshLambertMaterial();
        w = obj[1]['pos'][2];
    }else if($.inArray(obj[0], ['SimpleFreeSpace']) > -1){
        geom = new THREE.Geometry();
        geom.vertices.push(new THREE.Vector3(0, 0, -obj[1]['z']));
        geom.vertices.push(new THREE.Vector3(0, 0, 0));
        ttlz += obj[1]['z'];
        material = new THREE.LineBasicMaterial();
    }else{
        geom = new THREE.PlaneGeometry(50, 50);
        map1 = new THREE.ImageUtils.loadTexture('/texture/' + i.toString() + '.png?' + parseInt(Math.random()*1000000+1).toString());
        material = new THREE.MeshBasicMaterial({map: map1, side: THREE.DoubleSide, transparent: true});
    }
    var mesh = new THREE.Mesh(geom, material);
    return mesh;
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
    renderer.setClearColor(0x000000, 1.0);
    var container = document.getElementById('three');
    var controls = new THREE.OrbitControls( camera, container);
    controls.addEventListener('change', function(){renderer.render(scene, camera)});
    document.getElementById('three').appendChild(renderer.domElement);
    renderer.render(scene, camera);
});
