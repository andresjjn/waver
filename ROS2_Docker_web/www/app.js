/* Dashboard Vigilante Nocturno — Wave Rover
 * rosbridge (9090) para topics, web_video_server (8080) para video MJPEG.
 * Publica /web_vel (prioridad 90 en twist_mux), /lights, /set_mode, /set_estop.
 */
'use strict';

const HOST = location.hostname;
const ROSBRIDGE_URL = `ws://${HOST}:9090`;
const VIDEO_URL = (topic) => `http://${HOST}:8080/stream?topic=${topic}&type=ros_compressed&qos_profile=sensor_data`;
const SNAPSHOT_URL = (topic) => `http://${HOST}:8080/snapshot?topic=${topic}`;

const $ = (id) => document.getElementById(id);
const logEl = $('log');

function logEvent(text, isEvt = false) {
  const d = document.createElement('div');
  if (isEvt) d.className = 'evt';
  d.textContent = `${new Date().toLocaleTimeString()} ${text}`;
  logEl.prepend(d);
  while (logEl.children.length > 60) logEl.lastChild.remove();
}

/* ---------- conexión ROS ---------- */
const ros = new ROSLIB.Ros({ url: ROSBRIDGE_URL });

ros.on('connection', () => {
  $('conn-badge').textContent = 'conectado';
  $('conn-badge').className = 'badge ok';
  logEvent('Conectado a rosbridge');
});
ros.on('close', () => {
  $('conn-badge').textContent = 'desconectado';
  $('conn-badge').className = 'badge err';
  setTimeout(() => ros.connect(ROSBRIDGE_URL), 2000);
});
ros.on('error', () => {});

const topic = (name, messageType, opts = {}) =>
  new ROSLIB.Topic({ ros, name, messageType, ...opts });

const pubWebVel = topic('/web_vel', 'geometry_msgs/msg/Twist');
const pubLights = topic('/lights', 'std_msgs/msg/Int16MultiArray');
const pubSetMode = topic('/set_mode', 'std_msgs/msg/String');
const pubSetEstop = topic('/set_estop', 'std_msgs/msg/Bool');

/* ---------- vídeo ---------- */
const videoEl = $('video');
const videoSrc = $('video-src');
function setVideo() { videoEl.src = VIDEO_URL(videoSrc.value); }
videoSrc.onchange = setVideo;
setVideo();
$('btn-snap').onclick = () => window.open(SNAPSHOT_URL(videoSrc.value), '_blank');

/* ---------- modo y e-stop ---------- */
let currentMode = '—';
let estopOn = false;

topic('/robot_mode', 'std_msgs/msg/String').subscribe((m) => {
  if (m.data !== currentMode) logEvent(`Modo: ${m.data}`, true);
  currentMode = m.data;
  const b = $('mode-badge');
  b.textContent = currentMode;
  b.className = `badge ${currentMode}`;
  $('btn-auto').classList.toggle('on', currentMode === 'AUTO');
  estopOn = currentMode === 'E_STOP';
  $('btn-estop').classList.toggle('on', estopOn);
});

$('btn-auto').onclick = () =>
  pubSetMode.publish({ data: currentMode === 'AUTO' ? 'TELEOP' : 'AUTO' });
$('btn-estop').onclick = () => pubSetEstop.publish({ data: !estopOn });

/* ---------- focos ---------- */
function sendLights() {
  pubLights.publish({ data: [Number($('light-io4').value), Number($('light-io5').value)] });
}
$('light-io4').oninput = sendLights;
$('light-io5').oninput = sendLights;

/* ---------- telemetría ---------- */
let roll = 0, pitch = 0, yaw = 0;

topic('/imu/rpy', 'geometry_msgs/msg/Vector3Stamped', { throttle_rate: 100 })
  .subscribe((m) => {
    roll = m.vector.x; pitch = m.vector.y; yaw = m.vector.z;
    $('rp').textContent = `${roll.toFixed(1)}° / ${pitch.toFixed(1)}°`;
    $('yaw').textContent = `${((yaw + 360) % 360).toFixed(0)}°`;
    drawHorizon(); drawCompass();
  });

topic('/battery', 'sensor_msgs/msg/BatteryState').subscribe((m) => {
  $('bat-v').textContent = `${m.voltage.toFixed(2)} V`;
  $('bat-a').textContent = `${(m.current * 1000).toFixed(0)} mA`;
  const charging = m.power_supply_status === 1;
  $('bat-s').textContent = charging ? '⚡ cargando' : 'descargando';
  const pct = Math.round(m.percentage * 100);
  const bar = $('bat-bar');
  bar.style.width = `${pct}%`;
  bar.style.background = pct > 40 ? 'var(--ok)' : pct > 20 ? 'var(--warn)' : 'var(--err)';
  if (pct <= 20 && !charging) logEvent(`Batería baja: ${pct}%`, true);
});

