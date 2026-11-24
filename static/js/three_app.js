/* Interactive Three.js viewer showing project thumbnails on a cube */
(function(){
  if(typeof THREE === 'undefined') return;

  const canvas = document.getElementById('three-canvas');
  if(!canvas) return;

  const renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true});
  renderer.setPixelRatio(window.devicePixelRatio || 1);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 2, 0.1, 1000);
  camera.position.set(0, 1.2, 3);

  const light = new THREE.HemisphereLight(0xffffff, 0x444444, 1.2);
  scene.add(light);
  const dir = new THREE.DirectionalLight(0xffffff, 0.6);
  dir.position.set(3,10,10);
  scene.add(dir);

  // Project image paths (served by Flask /media/ route)
  const faces = [
    '/media/project1.jpg',
    '/media/project2.jpg',
    '/media/project3.jfif',
    '/media/project1.jpg',
    '/media/project2.jpg',
    '/media/project3.jfif'
  ];

  const loader = new THREE.TextureLoader();
  const materials = faces.map((url)=>{
    const tex = loader.load(url, undefined, undefined, function(){
      // onError fallback: use simple color
    });
    tex.minFilter = THREE.LinearFilter;
    return new THREE.MeshStandardMaterial({map: tex, roughness:0.6, metalness:0.1});
  });

  const geometry = new THREE.BoxGeometry(1.6,1.6,1.6);
  const cube = new THREE.Mesh(geometry, materials);
  scene.add(cube);

  // Orbit controls (examples/js/controls/OrbitControls.js must be included)
  let controls = null;
  try{
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 1.6;
    controls.maxDistance = 6;
  }catch(e){/* controls optional */}

  function resizeRendererToDisplaySize(){
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const needResize = canvas.width !== Math.floor(width * window.devicePixelRatio) || canvas.height !== Math.floor(height * window.devicePixelRatio);
    if(needResize){
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    }
    return needResize;
  }

  let lastTime = 0;
  function animate(time){
    time *= 0.001;
    const dt = time - lastTime;
    lastTime = time;

    cube.rotation.y += dt * 0.4; // slow auto-rotate
    if(controls){ controls.update(); }

    resizeRendererToDisplaySize();
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }
  requestAnimationFrame(animate);

  // Make cube interactive: click to open project link
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  function onPointer(event){
    const rect = canvas.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const intersects = raycaster.intersectObject(cube);
    if(intersects.length>0){
      const faceIndex = Math.floor(intersects[0].face.materialIndex);
      // map faceIndex to project links as defined in server-side projects
      const links = ['#','#','#','#','#','#'];
      const url = links[faceIndex] || '#';
      if(url && url!=='#') window.open(url, '_blank');
    }
  }
  canvas.addEventListener('click', onPointer, {passive:true});

  // Touch-friendly: simple tap detection
  let touchStart = null;
  canvas.addEventListener('touchstart', (e)=>{ touchStart = e.touches[0]; }, {passive:true});
  canvas.addEventListener('touchend', (e)=>{ if(!touchStart) return; const touch = e.changedTouches[0]; const dx = Math.abs(touch.clientX - touchStart.clientX); const dy = Math.abs(touch.clientY - touchStart.clientY); if(dx<10 && dy<10) onPointer(touch); touchStart = null; }, {passive:true});

})();
