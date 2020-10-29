
//import * as THREE from 'three';//'https://threejsfundamentals.org/threejs/resources/threejs/r119/build/three.module.js';
//import {OrbitControls} from './node_modules/three/examples/jsm/controls/OrbitControls.js';
import {GLTFLoader} from './node_modules/three/examples/jsm/loaders/GLTFLoader.js';
//import {EffectComposer} from './node_modules/three/examples/jsm/postprocessing/EffectComposer.js';


let renderer, camera, scene;

function init() {
  const canvas = document.querySelector('#c');
  //const xElem = document.querySelector('#x');
  //const yElem = document.querySelector('#y');
  //const zElem = document.querySelector('#z');
  //const container = document.createElement( 'div' );
  //document.body.appendChild( container );
  //renderer = new THREE.WebGLRenderer( { antialias: true } );

  //renderer = new THREE.WebGLRenderer({canvas});
  renderer = new THREE.WebGLRenderer({canvas});

  //container.appendChild(renderer.domElement);
  //canvas.appendChild(renderer.domElement);

  const fov = 45;
  const aspect = 2;  // the canvas default
  const near = 0.1;
  const far = 100;
  camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
  camera.position.set(0, 10, 756);

  //const controls = new OrbitControls(camera, canvas);
  //controls.target.set(0, 5, 0);
  //controls.update();

  scene = new THREE.Scene();

  const loader = new THREE.TextureLoader();
  const bgTexture = loader.load('./images/couch_blur.jpg');
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

  //Position camera
  function frameArea(sizeToFitOnScreen, boxSize, boxCenter, camera) {
    const halfSizeToFitOnScreen = sizeToFitOnScreen * 0.5;
    const halfFovY = THREE.MathUtils.degToRad(camera.fov * .5);
    const distance = halfSizeToFitOnScreen / Math.tan(halfFovY);
    // compute a unit vector that points in the direction the camera is now
    // in the xz plane from the center of the box
    const direction = (new THREE.Vector3())
        .subVectors(camera.position, boxCenter)
        .multiply(new THREE.Vector3(1, 0, 1))
        .normalize();

    // move the camera to a position distance units way from the center
    // in whatever direction the camera was from the center already
    camera.position.copy(direction.multiplyScalar(distance).add(boxCenter));

    // pick some near and far values for the frustum that
    // will contain the box.
    camera.near = boxSize / 100;
    camera.far = boxSize * 100;

    camera.updateProjectionMatrix();

    // point the camera to look at the center of the box
    camera.lookAt(boxCenter.x, boxCenter.y, boxCenter.z);
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

    const gltfLoader = new GLTFLoader(loadingManager);
    //todo, try renderpeople here
    gltfLoader.load('./angelica/scene.gltf', (gltf) => {
    //gltfLoader.load('./sophia/rp_sophia_animated_003_idling.glb', (gltf) => {
      const root = gltf.scene;
      //root.rotateY(Math.PI/0.5)
      //root.rotation.y = 0;//Math.PI
      //console.log(root)
      scene.add(root);

      // compute the box that contains all the stuff
      // from root and below
      const box = new THREE.Box3().setFromObject(root);

      const boxSize = box.getSize(new THREE.Vector3()).length();
      const boxCenter = box.getCenter(new THREE.Vector3());

      // set the camera to frame the box
      frameArea(boxSize * 1, boxSize, boxCenter, camera); //1 instead of 0.5 //finetune

      // update the Trackball controls to handle the new size
      //controls.maxDistance = boxSize * 10;
      //controls.target.copy(boxCenter);
      //controls.update();
    });
  }
}

function main() {

  function resizeRendererToDisplaySize(renderer) {
    const canvas = renderer.domElement;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const needResize = canvas.width !== width || canvas.height !== height;
    if (needResize) {
      renderer.setSize(width, height, false);
    }
    return needResize;
  }

/*  function onWindowResize() {

        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();

        renderer.setSize( window.innerWidth, window.innerHeight );

  }*/

  function render() {
    if (resizeRendererToDisplaySize(renderer)) {
      const canvas = renderer.domElement;
      camera.aspect = canvas.clientWidth / canvas.clientHeight;
      camera.updateProjectionMatrix();
    }

    renderer.render(scene, camera);

    requestAnimationFrame(render);
    
    //root.rotation.y += 0.01;
  }
  //window.addEventListener( 'resize', onWindowResize, false );
  requestAnimationFrame(render);

/*  xElem.textContent = boxCenter.x;
  yElem.textContent = boxCenter.y;
  zElem.textContent = boxCenter.z;*/

  //console.log(controls)
}

init();
main();
