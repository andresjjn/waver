# WAVER CRAB — Medidas maestras para Onshape

Hoja de referencia para reconstruir el ensamblaje en Onshape Education.
Fuente: `waver.urdf.xacro` + `plataforma.scad`. Convención REP-103: X adelante,
Y izquierda, Z arriba. **Origen del montaje: centro de la TAPA del rover.**
Todo en **mm**. Cargar como *Variables* de Onshape (menú `x=`) para que el
diseño sea paramétrico como el SCAD.

## Chasis (del URDF — verificado contra robot real)

| Variable | Valor | Nota |
|---|---|---|
| `chasis_l` | 194 | largo |
| `chasis_w` | 110 | ancho sin ruedas |
| `chasis_h` | 55 | alto [calibrar] |
| `clearance` | 20 | suelo → panza [calibrar] |
| `rueda_r` / `rueda_w` | 30 / 26 | |
| `rueda_sep` / `rueda_base` | 125 / 110 | entre centros / entre ejes |

## Plataforma / bandeja

| Variable | Valor | Nota |
|---|---|---|
| `plat_l` × `plat_w` × `plat_t` | 200 × 144 × 4 | bandeja atornillada a la tapa |
| Patrón tornillos M3 | (±70, ±35) y (0, ±42) | **[calibrar] — medir en la tapa real** |
| `tornillo_d` | 3.4 | paso M3 |

## Batería taladro (bahía trasera pasante, lo más bajo)

| Variable | Valor | Nota |
|---|---|---|
| `bat_l` × `bat_w` × `bat_h` | 116 × 76 × 62 | pack DeWalt-compat **[calibrar al llegar]** |
| `cuna_h` | 14 | cuna adaptadora bajo el pack **[calibrar]** |
| `bay_cx` | −38 | centro X de la bahía (atrás) |
| `bay_pared` / `holgura` | 3 / 1.0 | |

## Sensores

| Variable | Valor | Nota |
|---|---|---|
| LD06 lidar | ⌀38 × h34 | torre periscopio: `torre_h` = 58, base ⌀52 → top ⌀44 |
| **Regla de oro** | — | **nada cruza el plano de barrido del lidar** |
| OAK-D Lite | 17 × 91 × 28 | visor: x=94, z=26, tilt=8° (ojos asoman del caparazón) |
| URDF actual | lidar_z=85, oak_x=85, oak_z=60 | ⚠️ al montar el CRAB habrá que **actualizar el URDF** (lidar sube a torre) |

## Servos (inventario)

| Servo | Cuerpo | Extras |
|---|---|---|
| MG996R | 40.7 × 19.7 × 42.9 | flange 54.5 largo, eje descentrado 10.3 hacia el frente |
| S3003 | 40.0 × 20.0 × 38.0 | mismo patrón de eje aprox |

**Horns comprados (disco aluminio 25T)**: ⌀20 mm, 4 agujeros **M3 roscados en
patrón de 14 mm**, tornillo central M3×8 al eje (rosca interna del MG996R) —
los eslabones impresos se diseñan con ese patrón de 4×M3 a 14 mm.

## Brazos cangrejo — cadena ACTUALIZADA 2026-07-06 (6 DOF por lado)

`yaw S3003 → hombro MG996R → codo MG996R → muñeca-pitch S3003 → kit LG-KT
(rotación 180° + pinza, servos HS-422 incluidos)`

**Pinza resuelta con hardware en mano**: 2× Lynxmotion Little Grip Kit (LG-KT)
del inventario de Andrés — apertura 3.3 cm, 2× HS-422 por kit (4.8-6 V, mismo
riel UBEC), montaje patrón Lynxmotion.