let batAlert = 'OK';
topic('/battery_alert', 'std_msgs/msg/String').subscribe((m) => {
  if (m.data !== batAlert) {
    batAlert = m.data;
    if (batAlert === 'WARN') logEvent('🔋 Batería BAJA — terminar la ronda', true);
    else if (batAlert === 'CRITICAL') logEvent('🪫 Batería CRÍTICA — navegación vetada', true);
    else logEvent('🔋 Batería OK');
  }
});

topic('/imu/temperature', 'std_msgs/msg/Float32', { throttle_rate: 2000 })
  .subscribe((m) => { $('temp').textContent = `${m.data.toFixed(1)} °C`; });

// Clases COCO-80 (orden yolov4_tiny del driver depthai)
const COCO = ['persona','bicicleta','coche','moto','avión','bus','tren','camión',
  'barco','semáforo','hidrante','señal stop','parquímetro','banco','pájaro','gato',
  'perro','caballo','oveja','vaca','elefante','oso','cebra','jirafa','mochila',
  'paraguas','bolso','corbata','maleta','frisbee','esquís','snowboard','pelota',
  'cometa','bate','guante béisbol','skate','tabla surf','raqueta','botella',
  'copa','taza','tenedor','cuchillo','cuchara','bol','plátano','manzana',
  'sándwich','naranja','brócoli','zanahoria','hot dog','pizza','donut','tarta',
  'silla','sofá','planta','cama','mesa','inodoro','tele','portátil','ratón',
  'mando','teclado','celular','microondas','horno','tostadora','fregadero',
  'nevera','libro','reloj','jarrón','tijeras','peluche','secador','cepillo dientes'];

/* Overlay de cajas sobre el video. Las bbox llegan en pixeles del frame de
 * la red (416x416, estirado desde el RGB completo): se escala al tamano
 * mostrado del <img>. [verificar alineacion en vivo la primera vez] */
const NN_SIZE = 416;
const detCanvas = $('det-overlay'), detCtx = detCanvas.getContext('2d');
let detClearTimer = null;

function drawDetections(dets) {
  const vr = videoEl.getBoundingClientRect();
  const pr = videoEl.parentElement.getBoundingClientRect();
  detCanvas.style.left = `${vr.left - pr.left}px`;
  detCanvas.style.top = `${vr.top - pr.top}px`;
  detCanvas.width = vr.width; detCanvas.height = vr.height;
  const sx = vr.width / NN_SIZE, sy = vr.height / NN_SIZE;

  detCtx.clearRect(0, 0, detCanvas.width, detCanvas.height);
  if (videoSrc.value !== '/oak/rgb/image_raw') return; // cajas solo sobre RGB

  detCtx.lineWidth = 2; detCtx.font = '12px system-ui';
  for (const det of dets) {
    const best = det.results?.[0];
    if (!best || best.score < 0.5) continue;
    const cx = det.bbox.center.position?.x ?? det.bbox.center.x;
    const cy = det.bbox.center.position?.y ?? det.bbox.center.y;
    const w = det.bbox.size_x * sx, h = det.bbox.size_y * sy;
    const x = cx * sx - w / 2, y = cy * sy - h / 2;
    const id = Number(best.class_id ?? best.id);
    const name = COCO[id] ?? `clase ${id}`;
    const d = Math.hypot(det.position.x, det.position.y, det.position.z);
    const label = `${name} ${d.toFixed(1)} m`;

    detCtx.strokeStyle = '#3fb950'; detCtx.strokeRect(x, y, w, h);
    const tw = detCtx.measureText(label).width + 8;
    detCtx.fillStyle = '#3fb950'; detCtx.fillRect(x, y - 16, tw, 16);
    detCtx.fillStyle = '#0d1117'; detCtx.fillText(label, x + 4, y - 4);
  }
}

let lastDetLog = 0;
topic('/oak/nn/spatial_detections', 'depthai_ros_msgs/msg/SpatialDetectionArray',
  { throttle_rate: 300 }).subscribe((m) => {
    $('det').textContent = m.detections.length;
    drawDetections(m.detections);
    clearTimeout(detClearTimer);
    detClearTimer = setTimeout(
      () => detCtx.clearRect(0, 0, detCanvas.width, detCanvas.height), 1200);

    const now = Date.now();
    if (now - lastDetLog < 3000) return;   // no inundar el log de eventos
    for (const det of m.detections) {
      const best = det.results?.[0];
      if (best && best.score > 0.6) {
        const id = Number(best.class_id ?? best.id);
        const name = COCO[id] ?? `clase ${id}`;
        const p = det.position;
        const d = Math.hypot(p.x, p.y, p.z);
        logEvent(`👁 ${name} a ${d.toFixed(1)} m (${Math.round(best.score * 100)}%)`, true);
        lastDetLog = now;
      }
    }
  });

