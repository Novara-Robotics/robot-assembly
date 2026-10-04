// Replays a recorded MuJoCo run of the factory line. Nothing is simulated here: scene.glb is the MuJoCo model
// (z-up, one named node per body) and traj.bin.gz holds every animated body's world pose per frame.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const $ = (s) => document.querySelector(s);
window.addEventListener('error', (e) => { const l = document.querySelector('#loading') || document.body.appendChild(Object.assign(document.createElement('div'), { id: 'loading' })); l.style.cssText = 'position:fixed;inset:0;display:flex;align-items:center;justify-content:center;padding:30px;background:#0b0d10;color:#ff9a8a;font:15px monospace;white-space:pre-wrap;z-index:9'; l.textContent = 'Viewer error: ' + (e.message || e.error); });
window.addEventListener('unhandledrejection', (e) => { window.dispatchEvent(new ErrorEvent('error', { message: String(e.reason) })); });
const mj2three = (p) => new THREE.Vector3(p[0], p[2], -p[1]); // MuJoCo z-up -> three y-up (same as the GLB root rotation)

const renderer = new THREE.WebGLRenderer({ canvas: $('#c'), antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.95;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x151a21);
scene.fog = new THREE.Fog(0x151a21, 14, 30);
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.45;

const camera = new THREE.PerspectiveCamera(42, 1, 0.05, 80);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// light: a sun over the line with a shadow frustum that covers it
const sun = new THREE.DirectionalLight(0xfff3e6, 1.9);
const center = mj2three([0, -0.9, 0.4]);
sun.position.copy(center).add(new THREE.Vector3(-5, 9, 4));
sun.target.position.copy(center);
sun.castShadow = true;
sun.shadow.mapSize.set(4096, 4096);
Object.assign(sun.shadow.camera, { left: -10, right: 10, top: 10, bottom: -10, near: 1, far: 30 });
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 0.02;
scene.add(sun, sun.target, new THREE.HemisphereLight(0xdfe8ff, 0x3a3f48, 0.35));

function resize() {
  renderer.setSize(window.innerWidth, window.innerHeight, false);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', resize);
resize();

const meta = await (await fetch('./assets/traj.json')).json();
const raw = new Int16Array(await new Response((await fetch('./assets/traj.bin.gz')).body.pipeThrough(new DecompressionStream('gzip'))).arrayBuffer());
const T = meta.frames, N = meta.bodies.length, PER = N * 7;
const abs = new Int32Array(T * PER);
abs.set(meta.first, 0);
for (let t = 1; t < T; t++) {
  const o = t * PER, p = (t - 1) * PER;
  for (let k = 0; k < PER; k++) abs[o + k] = abs[p + k] + raw[p + k];
}

const gltf = await new GLTFLoader().loadAsync('./assets/scene.glb');
scene.add(gltf.scene);
gltf.scene.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
const nodes = meta.bodies.map((n) => gltf.scene.getObjectByName(n));

const qa = new THREE.Quaternion(), qb = new THREE.Quaternion();
function applyFrame(f) {
  f = Math.max(0, Math.min(T - 1, f));
  const i = Math.floor(f), j = Math.min(T - 1, i + 1), a = f - i;
  const pu = meta.pos_unit, qu = meta.quat_unit;
  for (let b = 0; b < N; b++) {
    const o = i * PER + b * 7, p = j * PER + b * 7, n = nodes[b];
    if (!n) continue;
    n.position.set((abs[o] + (abs[p] - abs[o]) * a) * pu, (abs[o + 1] + (abs[p + 1] - abs[o + 1]) * a) * pu, (abs[o + 2] + (abs[p + 2] - abs[o + 2]) * a) * pu);
    qa.set(abs[o + 4] * qu, abs[o + 5] * qu, abs[o + 6] * qu, abs[o + 3] * qu).normalize();
    qb.set(abs[p + 4] * qu, abs[p + 5] * qu, abs[p + 6] * qu, abs[p + 3] * qu).normalize();
    if (qa.dot(qb) < 0) { qb.x *= -1; qb.y *= -1; qb.z *= -1; qb.w *= -1; }
    n.quaternion.slerpQuaternions(qa, qb, a);
  }
}

// cameras: the same shots as the MuJoCo renders
const presets = {};
for (const [k, v] of Object.entries(meta.cameras)) presets[k] = { pos: mj2three(v.pos), target: mj2three(v.target) };
let camMode = 'auto', camGoal = presets.overview, camBlend = 1;
const camFrom = { pos: new THREE.Vector3(), target: new THREE.Vector3() };
function goCam(name) {
  camMode = name;
  const key = name === 'wide' ? 'overview' : name;
  if (name !== 'auto') setGoal(presets[key]);
  document.querySelectorAll('[data-cam]').forEach((b) => b.classList.toggle('on', b.dataset.cam === name));
}
function setGoal(g) { if (!g || g === camGoal) return; camFrom.pos.copy(camera.position); camFrom.target.copy(controls.target); camGoal = g; camBlend = 0; }
camera.position.copy(presets.overview.pos); controls.target.copy(presets.overview.target);

// auto director: one steady wide shot (no cuts to individual cells; the cell buttons are there for close-ups)
function autoShot() { return presets.overview; }

// transport
let frame = 0, playing = true, speed = 4, last = performance.now(), scrubbing = false;
const label = $('#label'), sub = $('#sub'), scrub = $('#scrub');
$('#play').onclick = () => { playing = !playing; $('#play').textContent = playing ? 'Pause' : 'Play'; };
document.querySelectorAll('[data-speed]').forEach((b) => b.onclick = () => { speed = +b.dataset.speed; document.querySelectorAll('[data-speed]').forEach((x) => x.classList.toggle('on', x === b)); });
document.querySelectorAll('[data-cam]').forEach((b) => b.onclick = () => goCam(b.dataset.cam));
scrub.oninput = () => { frame = (scrub.value / 1000) * (T - 1); scrubbing = true; };
scrub.onchange = () => { scrubbing = false; };
$('#hide').onclick = () => document.body.classList.toggle('hide');
window.addEventListener('keydown', (e) => {
  if (e.key === 'h' || e.key === 'H') document.body.classList.toggle('hide');
  else if (e.key === ' ') $('#play').click();
  else if (e.key === 'r' || e.key === 'R') frame = 0;
});
const params = new URLSearchParams(location.search);
if (params.get('ui') === '0') document.body.classList.add('hide');
if (params.has('t')) frame = Math.min(T - 1, +params.get('t') * meta.fps);   // ?t=SECONDS : start there
if (params.has('speed')) { speed = +params.get('speed'); }
if (params.get('pause') === '1') { playing = false; $('#play').textContent = 'Play'; }
if (params.has('cam')) goCam(params.get('cam'));
$('#loading').remove();

function tick(now) {
  requestAnimationFrame(tick);                       // schedule first: one bad frame must never stop playback
  const dt = Math.max(0, Math.min(0.25, (now - last) / 1000)); last = now;   // rAF timestamps can precede `last`
  if (playing && !scrubbing) frame += dt * meta.fps * speed;
  frame = Math.max(0, frame);
  if (frame >= T - 1) { frame = new URLSearchParams(location.search).has('loop') ? 0 : T - 1; if (frame > 0) { playing = false; $('#play').textContent = 'Play'; } }
  applyFrame(frame);
  const L = meta.labels; let cur = '';
  for (let i = 0; i < L.length; i++) if (L[i][0] <= frame) cur = L[i][1];
  label.textContent = cur;
  sub.textContent = `${(frame / meta.fps).toFixed(0)} s of ${(T / meta.fps).toFixed(0)} s   |   ${speed}x`;
  scrub.value = (frame / (T - 1)) * 1000;
  if (camMode === 'auto') setGoal(autoShot(frame));
  if (camBlend < 1) {
    camBlend = Math.min(1, camBlend + dt / 1.4);
    const s = camBlend * camBlend * (3 - 2 * camBlend);
    camera.position.lerpVectors(camFrom.pos, camGoal.pos, s);
    controls.target.lerpVectors(camFrom.target, camGoal.target, s);
  }
  controls.update();
  renderer.render(scene, camera);
}
requestAnimationFrame(tick);
window.__ready = true;