**CAD oficial de la pinza ENCONTRADO (2026-07-06, verificado)**:
- STEP oficial: [lg.step.zip](https://wiki.lynxmotion.com/info/wiki/lynxmotion/download/servo-erector-set-robots-kits/ses-v1-cad/WebHome/lg.step.zip)
  (página madre: [SES-V1 3D CAD Models](https://wiki.lynxmotion.com/info/wiki/lynxmotion/view/ses-v1/ses-v1-system/ses-v1-cad/) — también IGES y Parasolid)
- Servo Hitec estándar (HS-422): `servo.step.zip` y horns `servohorns.step.zip` en la misma página
- Alternativa comunidad: [GrabCAD Little Grip](https://grabcad.com/library/lynxmotion-little-grip-1) (SolidWorks, ensamblada)
- Montaje real: 3 tornillos **4-40 × 3/8"** con tuercas a través de placa (el cuerpo del
  servo bloquea el 4º agujero) — documentado en la [guía del brazo AL5A](https://wiki.lynxmotion.com/info/wiki/lynxmotion/view/ses-v1/ses-v1-robots/ses-v1-arms/al5a-arm-rev-2-1/)
- Atajo comprable: placa adaptadora oficial [LGA-KT en RobotShop](https://www.robotshop.com/products/lynxmotion-little-grip-kit-lga-kt) (~US$8)
- ⚠️ Descargar desde navegador (Cloudflare bloquea scripts); licencia: solo uso virtual/personal.
Solo se diseñan los 3 eslabones del medio — base: brazo Onshape de
vishnusivampeta (CC BY 4.0). Los 2× MG996R del carrito pasan a repuestos.
⚠️ HS-422 = engranaje plástico ~3.3 kg·cm: carga máx 100-150 g respetada.

| Variable | Valor | Nota |
|---|---|---|
| Anclaje hombro | x=12, y=±(plat_w/2 − 12) | parten del centro, a lado y lado |
| `l_humero` | 78 | hombro → codo |
| `l_ante` | 66 | codo → muñeca |
| `l_garra` | 72 | muñeca → punta de pinza |
| Pose demo | yaw 52°, hombro 26°, codo −58°, muñeca −14°, pinza 24° | para validar rangos en Onshape con *joint limits* |

## MuñecaCRAB v1 — pieza nueva diseñada (sesión nocturna 2026-07-07)

Part Studio **MunecaCRAB** en la copia de Andrés del brazo 6DOF
([elemento c4d69b72](https://cad.onshape.com/documents/859a0f262528fc744c10b004/w/0f122365df7b490cd4a487c1/e/c4d69b72efbd309b1783fae4)).
Reemplaza TODO el mecanismo interno del antebrazo original (tubo JointFour +
micro 9g en corredera, ya suprimidos): la muñeca-roll pasa a un MG996R directo.

**Decisión de cadena**: el diseño original NO tiene muñeca-pitch — su roll era
el tubo central. Fieles a eso: `muñeca-roll MG996R (eje colineal al antebrazo)
→ paleta adaptadora → pinza LG-KT usada SOLO como garra` (su servo de rotación
180° queda de repuesto — sería roll redundante).

Geometría (un solo sólido, imprimible sin soportes salvo pared izquierda):
| Elemento | Medida | Nota |
|---|---|---|
| Copa-abrazadera | Ø40.4 ext / Ø34.4 int × 10 alto | calza sobre anillo punta jaula (Ø34) con holgura 0.4 |
| Techo | Ø40.4 × 3, a ras | fusionado dentro del faldón (inserción útil 7 mm) |
| Cuna servo | int 41.0×20.2, paredes 3, alto 28 | MG996R vertical, eje ARRIBA |
| Offset cuna | centro caja a −10.2 mm en X | el EJE del servo queda colineal con el eje del antebrazo |

**Pendiente v2** (próxima sesión):
1. 2 agujeros Ø2.9 pasantes en el faldón a z=3.5 (prisioneros M3 que muerden el
   anillo) — Sketch 4 ya dibujado y acotado; el corte no se pudo seleccionar por
   automatización → **taladrar a mano** o completar con mouse real.
2. Pestañas de flange + 4 agujeros patrón MG996R (~49.4×10 mm **[calibrar con
   el servo físico]**).
3. Refuerzo/gusset bajo el extremo izquierdo de la cuna (vuela 13.6 mm fuera
   del disco por el offset del eje).
4. **PaletaLGKT**: disco Ø30×4 — 4×Ø3.2 en círculo Ø14 (al horn) + 3×Ø3.2 para
   4-40 al patrón de la placa trasera del LG-KT **[calibrar con la pinza física
   de Andrés]** + pasante central Ø6.

## CRAB Ensamble — brazos dobles montados (madrugada 2026-07-07) ✅

Assembly **"CRAB Ensamble"** ([elemento 8cfee54b](https://cad.onshape.com/documents/859a0f262528fc744c10b004/w/0f122365df7b490cd4a487c1/e/8cfee54be09e214bc96895ce)):
**PlacaCRAB (200×180×4) fija + 2 instancias del brazo completo, cada una a ±45°.**

| Elemento | Mate | Valores |
|---|---|---|
| PlacaCRAB | Fix | insertada en el origen (centro placa = origen) |
| Brazo 1 | Fastened → origen ensamble | offset (−4, −6.4, +0.7) cm, Rotate Z **+45°** |
| Brazo 2 | Fastened → origen ensamble (vía mate connector en origen de instancia) | offset (−4, +6.4, 0) cm, Rotate Z **−45°** |

Notas de diseño:
- Placa 180 de ancho (vs 144 de la bandeja): las bases 90×90 rotadas 45°
  (diagonal 127) exigen centros a ±64 → los pods cuelgan ~38 mm por fuera de
  cada costado = estética cangrejo intencional. **[calibrar] al armar**: si se
  prefiere sin voladizo, girar solo la tornamesa (servo yaw) y dejar bases a 0°.
- Separación entre diamantes: 0.8 mm en la línea central (¡justo sin chocar!).
- El Z de un brazo usa +0.7 (conector en cara superior de su base) y el otro 0
  (conector en origen de instancia = fondo de base) — mismos 4 mm de placa.
- Técnica ganadora para automatización: mate connector explícito en el origen
  de instancia + conector del origen del ensamble + offsets numéricos + campo
  "Rotate about Z" del Fastened (acepta ángulo arbitrario — ahí van los 45°).

## Checklist de la sesión Onshape

1. Crear documento "WAVER CRAB" + tabla de Variables con lo de arriba.
2. Importar STEP reales: OAK-D Lite (oficial Luxonis), LD06, MG996R, S3003,
   pack DeWalt, Raspberry Pi 5 (oficial).
3. Modelar bandeja → bahía → torre → visor → caparazón (mismo orden que el SCAD).
4. Ensamblar con *mates* revolute en hombro/codo/muñeca/pinza **con límites**
   (aquí Onshape gana: simula rangos de movimiento reales).
5. Exportar: STL por pieza para imprimir; a futuro `onshape-to-robot` → URDF.

**[calibrar] pendientes de Andrés con calibrador**: patrón de tornillos de la
tapa, alto real del chasis, pack real + cuna cuando lleguen.

## Modelos CAD para importar (verificados 2026-07-06)

| Componente | Enlace | Formato / fuente |
|---|---|---|
| OAK-D Lite PCBA | [DM9095_PCBA.STEP](https://oak-files.fra1.cdn.digitaloceanspaces.com/OAK-D-Lite/DM9095_PCBA.STEP) (15 MB) | STEP **oficial Luxonis**, sin cuenta |
| OAK-D Lite carcasa | [DM9095_enclosure.stp](https://oak-files.fra1.cdn.digitaloceanspaces.com/OAK-D-Lite/DM9095_enclosure.stp) (8.5 MB) | STEP **oficial Luxonis**, sin cuenta |
| Raspberry Pi 5 | [RaspberryPi5-step.zip](https://datasheets.raspberrypi.com/rpi5/RaspberryPi5-step.zip) | STEP **oficial RPi**, sin cuenta |
| LD06 lidar | [GrabCAD LD06 + bracket Pi](https://grabcad.com/library/ldrobot-ld06-360-lidar-module-raspberry-pi-mounting-bracket-1) | STEP comunidad (login gratis), 1.6k descargas |
| MG996R | [GrabCAD mg996r-servo-3](https://grabcad.com/library/mg996r-servo-3) | STEP + 4 horns, 13k descargas |
| S3003 | [GrabCAD servo-futaba-s3003-1](https://grabcad.com/library/servo-futaba-s3003-1) | STEP + IGES, 4.9k descargas |
| Pack DeWalt XR 5Ah | [GrabCAD DCB184](https://grabcad.com/library/dewalt-battery-dcb184-18v-xr-5ah-1) | .stp, el que mejor encaja con 116×76×62 |
| Cuna DeWalt | [GrabCAD battery-holder](https://grabcad.com/library/battery-holder-dewalt-1) | .stp, calidad modesta — **verificar riel contra pack real** |
| Chasis Wave Rover | [WAVE_ROVER_MODEL_STL.rar](https://files.waveshare.com/upload/e/ec/WAVE_ROVER_MODEL_STL.rar) (wiki oficial) | ⚠️ solo STL (malla, no editable) — usar como referencia visual + plano de la tapa del wiki |

## Búsqueda brazo COMPACTO MG996R (2026-07-07 — el de vishnu quedó grande)

Motivo: el brazo de vishnu es de escritorio (alcance ~40 cm, torreta de 5
servos arriba = pesado y CG alto para un rover de 194×110). Candidatos:

| Diseño | Servos | Tamaño/clase | CAD | Licencia | Veredicto |
|---|---|---|---|---|---|
| ⭐ **ARA — Another Robot Arm** ([printables 70258](https://www.printables.com/model/70258-ara-another-robot-arm), [GitHub](https://github.com/Hobbesdcc/RobotArm)) | **3× MG996R** + 1 micro (efector) | clase EEZYbot: base ~⌀80-100, alcance ~250-280 | STL (hecho **en Onshape**, fuente no publicada) | CC BY-NC-SA 4.0 | **RECOMENDADO** — topología paralelogramo: los 3 servos viven EN LA BASE → CG bajo, ideal rover; micro del efector se reemplaza por LG-KT |
| Emre Kalem ([makerworld 1134925](https://makerworld.com/en/models/1134925-robotic-arm-with-servo-arduino)) | 4× MG995/996R + 3× MG90S | escritorio (rodamientos 608+6203) | STL/CAD | ❌ estándar MakerWorld: **prohíbe derivados/compartir mods** | El más probado (6.3k builds, [port ESP32](https://github.com/peterz0310/robot-arm)) pero grande y licencia incompatible con nuestro GitHub |
| Robot Arm MG996R ([cults3d](https://cults3d.com/en/3d-model/gadget/robot-arm-mg996r)) | 5× MG996R | serial (como vishnu) | STL | ? (Cults bloquea acceso) | Misma topología pesada que ya descartamos |
| Compact Robot Arm ([printables 818975](https://www.printables.com/model/818975-compact-robot-arm-arduino-3d-printed)) | lista solo en video YouTube | compacto | STL | ? | Documentación floja |
| Brazo Arduino MG996r ([makerworld 1055189](https://makerworld.com/en/models/1055189-arduino-mg996r-arm)) | 6× MG996R | ? | STL | CC BY-SA ✓ | "Work in progress", sin instrucciones ni BOM |

### Giro 2026-07-07: brazos de ALUMINIO comprados (en vez de imprimir)

**Familia ROT3U 6DOF** — el estándar de brackets de aluminio diseñado para
MG995/MG996R, compatible con nuestros **horns 25T ya comprados**:

| Opción | Contenido | Precio | Fuente |
|---|---|---|---|
| ROT3U **sin servos** | 490 g de brackets: 5 multifunción + 4 U-largos + 1 L + 3 U-cintura + 4 rodamientos + garra + tornillería | US$49 | [diymore.cc](https://www.diymore.cc/products/diymore-rot3u-6dof-aluminium-robot-arm-mechanical-robotic-clamp-claw-kit-for-arduino-mega2560) / [Amazon B01LW0LUPT](https://www.amazon.com/diymore-Aluminium-Mechanical-Robotic-Arduino/dp/B01LW0LUPT) |
| ROT3U + 6× MG996R + horns 25T | kit completo | ~US$100 | [Amazon B0CJ4WR949](https://www.amazon.com/diymore-Aluminium-Mechanical-Robotic-Unassembled/dp/B0CJ4WR949) |
| Specs config completa 6DOF | alcance 355 mm, alto 460 mm, garra abre 55 mm | — | demasiado grande para el rover tal cual |

### ✅ DECISIÓN FINAL 2026-07-07: 2× brazo completo aluminio robusto (ThanksBuyer)

Andrés eligió **dos brazos 6DOF COMPLETOS** (no versión corta) — razón: módulo
de aprendizaje reutilizable (rover hoy; péndulo invertido / cuádruped mañana),
invertir en calidad una vez.

**Producto**: [Brazo 6DOF metal robusto, item 1005007215923987](https://es.aliexpress.com/item/1005007215923987.html) — ThanksBuyer
(5.251 seguidores, 91.9% pos). Variante **"Arm Only"** (sin servos).
- Precio COP 286.704 c/u + envío COP 46.860 → **2 brazos ≈ COP 620.000 (~US$155)**
- Llega 22 jul–1 ago (25 días). Reseñas 3.7★ pero la única negativa ("sin
  instrucciones/código") es irrelevante: usamos ROS2 + ESP32/PCA9685 propios.
- Placas gruesas = 1.37 kg c/u (2.7 kg el par sobre el rover → extender lento;
  el peso no importa cuando vaya a base fija/péndulo).

**✅ COMPATIBILIDAD MG996R VERIFICADA (ficha oficial del vendedor)**:
| | Frame diseñado p/ (servo 25 kg) | MG996R | Encaja |
|---|---|---|---|
| Tamaño | 40 × 20,5 × 40,5 mm | 40,7 × 19,7 × 42,9 | ✅ misma clase estándar 40×20 |
| Spline | **25T** | **25T** | ✅ horns 25T comprados sirven directo |

- Servo count: 2 brazos × 6 = 12 servos; Andrés tiene **13 MG996R** → +1 repuesto.
- ⚠️ Torque: frame pensado p/ 25 kg·cm; MG996R da ~10 → hombro/base son las
  juntas a vigilar con carga. Upgrade no destructivo: cambiar SOLO ese servo por
  **DS3225 (25 kg, mismo cuerpo 40×20, mismo 25T)** si hace falta. Sin rediseño.
- Las 2× LG-KT quedan como opción para reemplazar la garra nativa del brazo.
- ⛔ CAD Onshape CRAB con brazo vishnu → OBSOLETO (era maqueta). Real = aluminio.
  Solo se conserva la idea de placa de montaje sobre el rover a ±45°.

---
**Listado alternativo delgado/liviano (Youfang) — descartado por peso pero útil de referencia:**
[item 1005005352898104](https://es.aliexpress.com/item/1005005352898104.html) — ROT3U 6DOF exacto (estilo que le gusta a Andrés):
- Variante "Only arm frame" (sin servos, usa nuestros 6× MG996R): **COP 118.475**
- **Envío a Colombia COP 75.301** (95.8% ≤ 25 días) → total **~COP 194.000 (~US$49)**
- 4.5★, 37 reseñas, 303 vendidos; vendedor 92.8% pos, 6280 seguidores
- Bonus: guía de armado clara, **modelo 3D en Fusion360**, tornillería de sobra,
  acepta upgrade a servos 25-40 kg·cm en la base (confirmado por reseña)
- ⚠️ Reseña honesta: 2 juntas son "acoplador sobre eje estriado" = con juego;
  el eslabón de extensión cuesta fijarlo solo con prisioneros → imprimir
  soportes estabilizadores + usar arandelas nyloc/loctite. Relevante porque
  el brazo carga peso; en nuestros brazos CORTOS el brazo de momento es menor.
- Comparación: el listado que Andrés mandó primero (Hydraulic Tool Store) era
  COP 191k + **COP 285k de envío** = COP 477k. Este es 60% más barato puesto.
- Alternativas más baratas sin verificar envío: [COP 82.510 4.6★ 109 vend](https://es.aliexpress.com/w/wholesale-6DOF-aluminum-robot-arm-MG996R.html)
  y [COP 131.250 "excluido Servo" 4.6★ 158 vend].

**Plan CRAB-aluminio (recomendado): 1 kit ROT3U → DOS brazos cortos de 3DOF**
- Los brackets son LEGO de aluminio: cada brazo corto = 1 U-cintura (yaw) +
  1 multifunción + 1 U-largo (hombro) + 1 multifunción + 1 U-largo (codo).
  El kit trae piezas para los dos brazos (sobra la garra → repuesto).
- Cadena por brazo: yaw → hombro → codo → **LG-KT completo (roll + pinza)**
  = 5 DOF útiles. 3× MG996R por brazo = 6 total (inventario ✓).
- Alcance resultante ~200-250 mm y ~570 g/brazo con servos → 1.14 kg total,
  viable para el rover; con 355 mm completos serían 1.6+ kg y volcadura.
- La PaletaLGKT cambia de interfaz: horn 25T → placa trasera LG-KT (igual),
  y el bracket multifunción del extremo ya tiene patrón de tornillos M3.
- Guía de armado de referencia: [AutomaticAddison DIY 6DOF](https://automaticaddison.com/how-to-build-a-diy-aluminium-6-dof-robotic-arm-from-scratch/)
- Nota: brazos MG996R *pre-ensamblados* casi no existen (los ensamblados usan
  servos de bus propietarios, p.ej. Hiwonder). El kit se arma con tornillos
  en 1-2 h, sin impresión ni pegamento.

**Análisis CRAB con ARA** (plan impresión 3D, alternativa): 2 brazos = 6×
MG996R (inventario ✓). Cadena:
yaw base → hombro → codo (paralelogramo, efector siempre horizontal) →
PaletaLGKT → **LG-KT completo con SUS DOS servos** (rotación 180° = roll +
pinza) = 5 DOF controlables por brazo. Torque: MG996R (9-11 kg·cm) en
topología diseñada para MG90S (2.2) ≈ 4× margen → carga ~300 g en punta ✓.
CC BY-NC-SA: uso personal OK; publicar mods exige misma licencia y no
comercial (compatible con repo hobby).

| Diseño | Enlace | Por qué |
|---|---|---|
| ⭐ Brazo 6DOF MG996R (vishnusivampeta) | [thing:6152986](https://www.thingiverse.com/thing:6152986) | **Fuente editable en Onshape**, CC BY 4.0 — copiar documento y adaptar eslabones/portaservos |
| ⭐ Pinza TungTran MG996R | [thing:6900287](https://www.thingiverse.com/thing:6900287) | Garra probada para nuestro servo exacto, CC BY-SA, tornillería M3 |
| Pinza flexible (plan B) | [cults3d flexible gripper](https://cults3d.com/en/3d-model/various/robot-gripper-flexible-servo-mg995-mg996r) | Mordazas compliant — agarra irregulares sin control de fuerza |
| Brazo HowToMechatronics | [tutorial+STEP](https://howtomechatronics.com/tutorials/arduino/diy-arduino-robot-arm-with-smartphone-control/) | 3× MG996R hombro/codo como el CRAB; STEP escalable, BOM y video |
| EEZYbotARM MK2 | [thing:1454048](https://www.thingiverse.com/thing:1454048) | Miles de makes; [librería Python IK](https://github.com/meisben/easyEEZYbotARM); ⚠️ CC BY-NC |
| Bracket MG996R press-fit | [printables 11782](https://www.printables.com/model/11782-hobby-servo-holder-for-mg996r) | Referencia de portaservo para hombros |
| Rover + brazo 6DOF | [makerworld 1342319](https://makerworld.com/en/models/1342319-rc-rover-with-robot-arm-6-dof) | Lo más parecido publicado — **no existe rover de brazos dobles: el CRAB sería original** |

---

## F0 · SALA DE DECISIONES — Plan Maratón (2026-07-07)

Contexto: se definió el plan de 8 fases hacia la demo maratón (pick&place
autónomo en diorama + carga autónoma + días corriendo sin intervención).
F0 = cerrar decisiones de arquitectura ANTES del primer URDF. Bitácora:

### ✅ D1 — Configuración del módulo superior: **B DIRECTO (torso elevable)**
- Arquitectura "dos pisos" del módulo portable (mochila trasladable a
  futuras plataformas: orugas, péndulo, cuadrúpedo):
  - **Sub-chasis (NO sube)**: batería, Jetson, PCA9685, LiDAR, base de
    columna + rieles. Lo pesado abajo, ventilación fácil.
  - **Torso elevado (SÍ sube, presupuesto ≤4 kg)**: 2 brazos (~2 kg),
    placa-torso, cámara OAK como "cara" (~2.5-3 kg total ✓).
- Argumento decisivo: con MG996R los brazos DEBEN trabajar recogidos
  (10 kg·cm ÷ 30 cm ≈ 330 g estirado ≈ nada). La cobertura vertical la da
  la columna, no el estiramiento → cobertura fuerte 10-54 cm (vs 0-30 del
  plano fijo) y servos fríos = vida útil para la maratón.
- Se descartó "B por etapas" (placa plana primero): Andrés prefiere un solo
  esfuerzo mecánico desde el inicio.
- ⚠️ Riesgo #1 mecánico: paralelismo de rieles (binding). Mitigación:
  varillas lisas 8mm + rodamientos LM8UU (estándar impresora 3D) + diseño
  con ajuste de paralelismo.

### ✅ D1b — LiDAR: **fijo en el sub-chasis** (no sube con el torso)
- SLAM 2D exige altura de escaneo constante; si el LiDAR sube/baja el mapa
  se corrompe. Sigue siendo parte del módulo portable.

### 📐 L16 REAL confirmado: **Actuonix L16-140-63-6-R** (ya comprado)
| Parámetro | Valor | Implicación |
|---|---|---|
| Carrera | 140 mm | banda de trabajo desplazable 14 cm |
| Fuerza máx (63:1) | 100 N (~10 kg) | 3× margen p/ torso 3 kg |
| Retención s/ corriente | **46 N (~4.6 kg)** | ⛔ masa elevada ≤4 kg (regla de diseño) |
| Velocidad | 20 mm/s | carrera completa en 7 s |
| Alimentación | **6 V** | mismo riel que los servos |
| Interfaz "R" | **PWM RC 1-2 ms** | = servo #13 del PCA9685, cero electrónica extra |
| Feedback | lazo interno, NO legible | software asume comandado=alcanzado tras t de viaje |
| Duty cycle | 20% máx | ciclo demo ~2 min con 2 movs (14 s) ≈ 12% ✓ |

### 🛒 Compras chicas para la columna (agregar al próximo pedido)
- 2× varilla lisa acero 8 mm × ~250-300 mm (rectificada, tipo impresora 3D)
- 4× rodamiento lineal LM8UU
- 2× soporte SHF8 o SK8 (fijación de varilla)
- Tornillería M3/M4 + tuercas nyloc

### ⏳ Decisiones pendientes de F0
- D2: reparto de cómputo Pi↔Jetson + mejoras de software que desbloquea
- D3: energía del módulo (riel 6V p/ 12 servos + L16; batería módulo vs plataforma)
- D4: interfaz módulo↔plataforma (contrato mecánico/eléctrico/datos)
- D5: reestructura de PLAN.md con el plan de 8 fases

### ✅ D2 — Cómputo: **Jetson Orin Nano Super 8GB SOLA, migración por etapas**
- Regla que ordenó el debate: los topics RGB-D no viajan bien por red (cientos
  de Mbps) → la percepción vive donde está enchufada la cámara → el OAK se
  muda a la Jetson en cualquier escenario.
- Destino: TODO en la Jetson (8GB unificada mata la saga del freeze de la Pi;
  DDS en localhost; 1 solo punto de falla para la maratón; 7/15/25W config.).
- Ejecución: Jetson se configura en la mesa (fuente de pared), migración
  servicio por servicio (1º OAK/percepción, 2º SLAM/Nav2, 3º base+web) con la
  Pi operando. Al final la Pi queda de REPUESTO CALIENTE o libre.
- Desbloqueos: Isaac ROS (cuVSLAM, nvblox, AprilTag GPU), YOLO en GPU o en
  VPU del OAK (liberando GPU p/ LLM local + Whisper + Piper).
- Sub-decisión diferida a F5 con benchmark real: tamaño del LLM (3B holgado
  vs 7B apretado) según presupuesto de los 8GB compartidos.
- JetPack 6 = Ubuntu 22.04 = ROS2 Humble nativo ✓; I2C PCA9685 en header 40
  pines ✓; Docker arm64 portable ✓.

### ✅ D3 — Energía: **fuente única DeWalt DENTRO del módulo "TORSO"** (arquitectura de Andrés)
- Nombre oficial del módulo: **TORSO** = de la Jetson hacia arriba, atornillado
  al rover, batería incluida. Autocontenido de verdad.
- Pack DeWalt 6Ah en el sub-chasis, junto a la Jetson (⚠️ regla térmica CAD:
  pack AL LADO al mismo nivel, o encima con 3-4cm + deflector — el exhaust de
  la Orin no puede bañar el litio 24/7).
- **El robot vive siempre**: Jetson nunca se apaga. En dock = modo espera
  (0 servos, 0 motores, 0 L16) hasta batería llena. Espera ≈ 8-12W.
- Dock propio con **pogo pins (ya comprados)**: entrega carga + vigilancia.
  Fuente dock ~100W. Cargar a **20.4V (≈85-90%)**, no 21V: packs de taladro
  no balancean; menos estrés = muchos más ciclos p/ la maratón.
  ⚠️ verificar rating de corriente de los pogo pins (típ. 1-3A c/u → 3-4
  pines en paralelo por polo). Fusible + termistor lado robot; INA3221
  confirma corriente de carga real como señal de acople exitoso.
- Bus de carga = bus del pack → cero microcortes en acople/desacople.
  El buffer (UPS) resulta innecesario.
- **UPS 3S viejo: fuera de la cadena crítica.** Se retira si el peso molesta
  (eran 150g de lastre gratis, nada más). Rover recibe 12V desde el TORSO.
- Riel 6V: 2× UBEC 8-10A, **uno por brazo** (aislamiento de brownout);
  L16 (650mA) cuelga del UBEC menos cargado.
- Costo de CG aceptado: pack a ~17cm (−2° de vuelco vs bahía baja) a cambio
  de portabilidad total. Regla operativa: **navegar con torso ABAJO**
  (θ≈18° vs 14° arriba) — invariante del behavior tree (F7).
- ⚠️ PACKS REALES (Andrés, confirmado 2026-07-08): **2× DeWalt DCB203-B3 =
  20V MAX 2.0Ah cada uno ≈ 36Wh nominales** (5S1P 18650, 18V nom × 2Ah).
  NO son 6Ah — la estimación previa de 120Wh estaba inflada 3×.
- Presupuesto energético (estimado; MEDIR con INA3221 en F4 antes del dock):
  - Consumo del pack (con pérdidas buck+UBEC ~10-15%) por estado:
    standby brazos-sin-energía ~20W · navegando torso-abajo ~45W ·
    manipulando detenido ~65W · **mezcla real de maratón ~47W**.
  - Autonomía con UN DCB203 (36Wh al 85% ≈ 30Wh útiles): standby ~1.5h ·
    **trabajo activo ~40 min** · manipulando ~28 min.
  - 🃏 Comodín = 12× MG996R: en pose compacta o depotenciados casi no gastan;
    sosteniendo torque pueden sumar 40-70W. Mitigación de diseño: NUNCA todo
    a la vez (navegar=motores sí/servos plegados; manipular=detenido) +
    depotenciar servos ociosos. Incertidumbre ±100% hasta medir.
  - RESCATE: un 2Ah recarga en ~40-45 min → ritmo ~40min trabajo : ~45min
    carga ≈ **1:1**. La maratón NO se rompe; cambia a ciclos cortos y más
    frecuentes → más repeticiones de docking (bueno para la métrica estrella).
  - Opciones con los 2 packs: (1) 1 pack + docking frecuente (simple, hoy);
    (2) 2 bahías uso SECUENCIAL con conmutador A/B → ~80 min (⛔ nunca en
    paralelo directo: cross-charge entre packs, necesita aislamiento);
    (3) para F8 comprar 1× DCB205 5Ah (~90Wh→~2h) o DCB206 6Ah (~108Wh→~2.4h),
    mismo cargador/cuna, + lastre bajo. Los 2Ah quedan de banco/desarrollo.
  - Plan: usar los 2×2Ah para F1-F4 y levantar el consumo REAL; decidir pack
    de maratón con datos del INA3221, no con esta estimación.

### ✅ D4 — Contrato TORSO↔plataforma: **"4 tornillos + XT30 + USB"** (aprobado)
- Mecánica: patrón 4-6× M4 en placa base del TORSO; cada plataforma aporta
  placa adaptadora. Las plataformas se adaptan al TORSO, nunca al revés.
- Potencia: TORSO entrega 12V por **XT30** (15A cont.; motores rover pican 3A).
- Datos: 1× USB Jetson↔ESP32, protocolo serial JSON actual sin cambios.
- Software: el TORSO solo conoce cmd_vel + telemetría. Percepción, brazos,
  LLM y dock viven en el TORSO. Portar = 4 tornillos + 2 cables + firmware
  que hable el mismo JSON.

### 🔌 Pogo pins del dock — referencia confirmada (ya comprados)
[item 1005009020459440](https://es.aliexpress.com/item/1005009020459440.html) —
par magnético macho/hembra, **10A cont. / 24V** (cable 18A), coaxial, roscado
p/ panel, contactos C3604 dorados, hembra estanca, imanes NdFeB. ~COP 36k.
- ✓ Un solo par cubre los ~4.5A de carga+vigilancia (margen 2.2×). Sin paralelos.
- ✓ Imán auto-asienta los últimos mm (AprilTag ±1cm → embudo ±3mm → imán) y
  da desacople seguro + confirmación táctil de acople.
- Reglas de diseño derivadas:
  1. **Dock muerto por defecto**: energizar solo tras handshake de acople
     (precarga limitada → plena). Lado robot: diodo ideal (pines nunca vivos).
  2. **Montaje flotante lado dock** (1-2mm de juego) p/ que el imán alinee.
  3. Verificar fuerza de despegue NdFeB vs tracción skid-steer en piso liso
     al llegar; plan B: desacoplar con giro, no con tirón recto.

---

## Manual del brazo 6DOF (kit Red Sun Global / ThanksBuyer) — 2026-07-09

PDF de 30 páginas digerido (guía fotográfica de ensamblaje). Hallazgos:
- **Cadena cinemática confirmada** (pág. 28): A=yaw base sobre RODAMIENTO
  grande · B=hombro · C=codo (bloque de 2 servos espalda con espalda,
  pág. 15) · D=muñeca pitch · E=muñeca roll · F=garra de ENGRANAJES
  (dedos dentados espejados, pág. 22-26).
- Servos del kit: "25KG 180°, PWM 0.5-2.5ms, DC 4.8-8.4V" — mismo formato
  40×20/25T que MG996R ✓ (los nuestros entran directo).
- Joints con **rodamiento M4X12 en el lado libre** (pág. 14/16/19) — el eje
  no carga solo sobre el spline del servo. Buen diseño, menos juego.
- Electrónica del kit (Arduino NANO + expansión + Bluetooth + buck LM2596):
  NO se usa (nosotros: PCA9685 desde Jetson). Queda de repuesto.
- Servos A-F van a pines 4-9 del Nano en el diseño original (referencia
  para el orden de canales en el PCA9685: A=ch0...F=ch5 por brazo).

## F1 · Gemelo digital — AVANCE 2026-07-09 (sesión autónoma)

Creado `ROS2_Docker_twin/ros2_ws/src/waver_arm_description`:
- `arm_6dof.xacro`: macro parametrizada del brazo (pose vela, REP-103),
  6 revolutas + garra con mimic, límites ±90° (servo 180°), effort 1.0 N·m
  (MG996R), rodamientos del manual reflejados en ejes Y.
- `waver_crab.urdf.xacro`: rover (194×110×55) + sub-chasis (batería+Jetson+
  LiDAR fijo D1b) + **torso_lift_joint prismática** (L16: 0-0.14m, 100N,
  0.02m/s) + placa-torso + 2 brazos a ±45° + OAK como cara.
- Validado sin ROS (pip xacro + urdf-parser-py): ambos modelos ✅.
  CRAB: 29 links, 28 joints (15 móviles), masa modelada 6.26 kg;
  **masa elevada 2.4 kg ≤ 4 kg** (regla D3 ✓); alcance hombro→punta 385mm.
- Geometría del brazo [calibrar] (estimada de fotos, medir al llegar):
  base 95×95×62 · disco+horquilla 57 · hombro→codo 120 · codo→muñeca 90 ·
  muñeca 55 · base garra 45 · dedo 75 (mm).
- Pendiente F1: Gazebo+ros2_control, MoveIt2 (SRDF, TRAC-IK), nodo
  waver_arm con PCA9685 mock.

## F1b · Capa de control del gemelo — AVANCE 2026-07-09 (goal: sigue con f1)

- **`waver_arm`** (paquete nuevo): `servo_map.py` (joint→canal PCA9685:
  izq A-F=0-5, der A-F=6-11, L16=12; ángulo→pulso 500-2500µs/±90°;
  L16 1000-2000µs/0-140mm; rampa de seguridad por joint) + backends
  Mock/Real (Real SIN armar lanza PermissionError — regla de oro codificada)
  + nodo `arm_controller` (rampa 50Hz, /waver_arm/command, /joint_states,
  servicio /waver_arm/arm).
- **19 pruebas unitarias** (mapeo, saturación, canales únicos, mimic sin
  canal, rampa L16=7.0s carrera, regla de oro) — pasan en Mac y en ROS.
- **ros2_control**: control.xacro (posición por joint, mimic de dedos) +
  waver_crab_sim.urdf.xacro + controllers.yaml (JTC por brazo + torso con
  constraint 0.02m/s + grippers).
- **MoveIt2**: SRDF (grupos left/right_arm, *_with_torso, poses candle/
  compact/open/closed, colisiones adyacentes) + kinematics.yaml (KDL,
  TRAC-IK a 1 línea).
- **SMOKE TEST E2E EN DOCKER ✅** (osrf/ros:humble-desktop, scripts/
  smoke_test.sh): colcon build + 19 tests + xacro 3 modelos + robot_state_
  publisher + nodo mock → comando torso 0.14m → **TF midió +140.0mm** en
  ~7s. Trampas resueltas: URDF por --params-file (por -p CLI rompe rcl);
  imagen vieja sin xacro → vendor PyPI por PYTHONPATH.
- Pendiente F1 (sesión con Andrés): RViz/Gazebo con ventana (mini-clase),
  MoveIt2 bringup, decidir KDL vs TRAC-IK, grabar short 🎬.

### F1 · Gemelo VISIBLE en RViz vía navegador ✅ (2026-07-09, verificado con Chrome)
- Contenedor `waver_twin_vnc` (tiryoh/ros2-desktop-vnc:humble, arm64 nativo)
  con el workspace montado → RViz + joint_state_publisher_gui en
  **http://localhost:6080** (noVNC). Sin X11, sin instalar nada en la Mac.
- Verificado moviendo sliders desde el navegador: torso_lift a 0.140 (columna
  extendida en pantalla), hombro 0.671, codo 1.112 → el CRAB responde.
- Gotchas: display debe lanzarse `-u ubuntu` con DISPLAY=:1 (X auth);
  mounts con ruta ABSOLUTA (un $(pwd) relativo creó un dir espurio).
- El contenedor queda corriendo para la sesión de Andrés (grabar short 🎬).

### F4 · ¡LLEGARON LOS BRAZOS! Ensamble + cableado real (2026-07-22)
- Ambos brazos 6DOF ensamblados por Andrés (garra de engranajes incluida).
  Servos instalados: **MG996R** (no los "25KG" del manual) → la regla de
  poses compactas (10 kg·cm ÷ 30 cm ≈ 330 g útiles) queda CONFIRMADA.
- Cadena real por brazo (nomenclatura de Andrés → URDF): rotación de
  hombro = yaw A, elevación = shoulder B, codo 1 = elbow C, codo 2 =
  **wrist_pitch D** (cabeceo de muñeca, mismo sentido que el codo),
  rotación de muñeca = wrist_roll E, pinza = garra F. 6 servos
  independientes por brazo — NO hay bloque doble espejado.
- **Cableado al PCA9685** (garra primero, de externo a interno,
  canales descendiendo): derecho 15→10, izquierdo 9→4, L16 = canal 0
  [por conectar], 1-3 de repuesto. ⚠️ Placa sin serigrafía: el "arranca
  en 15" sale de la imagen del vendedor → **verificar en primer
  encendido** (un servo a la vez, 1500 µs, corriente limitada).
  `servo_map.py` + 20 tests actualizados al cableado real.
- Placa PCA9685 montada entre hombros, con condensador en V+ y borne
  verde libre → alimentar con 6V del UBEC, cable ≥16 AWG, JAMÁS por USB.
  Riel V+ compartido por 12 MG996R: medir pico real con INA3221 (F4)
  y decidir si se refuerza.
- Placa del rover (General Driver): los 4 conectores 2P en uso son
  motor-sin-encoder, pero la placa TRAE 2 puertos PH2.0 6P con entrada
  de encoder (MA1/AC1/AC2/3V3/GND/MA2 y espejo B). Upgrade futuro (F3+):
  2 motores con encoder Hall (1 por lado, verificar encaje mecánico),
  ISR de cuadratura en ESP32 → odometría de ruedas al EKF.
- Pendiente de medición con calibrador (para des-[calibrar] el xacro):
  8 longitudes por brazo + peso por brazo (regla D3 ≤4 kg elevados) +
  patrón de tornillos de la base (para la placa-torso de Onshape).

### F4 · Primer encendido REAL de los brazos + mapeo verificado ✅ (2026-07-22)
- I2C Pi5↔PCA9685 verificado (`i2cdetect` → 0x40) y cadena completa
  validada SIN potencia primero: 50 Hz exactos, eco de registros de los
  13 canales, salidas en FULL_OFF antes de conectar batería.
- Potencia: LiPo 2S del Alpha 1S → interruptor+fusible → UBEC 6V → borne
  V+. NUNCA la LiPo directa (8.4V llena > 7.2V máx del MG996R).
- Descubrimiento canal por canal con bursts de 60 ms (mínimo movimiento,
  servos sin calibrar): los 12 canales de brazos coinciden con el mapa
  der 15→10 / izq 9→4.
- **L16 en canal 0 con convención INVERTIDA (dato medido, no datasheet):
  2.0 ms = retraído, 1.0 ms = extendido.** Descubierto porque el comando
  "retraer" de 8 s lo extendió por completo. Corregido en servo_map.py
  (min_us > max_us intencional) + tests.
- Lecciones de fiabilidad (adelanto de F7):
  · Conector flojo = fallas raras (servos "fantasma" al energizar, bus
    I2C caído a mitad de sesión con Errno 121). Arnés definitivo del
    TORSO: JST con seguro para I2C y retén de silicona en conectores
    de servo.
  · Backend real ahora reintenta transacciones I2C (3 intentos): un
    glitch aislado no tumba el nodo. 22 tests.
  · MG996R clones dan "power-on twitch" al energizar V+: conectar
    siempre con brazos en pose compacta apoyada.

### F4 · PENDIENTE ABIERTO al cierre de sesión (2026-07-22 ~22:15)
- **Bus I2C Pi↔PCA9685 aleteando**: 4 caídas en la sesión (Errno 121),
  la última sin recuperación (20 reintentos). Correlaciona con
  manipulación/vibración → dupont roto por dentro o soldadura fría del
  header del clon. ACCIÓN: 4 cables nuevos y cortos; si persiste,
  repasar soldaduras. El watch de i2cdetect + golpecitos es el test.
- **L16 dejó de responder tras su primer ciclo exitoso** (sí extendió
  y retrajo con el bus sano). Pendiente con bus estable: barrido de
  canales 0-3 y prueba de intercambio (servo suelto en la posición
  del ch0). Sesión cerró con LiPo apagada por seguridad.
- Verificado y NO afectado: mapeo 12 servos de brazos (discovery de
  Andrés lo re-confirmó esta noche: muñeca responde), inversión del
  L16 medida y codificada, riel 6V vivo.

### F4 · RESUELTO: el L16 estaba ACUÑADO contra su tope ✅ (2026-07-22 ~23:00)
- Causa raíz de la "sordera" del L16: los comandos de retraer sostenidos
  8 s con el vástago YA retraído acuñaron el husillo contra el tope
  interno. Síntomas: retraer = silencio, extender = amagos sin salir.
  Ni batería nueva ni cambio de canal lo curaban.
- Liberación: comando de extender + tracción manual suave del vástago
  ("la mano rompe el acuñamiento"). Después respondió a posiciones
  absolutas de nuevo (verificado: casi-afuera → casi-adentro → media
  carrera, terminando exacto en 70 mm).
- REGLAS NUEVAS codificadas en servo_map.py (22 tests verdes):
  · L16 vive en el CANAL 3 (el 0 queda de repuesto, bajo sospecha).
  · LÍMITES SUAVES: saturación a 5-135 mm (1964-1036 us). Ningún
    comando puede volver a sostenerlo contra un tope físico.
- Los cables I2C nuevos dejaron el bus estable el resto de la sesión.
- Cierre real de la noche: 13 canales mapeados y verificados con
  potencia, brazos + columna vertebral respondiendo, y 4 lecciones de
  hardware que el gemelo digital jamás nos habría enseñado.

## 2026-07-30 — Jetson Orin Nano Super lista; los brazos obedecen a la Jetson

- Jetson: JetPack 7.2 en NVMe (ISO installer por USB), firmware 36.4.3.
  MAXN_SUPER persistente tras apuntar extlinux al DTB p3767-0005-super
  (el script nvpower.sh de NVIDIA re-enlazaba el perfil normal en cada
  boot mientras la máquina no se identificara "-super").
- Escritorio remoto final: xrdp headless. Dos descartes con causa: NoMachine
  v10 (suscripción) y Remote Login de GNOME (falla la redirección 3389→3390
  con clientes macOS). Bug de fábrica corregido: ~/.xsessionrc de JetPack es
  bash pero Xsession lo sourcea con dash → sesión moría en 0 s.
- PCA9685 al header de la Jetson (pines 1/3/5/6, bus i2c-7). Workbench web
  de calibración (soma-arms/scripts/servo_workbench.py): rampa server-side
  50 Hz, un servo a la vez, L16 en ch3 con banda 1000-2000 us, rampa
  140 us/s y auto-release 2 s. Los 13 actuadores verificados desde la
  Jetson. Datos de calibración reiniciados (los primeros no eran fiables).
- OAK-D Lite sobre la Jetson: depthai 2.32 + OpenCV 5 + regla udev; demos
  de detección espacial (VPU), ArUco (cubo Alpha 1S, ids 7-10, ~7 cm) y
  profundidad, las 3 funcionando.
- Abiertos: recentrado mecánico de horns a 1500 us, captura completa
  zero/min/max, muñeca izquierda que retiene con potencia sin señal
  (diferencial pendiente), confirmar USB3 (SUPER) de la cámara, medir el
  marcador impreso con regla.

## 2026-08-05 — Sesión de calibrador: la geometría deja de ser estimada

- Llegó el calibrador. Las 14 medidas de la cadena del brazo (derecho) +
  anclajes del banco con flexómetro. Todo en soma-arms:
  `soma_description/config/dimensions.yaml` con provenance por entrada.
  Los estimados de fotos fallaban hasta 40 mm (brazo superior: 79.3 real
  vs 120 estimado).
- DESCUBRIMIENTO de configuración: los dos brazos CUELGAN de una caja
  central (las dos cajas base atornilladas espalda con espalda, 109.8 mm
  entre asientos de disco) sobre columna de soporte de monitor. Ejes de
  los discos horizontales, colineales, hacia afuera, a 343 mm de la placa.
- Los 4 primeros ejes de cada brazo son PARALELOS (disco ∥ hombro ∥ codo ∥
  pitch): cada brazo es cadena plana 4R en su plano vertical; el roll de
  muñeca saca la pinza del plano. Eslabón "clavícula" de 33 mm entre disco
  y hombro. El manual decía yaw-primero vertical; el robot real manda.
- Verificación que cerró el círculo: FK del modelo pone la punta de los
  dedos a 5.7 mm de la placa en pose cero, igual que las fotos del rig.
- El torso L16 queda formalmente FUERA del banco actual (dormante hasta el
  torso impreso); smoke test de CI ahora prueba codo izquierdo −90° = la
  herramienta sube 225 mm exactos.
- Pendientes: pesar un brazo, verificar SIGNOS de ejes con potencia
  (v0.2), re-spline del yaw izquierdo.


## 2026-08-11 — Sesión v0.2 EN CURSO (estado guardado pre-compact)

- Multímetro re-certificado (pila 9V nueva): LiPo 8.2V, pack DeWalt 20.2V
  en reposo. El "15.6V" de anoche era la pila muerta del multímetro.
- Fusible 7.5-10A no hubo en el pueblo → repuestos de motos/carros. HOY no
  bloquea: la sesión de metal usa la cadena LiPo 2S conocida (doctrina de
  una variable a la vez); la cadena DeWalt debuta cuando tenga su fusible.
- SOLDADURA DE HOY (decidida, AMPLIADA): todo el cobre de la arquitectura
  dos placas + INA3221, SIN conmutar servos:
  · PCA9685 #2: puente A0 → 0x41. Daisy I2C (4 hilos <10cm) desde placa #1.
  · INA3221 SE INSTALA HOY (decisión 11-ago, antes era "futuro"):
    lógica al final del daisy (PCA#2 → INA, 4 hilos), jumper dir → 0x44;
    shunt CH1 EN SERIE en el positivo entre fusible y UBEC #1 (se corta
    ese tramo; nacen cables W15/W16). CH2/CH3 SIN conectar: el shunt de
    fábrica (0.1Ω 2W) se quemaría en el riel de 6V a 5A.
  · UBEC #2: jumper a 6V + pigtail XT60 + verificar 6.0V sin carga.
  · V+ separados por placa (D3: aislamiento por brazo). GND común.
  · Los 12 servos SIGUEN en placa #1 (0x40). La conmutación del brazo
    izquierdo a 0x41 va en sesión posterior, con el software multi-placa
    ya en main. Pendiente material: ¿segundo condensador 1000µF?
- PLANO DE CABLEADO formal (cable por cable, wirelist W01-W23 + WF, config
  C1-C6, notas N1-N8, checklist V1-V9): cad/plano_cableado_soma_v02.html
  (rev A, también publicado como artifact para verlo junto al banco).
- Verificación al subir la Jetson: i2cdetect -y -r 7 → 0x40, 0x41 Y 0x44;
  firma del INA: i2cget -y 7 0x44 0xfe w → 0x4954 ('TI' bytes volteados).
- OJO software: BATTERY_FLOOR_V=15.2 es del pack DeWalt 5S. Con la LiPo 2S
  del banco (~8V) ese guard rechazaría todo: la integración del INA al
  nodo llevará piso por PERFIL DE FUENTE. Hoy el INA se instala y se lee;
  no gobierna el armado todavía.
- Software pendiente (Claude): (a) soporte multi-placa retrocompatible
  (campo address default 0x40 en servo_map + router de backends + tests);
  (b) integración INA3221 al nodo: rechazar armado bajo 15.2V.
- Runbook restante: soldar → continuidad → "jetson arriba" (Claude
  prepara remoto: pull+build+ensayo mock) → LiPo, brazos quietos, V+ al
  final → ritual de armado de Andrés → soma_sign_check joint por joint
  (anotar flips → Claude corrige ejes en xacro) → soma_primitives demo
  FILMADA → tag v0.2 si todo canta.


## 2026-08-11 (noche) — BUS DE DOS PLACAS + INA3221: VIVO Y VERIFICADO

- i2cdetect -y -r 7: **0x40 (PCA#1) · 0x41 (INA3221) · 0x43 (PCA#2)**
  + 0x70 (all-call, normal). Identidades por firma, no por fe: 0x41
  responde manufacturer 0x5449 'TI' y die ID 0x3220; 0x43 responde
  prescale virgen (0x1E). Tres chips, tres nombres, cero colisiones.
- El camino: los tres llegaron apiñados en 0x40 (ningún puente de
  dirección estaba hecho). Forense de la colisión: reg 0xFE de 0x41
  leyó 0x0814 = AND bit a bit de 0x1E1E (PCA) con 0x5449 (INA), porque
  en I2C los ceros dominan. Colisión demostrada sin desoldar nada.
- LECCIÓN de direcciones: el INA3221 solo ofrece 0x40-0x43 vía A0
  (SBOS576); el "0x44/45" del inventario era del INA219 del rover.
  Mapa final por adyacencia de pads: INA 0x41 (gota A0↔VS), PCA#2
  0x43 (A0+A1). Tres puentes SMD de Andrés, tres al primer intento.
- Lección de topología: I2C es bus. La "estrella" soldada desde los
  pines de entrada del PCA#1 es eléctricamente idéntica al daisy por
  el header de salida. Válida tal cual quedó.
- El clon del PCA#2 (V1246) trae condensador electrolítico a bordo:
  compra del segundo 1000µF aplazada a la conmutación.
- Bus V del INA: CH1/CH2/CH3 = 0.00V (correcto: potencia sin pasar
  por los shunts todavía).
- Software corregido con los hechos (soma-arms 8ef31e5): DEFAULT
  0x44→0x41 en ina3221.py, test de dirección reescrito explicando el
  cambio de hecho físico, CLAUDE.md y wiring.md al mapa real. Suite
  130 passed + 6 skipped local.
- Los 12 servos siguen en 0x40: la demo de hoy NO necesita el software
  multi-placa. Pendiente en banco: ¿shunt CH1 en serie ya insertado?
  (confirmar), UBEC#2 a 6.00V sin carga, luego cadena LiPo → ritual de
  armado (Andrés) → sign_check → demo filmada → tag v0.2.

### Cierre 11-ago (noche) y plan 12-ago — MONTAJE FÍSICO TOTAL

- Sesión cerrada por fatiga (regla de siempre: soldador cansado =
  defecto de seguridad). Shunt CH1 aún NO insertado; UBEC#2 aún sin
  verificar 6.00V. La demo v0.2 queda para después del montaje.
- DECISIÓN de Andrés: 12-ago = completar TODO el cobre de una vez
  (hoja B del plano rev B), en este orden:
  1. Comprar fusible 7.5-10A: es de CUCHILLA automotriz (ATO/ATC),
     pedirlo así en repuestos de motos/carros.
  2. Shunt CH1 en serie fusible→UBEC#1 (cables W15/W16 del plano).
  3. Cadena DeWalt servos: adaptador B0B9NPZM3M + fusible nuevo + XT60
     (WF01/WF02). Con fusible en mano la DeWalt puede debutar como
     fuente de servos (el UBEC regula igual); todo encendido con
     brazos compactos y apoyados, como siempre.
  4. Cadena Jetson wireless: dock B0FP1B1F86 → barrel 5.5×2.5 centro+
     → Jetson (WF03). OJO: sin power_guard de software todavía, pack
     agotado = corte duro del UVLO a 15.2V. Aceptable para pruebas
     cortas con pack lleno (20.2V = horas de margen); NO dejar la
     Jetson desatendida a batería.
  5. PREGUNTA DE DISEÑO para el banco: ¿el dock expone el voltaje del
     PACK (20V) en algún punto medible con multímetro? Si sí → tap
     solo-voltaje a INA CH3 (VIN3+ y VIN3− puenteados juntos al
     positivo del pack: voltímetro sin shunt en serie, sin límite
     térmico) y el power_guard lee CH3. Si no → pinza en terminales
     pack↔dock o guard por tiempo. Se decide con el hardware en mano.
- Software pendiente (Claude, mientras Andrés suelda): (a) multi-placa
  retrocompatible (campo address en servo_map, default 0x40, PCA#2 =
  0x43); (b) power_guard de la Jetson (diseño depende del punto 5);
  (c) integración INA al nodo con piso por perfil de fuente.

## 2026-08-12 — Software del día + FUENTE ATX entra al banco

- SOFTWARE CERRADO (CI verde en ambos commits):
  · Multi-placa (soma-arms b51169e): ServoSpec.address default 0x40,
    flota de backends ruteada por dirección, armado todo-o-nada, regla
    de oro por placa; test pin "todo el mapa sigue en 0x40 hoy". La
    conmutación del brazo izquierdo = 6 renglones + 6 conectores.
  · Veto de batería (soma-arms 4f43627): parámetro battery_source
    ('none' default / 'dewalt_5s' 15.2V / 'lipo_2s' 6.4V), publica
    soma/power (BatteryState 1Hz, INA ch1), rechaza armar bajo el piso.
    VETO, nunca compuerta; fail-safe si el INA no responde; SIN desarme
    automático (cortar PWM en movimiento tira los brazos: la política
    suave es del power_guard). Suite: 151 verdes + 1 skip rclpy.
- FUENTE ATX MaxiTech 300U (decisión: fuente de BANCO; DeWalt = móvil):
  · Etiqueta "500W" = marketing: rieles suman ~241W. Manda +12V@10A.
  · Presupuesto 12V: Jetson ~2.5A + UBEC#1 ~3A + UBEC#2 ~3A ≈ 8.5A
    pico peor caso (dentro, vigilado por soma/power). Hoy sin servos
    en UBEC#2: ~5.5A pico, cómodo.
  · Encendido standalone: puente VERDE(PS_ON)↔NEGRO en el 24 pines.
    ATX12V v1.3: si el 12V baila sin carga, ventilador en 5V.
  · Cosecha: P4 (2×amarillo+2×negro) → fusible 7.5-10A → XT60 →
    UBECs; molex → barrel 5.5×2.5 centro(+) → Jetson.
  · Primer encendido A SOLAS con multímetro: 11.8-12.3V estables antes
    de conectar nada. Plano rev C: hoja C nueva del modo banco.
- CONMUTACIÓN DEL BRAZO IZQUIERDO: HOY (corrección de Andrés: "no
  tiene sentido omitir algo que ya está instalado" — las dos placas
  están soldadas, testeadas y con firma en el bus, y el software
  multi-placa ya está en main). Plan ejecutado:
  · servo_map: los 6 renglones del brazo izq ganan address=0x43,
    MISMOS números de canal (9-4): el movimiento físico es 6 conectores
    de la placa #1 a la #2, posición por posición. Pulsos y límites
    intactos (pertenecen a los servos, no a la placa).
  · Tests editados DECLARANDO el cambio de hecho (tabla exacta gana
    columna de placa; el pin "todo en 0x40" muere como su propio
    comentario exigía). Suite 151+1, CI VERDE (soma-arms d679c3f).
  · La placa #2 no tiene serigrafía: primer armado re-confirma canal
    por canal (sign_check del brazo izq), ritual del 22-jul.
- FUENTE UNIVERSAL POR XT60 (decisión de diseño): la ATX termina en un
  XT60 macho y se enchufa DONDE IBA LA LIPO, alimentando un Y de XT60
  (fabricar hoy: 1 macho + 2 hembras) hacia ambos rieles. El árbol
  aguas abajo queda intacto (switch → fusible → shunt CH1 → UBECs):
  el INA ve todo en cualquier modo, y banco↔móvil = cambiar UN
  conector. Plano rev D: dos rieles activos, C8 (Y de XT60), C9
  (reconexión brazo izq), V11 (INA lee ~12V con ATX), V12 (sign_check
  del izq post-conmutación).


## 2026-09-01 — Reanudación tras 3 semanas (estado real del banco)

- Reporte de Andrés: fusible 10A COMPRADO E INSTALADO ✓; ATX en curso
  de preparación; PENDIENTES: reconexión brazo izq a placa #2 (C9),
  Y de XT60 (C8), shunt CH1 (W15/W16), molex→barrel Jetson (WB03).
- ⚠ DESAJUSTE CONSCIENTE mapa/banco: main (soma-arms d679c3f) ya
  mapea el brazo izquierdo en 0x43, pero sus 6 servos siguen
  físicamente en la placa #1 (0x40). Desarmado es inofensivo (el
  brazo izq quedaría sin señal, flácido, jamás errático). PROHIBIDO
  ARMAR hasta completar C9: la reconexión va ANTES del ritual en la
  secuencia de esta sesión. El mapa describe el banco OBJETIVO de hoy.
- Secuencia de reanudación: (1) ATX terminada + V10 (11.8-12.3V a
  solas); (2) Y de XT60 + molex→barrel; (3) C9 reconexión 6 servos
  posición por posición; (4) shunt CH1 si hay gasolina (recomendado,
  no bloqueante: la demo sale sin él); (5) Jetson arriba → escaneo →
  ritual de armado de Andrés → sign_check AMBOS brazos → demo
  bimanual FILMADA → tag v0.2.
- Pregunta abierta: ¿el fusible 10A quedó en la rama ATX (antes del
  XT60 universal, posición WB01: perfecto) o en la cadena del
  adaptador DeWalt (WF02: entonces la rama ATX necesita el suyo o
  moverlo)? El 12V de la ATX no viaja sin fusible.
- Correo de OmniLink (31-ago) analizado: outreach real no-phishing de
  un simulador open-source; valor técnico ~0 para SOMA (tenemos
  MuJoCo+oráculo propios), decisión de marca pendiente de Andrés.
- V10 CUMPLIDO: ATX a solas con puente verde-negro = 11.6V ESTABLES.
  Bajo el deseable (11.8-12.3) pero dentro del ±5% del estándar ATX
  (11.4-12.6); Jetson (9-20V) y UBECs lo aceptan de sobra. Vigilar
  bajo carga: si cae de 11.4V sostenido → ventilador de carga en 5V.
- Limpieza de circuitos: WD-40 clásico VETADO en electrónica (residuo
  aceitoso que atrapa polvo y arruina resoldaduras). Estándar: alcohol
  isopropílico ≥90% + brocha suave + aire, todo desenergizado y seco
  antes de dar candela. (Andrés, técnico en electrónica, limpió la ATX
  por dentro con criterio propio: ventilador y polvo, primario intacto.)
- MONTAJE COMPLETADO 01-sep: molex→barrel (centro+ verificado contra
  spec NVIDIA: 5.5×2.5, centro positivo, 9-19V), P4 completo → fusible
  10A → XT60 hembra → Y → ambos UBEC (distribución en estrella,
  retornos separados). Jetson corrió DE LA ATX por primera vez. Jetson
  reubicada por DHCP: ahora jetson.local (192.168.1.11; la .13 se la
  quedó un celular). Repo en Jetson actualizado a main (aeff395);
  usuario jetson SIN grupo docker (pendiente usermod de Andrés).
- ⚡ INCIDENTE 01-sep: al conectar la potencia de servos EN CALIENTE,
  el inrush (caps de entrada de ambos UBEC + 12 servos) disparó la
  protección/hundió el riel 12V de la ATX y APAGÓ la Jetson (corte
  duro). Física: la fuente es el nodo raíz común; la estrella no
  protege del colapso del raíz. Decisión pendiente de Andrés:
  (A) Jetson a su adaptador de pared 19V y ATX dedicada a servos
  (dominios separados de verdad, voto de Claudia), o
  (B) todo-ATX con secuencia estricta: todo conectado ANTES de
  encender la fuente (el soft-start de la ATX limita el inrush).

### Pausa 01-sep (noche): fijación mecánica antes de mover
- Driver VIVO en la Jetson: contenedor soma_driver con main completo,
  "MOCK backend, DISARMED" en logs. Docker OK (usermod hecho).
- 6.00V confirmados en AMBOS bornes. Jetson en su adaptador propio
  (decisión A). Ritual de 3 pasos entregado a Andrés (A: relanzar con
  allow_real; B: /soma/arm — suyo; C: soma_sign_check interactivo).
- PENDIENTE ANTES DE MOVER: C9 (¿6 conectores del brazo izq en placa
  #2? sin confirmar) + FIJACIÓN MECÁNICA en curso: Andrés fija placas/
  UBECs/cables (estaban al aire: riesgo real de corto o tirón al
  mover). Decisión correcta, regla 5 en acción.

## 2026-10-01 — Red de la Jetson curada + OAK-D Lite verificada en USB-C
- Lentitud de SSH/xrdp: NO era alimentación (VDD_IN 4.7 W, 0 alarmas
  del INA3221 interno, 49 °C, CPU 96-100% idle, 0 iowait). Causa: WiFi
  power save ON (ping 37 ms prom / 99 ms máx, pérdidas intermitentes).
  Fix: sudoers acotado /etc/sudoers.d/soma-claude (NOPASSWD solo
  nmcli, iw, nvpmodel, jetson_clocks, shutdown) + perfil JEJEN_5G
  powersave=disable + iw power_save off → 1.5 ms prom, 3.4 máx, 0%
  pérdida. Login SSH 0.45 s. xrdp sigue pesado por diseño (Xorg :10
  por software, max_bpp=32, crypt high): bajar a 16 bits en cliente.
- Jetson ahora en 192.168.1.2 por WiFi (wlP1p1s0); Ethernet sin cable.
  Pendiente: reserva DHCP de la MAC f0:68:e3:32:b6:8f en el router.
- MAXN_SUPER activo; jetson_clocks NO aplicado a propósito (sin carga
  que lo justifique hasta v0.3/RL).
- OAK-D Lite (MxId 19443010A1A8DE5900) por el USB-C de la Jetson
  (modo host, USB 3.2 Gen2) con cable 40 Gbps: USB SUPER (5 Gbps),
  IMX214 + 2× OV7251, RGB 640×400 a 29.7 fps, chip 33 °C. depthai
  2.32 en Python del sistema + regla udev 80-movidius ya instaladas.
