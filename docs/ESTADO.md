# ESTADO del ecosistema — actualizado 2026-07-30

Documento vivo: fotografía del estado real de cada frente. El detalle
histórico vive en `cad/MEDIDAS.md` (bitácora maestra); esto es el resumen
para saber dónde estamos parados hoy.

## Vista rápida

| Frente | Estado | Siguiente paso |
|---|---|---|
| Waver (rover) | Stack de 6 servicios operativo; fix ipc:host aplicado | Sesión física: mapeo con slam_toolbox + primera navegación (docs/SESION_FISICA.md) |
| SOMA (brazos) | v0.1 en curso; **13 actuadores verificados desde la Jetson**; workbench de calibración operativo | Recentrado mecánico de horns + captura de ceros/límites; medidas con calibrador (en camino) |
| Jetson Orin Nano Super | **LISTA**: JetPack 7.2 en NVMe, MAXN_SUPER activo, SSH/RDP headless | Ollama + jetson-device-skills + OpenClaw |
| OAK-D Lite en Jetson | 3 demos funcionando (detección espacial, ArUco, profundidad) | Medir marcador real del cubo; verificar USB3 (SUPER) |
| Second brain | Graphiti + FalkorDB corriendo en Docker | Alimentar con group_id por proyecto |

## Sesión 2026-07-30 — Jetson lista y primer metal movido desde ella

### Jetson Orin Nano Super: bring-up completo

- JetPack 7.2 instalado en NVMe con el ISO installer nuevo (aprendizaje: el
  ISO va en un pendrive USB, no en el disco destino; el instalador
  particiona el NVMe). Firmware UEFI 36.4.3 de fábrica, compatible.
- **Modo Super desbloqueado de verdad**: la placa (módulo p3767-0005)
  arrancaba con el DTB genérico y el script de NVIDIA re-enlazaba el perfil
  de potencia normal en cada boot. Fix: línea `FDT` en
  `/boot/extlinux/extlinux.conf` apuntando al DTB `-super` → el sistema se
  identifica `p3767-0005-super` y **MAXN_SUPER queda persistente**.
- Acceso: SSH con llaves y reserva DHCP (práctica estándar del taller:
  reserva en router + alias en ~/.ssh/config + mDNS solo como comodidad).
- Escritorio remoto: gnome-remote-desktop descartado (NoMachine v10 pasó a
  suscripción; el Remote Login de GNOME falla la redirección de sesión con
  clientes macOS). Solución final: **xrdp headless**, tras corregir un bug
  de fábrica de JetPack: `~/.xsessionrc` está escrito en bash pero Xsession
  lo lee con dash → la sesión moría al instante. Wrapper POSIX y a andar.

### SOMA: los brazos ya obedecen a la Jetson

- PCA9685 conectado al header 40 pines (pines 1/3/5/6, bus i2c-7 — mismo
  cableado físico que en la Pi). UBEC 6 V como siempre; V+ jamás de la placa.
- Nuevo `scripts/servo_workbench.py` en el repo soma-arms: sliders web para
  calibrar servo por servo. Seguridad codificada: arranca desarmado y en
  FULL_OFF, un solo servo activo a la vez, banda 500-2500 us, **rampa de
  50 Hz en el servidor** (400 us/s: el navegador solo fija objetivos, el
  cable nunca ve saltos), botón ALL OFF, y el L16 con física propia (banda
  1000-2000 us, rampa 140 us/s igual a sus 20 mm/s reales, auto-release a
  los 2 s de asentarse: el acuñamiento de julio es irrepetible desde aquí).
- **Los 13 actuadores (12 MG996R + L16) verificados funcionando desde la
  Jetson.** Calibración de ceros/límites iniciada con JSON limpio.
- Pendientes abiertos: recentrar los horns en las carcasas (cero eléctrico
  = cero mecánico, servo a 1500 us y re-splinear), completar la captura
  zero/min/max de los 13, y diagnosticar la muñeca izquierda (retiene con
  potencia sin señal; diferencial pendiente: ¿mecánico, servo o fila?).

### OAK-D Lite sobre la Jetson: percepción funcionando

- Stack instalado sin tocar el sistema: depthai 2.32 (v2 estable a
  propósito), OpenCV 5 wheel ARM64, blobconverter con el modelo cacheado
  (no depende de internet), regla udev de Movidius aplicada.
- **3 demos operativas** en `~/soma-demos/` de la Jetson:
  1. Detección de objetos con distancia 3D (red corriendo en el VPU de la
     cámara, la Jetson libre).
  2. ArUco con pose, usando la calibración intrínseca de fábrica. Integrado
     el **cubo Alpha 1S** (caras de 10 cm, marcadores ids 7-10 de ~7.0 cm,
     etiquetados por cara). Verificar el tamaño impreso con regla.
  3. Profundidad colorizada en vivo (nube de puntos pospuesta: open3d sin
     wheel ARM64; el script la activa solo si aparece).
- Verificar en próxima corrida: que `USB:` reporte SUPER (USB3); si dice
  HIGH, cambiar puerto/cable.

## Arquitectura de cómputo (se mantiene)

Pi 5 = control y seguridad (ROS 2, PCA9685 del rover). OAK-D = percepción
en su propio VPU. **Jetson = caja de inferencia** (LLMs locales, futuro
VLA) y ahora también banco de calibración de SOMA. El LLM pesado sigue en
la Mac. Nada de esto cambia el roadmap de SOMA: v0.1 cierra con el
calibrador, v0.2 con el driver ROS moviendo metal armado.
