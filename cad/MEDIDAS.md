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

## Brazos cangrejo (cadena por lado: yaw S3003 → hombro MG996R → codo MG996R → muñeca S3003 → pinza MG996R)

| Variable | Valor | Nota |
|---|---|---|
| Anclaje hombro | x=12, y=±(plat_w/2 − 12) | parten del centro, a lado y lado |
| `l_humero` | 78 | hombro → codo |
| `l_ante` | 66 | codo → muñeca |
| `l_garra` | 72 | muñeca → punta de pinza |
| Pose demo | yaw 52°, hombro 26°, codo −58°, muñeca −14°, pinza 24° | para validar rangos en Onshape con *joint limits* |

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