/* ---------- radar lidar ---------- */
const RADAR_RANGE = 4.0; // m mostrados (el LD06 llega a ~8-12 m)

topic('/scan', 'sensor_msgs/msg/LaserScan', { throttle_rate: 200 })
  .subscribe((m) => {
    const c = $('radar'), ctx = c.getContext('2d');
    const w = c.width, cx = w / 2, S = (w / 2 - 8) / RADAR_RANGE;
    ctx.clearRect(0, 0, w, w);

    ctx.strokeStyle = '#30363d'; ctx.lineWidth = 1;
    for (let m_ = 1; m_ <= RADAR_RANGE; m_++) {
      ctx.beginPath(); ctx.arc(cx, cx, m_ * S, 0, 7); ctx.stroke();
    }
    ctx.beginPath();
    ctx.moveTo(cx, 8); ctx.lineTo(cx, w - 8);
    ctx.moveTo(8, cx); ctx.lineTo(w - 8, cx);
    ctx.stroke();

    // puntos del barrido (frame laser_frame: x adelante, CCW; adelante = arriba)
    ctx.fillStyle = '#3fb950';
    let nearest = Infinity;
    for (let i = 0; i < m.ranges.length; i++) {
      const r = m.ranges[i];
      if (!r || r < 0.05) continue;
      if (r < nearest) nearest = r;
      if (r > RADAR_RANGE) continue;
      const th = m.angle_min + i * m.angle_increment;
      ctx.fillRect(cx - r * Math.sin(th) * S - 1, cx - r * Math.cos(th) * S - 1, 2.5, 2.5);
    }

    // robot en el centro
    ctx.fillStyle = '#58a6ff';
    ctx.beginPath();
    ctx.moveTo(cx, cx - 7); ctx.lineTo(cx - 5, cx + 5); ctx.lineTo(cx + 5, cx + 5);
    ctx.closePath(); ctx.fill();

    $('radar-min').textContent = isFinite(nearest) ? `${nearest.toFixed(2)} m` : '—';
  });

/* ---------- instrumentos ---------- */
function drawHorizon() {
  const c = $('horizon'), ctx = c.getContext('2d');
  const w = c.width, h = c.height, r = w / 2 - 4;
  ctx.clearRect(0, 0, w, h);
  ctx.save();
  ctx.beginPath(); ctx.arc(w / 2, h / 2, r, 0, 7); ctx.clip();
  ctx.translate(w / 2, h / 2);
  ctx.rotate(-roll * Math.PI / 180);
  const off = pitch * 1.6;
  ctx.fillStyle = '#274b6d'; ctx.fillRect(-w, -h + off, 2 * w, 2 * h); // cielo
  ctx.fillStyle = '#4a3524'; ctx.fillRect(-w, off, 2 * w, 2 * h);      // suelo
  ctx.strokeStyle = '#c9d1d9'; ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.moveTo(-w, off); ctx.lineTo(w, off); ctx.stroke();
  ctx.restore();
  // avión fijo
  ctx.strokeStyle = '#f0c040'; ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(w / 2 - 30, h / 2); ctx.lineTo(w / 2 - 8, h / 2);
  ctx.moveTo(w / 2 + 8, h / 2); ctx.lineTo(w / 2 + 30, h / 2);
  ctx.stroke();
  ctx.beginPath(); ctx.arc(w / 2, h / 2, 3, 0, 7); ctx.stroke();
  ctx.strokeStyle = '#30363d'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.arc(w / 2, h / 2, r, 0, 7); ctx.stroke();
}

function drawCompass() {
  const c = $('compass'), ctx = c.getContext('2d');
  const w = c.width, h = c.height, r = w / 2 - 4;
  ctx.clearRect(0, 0, w, h);
  ctx.save();
  ctx.translate(w / 2, h / 2);
  ctx.strokeStyle = '#30363d'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); ctx.stroke();
  ctx.rotate(-yaw * Math.PI / 180);
  ctx.fillStyle = '#8b949e'; ctx.font = '14px system-ui';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const pts = [['N', 0, '#f85149'], ['E', 90, '#8b949e'], ['S', 180, '#8b949e'], ['O', 270, '#8b949e']];
  for (const [t, a, col] of pts) {
    ctx.save();
    ctx.rotate(a * Math.PI / 180);
    ctx.fillStyle = col;
    ctx.fillText(t, 0, -r + 16);
    ctx.restore();
  }
  ctx.restore();
  // flecha del robot (fija, apunta arriba)
  ctx.fillStyle = '#58a6ff';
  ctx.beginPath();
  ctx.moveTo(w / 2, h / 2 - 22);
  ctx.lineTo(w / 2 - 9, h / 2 + 12);
  ctx.lineTo(w / 2 + 9, h / 2 + 12);
  ctx.closePath(); ctx.fill();
}
drawHorizon(); drawCompass();

