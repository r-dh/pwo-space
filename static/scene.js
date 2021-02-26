
//import * as THREE from 'three';//'https://threejsfundamentals.org/threejs/resources/threejs/r119/build/three.module.js';
//import {OrbitControls} from './node_modules/three/examples/jsm/controls/OrbitControls.js';

//import {GLTFLoader} from './node_modules/three/examples/jsm/loaders/GLTFLoader.js';
//import * as THREE from 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r122/three.min.js';

//const scene = new THREE.Scene();


let renderer, camera, scene;
var mixer, clock;

function init() {
  const canvas = document.querySelector('#c');

  renderer = new THREE.WebGLRenderer({canvas, antialias: true});
  renderer.setPixelRatio( window.devicePixelRatio );
  renderer.setSize( window.innerWidth, window.innerHeight );

  camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.z = 5;

  //TODO: TEMP
  //const controls = new THREE.OrbitControls(camera, canvas);
  //controls.target.set(0, 5, 0);
  //controls.update();

  scene = new THREE.Scene();

  const loader = new THREE.TextureLoader();
  const bgTexture = loader.load('/static/img/couch_blur.jpg');
  scene.background = bgTexture;


  //Lights + colour
  {
    const skyColor = 0xB1E1FF;  // light blue
    const groundColor = 0xB97A20;  // brownish orange
    const intensity = 1;
    const light = new THREE.HemisphereLight(skyColor, groundColor, intensity);
    scene.add(light);
  }

  {
    const color = 0xFFFFFF;
    const intensity = 1;
    const light = new THREE.DirectionalLight(color, intensity);
    light.position.set(5, 10, 2);
    scene.add(light);
    scene.add(light.target);
  }

  //Animation + loader
  {
    const loadingManager = new THREE.LoadingManager(() => {
    
      const loadingScreen = document.getElementById('loading-screen');
      loadingScreen.classList.add('fade-out');
      
      // optional: remove loader from DOM via event listener
      loadingScreen.addEventListener('transitionend', () => {
        loadingScreen.remove();
      });
      
    });

    const gltfLoader = new THREE.GLTFLoader(loadingManager);
      // gltfLoader.load('static/angelica/scene.gltf', (gltf) => {
      // gltfLoader.load('./sophia/rp_sophia_animated_003_idling.glb', (gltf) => {
      gltfLoader.load('static/nathan/nathan_sitting_fidgeting.gltf', (gltf) => {
      //gltfLoader.load('static/sophia/sophia_idling.gltf', (gltf) => {
    
      scene.add(gltf.scene);

      var animations = gltf.animations;
      console.log(animations) // name: Armature|Take 001|BaseLayer.001
      //var keyRotationClip = gltf.animations[0] //THREE.AnimationClip.findByName( animations, 'A' );
      var keyRotationClip = THREE.AnimationClip.findByName(animations, 'sitting_fidgeting.001');

      //cut first frame
      //keyRotationClip = THREE.AnimationUtils.subclip(keyRotationClip, "idling", 2, Infinity, 30);// : AnimationClip

      mixer = new THREE.AnimationMixer(gltf.scene);
      var action = mixer.clipAction(keyRotationClip);

      action.clampWhenFinished = true;
      //action.loop = THREE.LoopPingPong; //THREE.LoopOnce;
      action.play();

      // center model
      const object = gltf.scene;

      const box = new THREE.Box3().setFromObject(object);
      const center = box.getCenter(new THREE.Vector3());

      var offset_sophia = 7;
      var offset_nathan_sitting = 5.55;
      var offset = offset_nathan_sitting;

      object.position.x += (object.position.x - center.x);
      object.position.y += (object.position.y - center.y - offset);
      object.position.z += (object.position.z - center.z);

      // disable view frustum culling
      object.traverse(function(child) {

        child.frustumCulled = false;

      });

      clock = new THREE.Clock();

      window.addEventListener('resize', onWindowResize, false);
    });
  }
}


function onWindowResize() {

  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  renderer.setSize(window.innerWidth, window.innerHeight);

}

function animate() {

  requestAnimationFrame( animate );

  if ( mixer ) {

    var delta = clock.getDelta();
    mixer.update( delta );

  }

  renderer.render( scene, camera );

}

init();
animate(); 