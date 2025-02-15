<script lang="ts">
  import { onMount } from 'svelte';
  import * as THREE from "three";
  import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";

  onMount(() => {
    const container = document.getElementById('galaxy-container');
    
    let scene = new THREE.Scene();
    scene.background = new THREE.Color(0x160016);
    let camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 1000);
    camera.position.set(0, 4, 44);
    let renderer = new THREE.WebGLRenderer({ antialias: false });
    renderer.setSize(window.innerWidth, window.innerHeight);
    container.appendChild(renderer.domElement);

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener("resize", handleResize);

    let controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.enablePan = false;

    let gu = {
      time: {value: 0}
    }

    let sizes = [];
    let shift = [];
    let pushShift = () => {
      shift.push(
        Math.random() * Math.PI, 
        Math.random() * Math.PI * 2, 
        (Math.random() * 0.9 + 0.1) * Math.PI * 0.1,
        Math.random() * 0.9 + 0.1
      );
    }
    
    let pts = new Array(25000).fill(null).map(p => {
      sizes.push(Math.random() * 1.5 + 0.5);
      pushShift();
      return new THREE.Vector3().randomDirection().multiplyScalar(Math.random() * 0.5 + 9.5);
    })
    
    for(let i = 0; i < 50000; i++){
      let r = 10, R = 40;
      let rand = Math.pow(Math.random(), 1.5);
      let radius = Math.sqrt(R * R * rand + (1 - rand) * r * r);
      pts.push(new THREE.Vector3().setFromCylindricalCoords(radius, Math.random() * 2 * Math.PI, (Math.random() - 0.5) * 2 ));
      sizes.push(Math.random() * 1.5 + 0.5);
      pushShift();
    }

    let g = new THREE.BufferGeometry().setFromPoints(pts);
    g.setAttribute("sizes", new THREE.Float32BufferAttribute(sizes, 1));
    g.setAttribute("shift", new THREE.Float32BufferAttribute(shift, 4));
    
    let m = new THREE.PointsMaterial({
      size: 0.125,
      transparent: true,
      depthTest: false,
      blending: THREE.AdditiveBlending
    });

    m.onBeforeCompile = shader => {
      shader.uniforms.time = gu.time;
      shader.vertexShader = `
        uniform float time;
        attribute float sizes;
        attribute vec4 shift;
        varying vec3 vColor2;
        ${shader.vertexShader}
      `.replace(
        `gl_PointSize = size;`,
        `gl_PointSize = size * sizes;`
      ).replace(
        `#include <color_vertex>`,
        `#include <color_vertex>
          float d = length(abs(position) / vec3(40., 10., 40));
          d = clamp(d, 0., 1.);
          vColor2 = mix(vec3(227., 155., 0.), vec3(100., 50., 255.), d) / 255.;
        `
      ).replace(
        `#include <begin_vertex>`,
        `#include <begin_vertex>
          float t = time;
          float moveT = mod(shift.x + shift.z * t, PI2);
          float moveS = mod(shift.y + shift.z * t, PI2);
          transformed += vec3(cos(moveS) * sin(moveT), cos(moveT), sin(moveS) * sin(moveT)) * shift.w;
        `
      );
      
      shader.fragmentShader = `
        varying vec3 vColor2;
        ${shader.fragmentShader}
      `.replace(
        `vec4 diffuseColor = vec4( diffuse, opacity );`,
        `float d = length(gl_PointCoord.xy - 0.5);
         vec4 diffuseColor = vec4( vColor2, smoothstep(0.5, 0.1, d) );`
      );
    };
    
    let p = new THREE.Points(g, m);
    p.rotation.order = "ZYX";
    p.rotation.z = 0.2;
    scene.add(p)

    let clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      let t = clock.getElapsedTime() * 0.1;
      gu.time.value = t * Math.PI;
      p.rotation.y = t * 0.02;
      renderer.render(scene, camera);
    }

    animate();

    return () => {
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
  });
</script>

<div id="word" class="hidden">darwin</div>
<div id="galaxy-container" class="fixed top-0 left-0 w-full h-full -z-10"></div> 