/* ---------- joystick virtual ---------- */
const MAX_LIN = 0.6;   // m/s enviados a stick lleno
const MAX_ANG = 10.0;  // rad/s — skid-steer: girar en el sitio pide PWM alto

const joy = $('joystick'), jctx = joy.getContext('2d');
let joyActive = false, joyX = 0, joyY = 0; // -1..1

function drawJoy() {
  const w = joy.width, cx = w / 2, R = w / 2 - 10, r = 34;
  jctx.clearRect(0, 0, w, w);
  jctx.fillStyle = '#0d111766';
  jctx.beginPath(); jctx.arc(cx, cx, R, 0, 7); jctx.fill();
  jctx.strokeStyle = '#30363d'; jctx.lineWidth = 2; jctx.stroke();
  jctx.fillStyle = joyActive ? '#58a6ffcc' : '#8b949e88';
  jctx.beginPath();
  jctx.arc(cx + joyX * (R - r), cx + joyY * (R - r), r, 0, 7);
  jctx.fill();
}
drawJoy();

function joyEvent(e) {
  const rect = joy.getBoundingClientRect();
  const t = e.touches ? e.touches[0] : e;
  let x = ((t.clientX - rect.left) / rect.width) * 2 - 1;
  let y = ((t.clientY - rect.top) / rect.height) * 2 - 1;
  const mag = Math.hypot(x, y);
  if (mag > 1) { x /= mag; y /= mag; }
  joyX = x; joyY = y;
  drawJoy();
}
function joyStart(e) { joyActive = true; joyEvent(e); e.preventDefault(); }
function joyEnd() { joyActive = false; joyX = 0; joyY = 0; drawJoy(); }

joy.addEventListener('pointerdown', joyStart);
joy.addEventListener('pointermove', (e) => joyActive && joyEvent(e));
joy.addEventListener('pointerup', joyEnd);
joy.addEventListener('pointercancel', joyEnd);

/* ---------- gamepad (ROG Ally / mando Xbox) ---------- */
let gpIndex = null;
let gpPrevButtons = [];

window.addEventListener('gamepadconnected', (e) => {
  gpIndex = e.gamepad.index;
  $('gamepad-badge').textContent = `🎮 ${e.gamepad.id.slice(0, 24)}`;
  $('gamepad-badge').className = 'badge ok';
  logEvent('Mando conectado');
});
window.addEventListener('gamepaddisconnected', () => {
  gpIndex = null;
  $('gamepad-badge').textContent = 'sin mando';
  $('gamepad-badge').className = 'badge';
});

function pollGamepad() {
  if (gpIndex === null) return null;
  const gp = navigator.getGamepads()[gpIndex];
  if (!gp) return null;

  // Botón A (0): alterna modo autónomo. Botón B (1): e-stop.
  const edge = (i) => gp.buttons[i]?.pressed && !gpPrevButtons[i];
  if (edge(0)) pubSetMode.publish({ data: currentMode === 'AUTO' ? 'TELEOP' : 'AUTO' });
  if (edge(1)) pubSetEstop.publish({ data: !estopOn });
  gpPrevButtons = gp.buttons.map((b) => b.pressed);

  const dz = (v) => (Math.abs(v) < 0.12 ? 0 : v);
  return { x: dz(gp.axes[0]), y: dz(gp.axes[1]) }; // stick izquierdo
}

/* ---------- bucle de teleop (10 Hz) ---------- */
setInterval(() => {
  const gp = pollGamepad();
  let x = 0, y = 0, active = false;

  if (joyActive) { x = joyX; y = joyY; active = true; }
  else if (gp && (gp.x || gp.y)) { x = gp.x; y = gp.y; active = true; }

  if (active) {
    pubWebVel.publish({
      linear: { x: -y * MAX_LIN, y: 0, z: 0 },
      angular: { x: 0, y: 0, z: -x * MAX_ANG },
    });
  }
  // Al soltar no se publica: el timeout de 0.5 s del twist_mux libera la
  // prioridad y el watchdog de cmd_vel_to_motors detiene el robot.
}, 100);
