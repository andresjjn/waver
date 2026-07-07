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

**Análisis CRAB con ARA**: 2 brazos = 6× MG996R (inventario ✓). Cadena:
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
