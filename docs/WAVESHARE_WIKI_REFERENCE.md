# Referencia técnica offline — Waveshare WAVE ROVER + General Driver for Robots

> Documento consolidado a partir de la wiki oficial de Waveshare (páginas
> `WAVE_ROVER` oldid=103639, `General_Driver_for_Robots` oldid=103968 y los
> tutoriales I–VIII de la placa). Extraído el 2026-07-03. Es la referencia
> permanente del proyecto **Waver** (ROS 2, Raspberry Pi 5 + ESP32 esclavo con
> firmware I2C custom `waver_slate_v2`).

---

## 1. WAVE ROVER — Resumen del producto y especificaciones

Chasis móvil 4WD de cuerpo totalmente metálico, con capacidad off-road y
absorción de impactos. Todo el código es open-source. El host (Raspberry Pi,
Jetson Nano/Orin Nano, etc.) se comunica con el ESP32 esclavo por puerto serie
(en el firmware stock; nuestro stack usa I2C, ver §6).

| Parámetro | Valor |
|---|---|
| Dimensiones del chasis | **194 × 168 × 100 mm** |
| Tracción | 4WD, 4 × motor N20 con reductora, ruedas de goma blanda |
| Velocidad máxima | **1.25 m/s** |
| Motores | GF12-N20, 12 V, 200 rpm, **sin encoders** |
| Alimentación | UPS 3S con 3 × 18650 en serie (no incluidas), ~7800 mAh |
| Cargador | **12.6 V / 2 A** (puerto de carga dedicado; permite usar mientras carga) |
| Monitoreo de batería | INA219 en el módulo UPS (tensión y corriente de carga en tiempo real) |
| Salidas auxiliares del UPS | 5 V y 3.3 V para periféricos |
| Protección de batería | Sobrecarga, sobredescarga, sobrecorriente y cortocircuito |
| Pantalla | OLED 0.91" (SSD1306, 128×32) |
| Cerebro esclavo | ESP32 (placa General Driver for Robots) con WiFi, Bluetooth y ESP-NOW |
| Expansión | Plataforma superior para host (RPi 4B/5, Jetson), LiDAR LD19/STL-27L, pan-tilt |

### Especificaciones del motor (GF12-N20 Motor 12V200rpm Gearbox)

| Parámetro | Valor |
|---|---|
| Tensión nominal | 12 V |
| Corriente nominal | 0.055 A |
| Corriente a rotor bloqueado | 0.45 A |
| Par nominal | 0.09 kg·cm |
| Par a rotor bloqueado | 0.7 kg·cm |
| Potencia de salida nominal | 1.5 W |
| Velocidad sin carga | 66 ± 10 % RPM *(así aparece en la wiki; el modelo comercial es "200 rpm" — dato a verificar empíricamente para odometría)* |
| Tamaño del motor | 34 × 12 mm |
| Eje de salida | 4 × 10 mm |

### Comportamiento del firmware stock al arrancar

- OLED línea 1: WiFi en modo **AP**, hotspot `UGV`, contraseña `12345678`, IP `192.168.4.1`.
- OLED línea 2: estado STA (IP asignada por el router si está configurado).
- OLED línea 3: dirección **MAC** (usada para ESP-NOW).
- OLED línea 4: **tensión de alimentación**.
- Firmware "nuevo" muestra `Version: 0.9` al arrancar.
- **Heartbeat**: si no llega un comando de movimiento nuevo en **3 s**, el robot se detiene solo. La web app también tiene detección de heartbeat.
- LED encendido al conectar baterías por primera vez = **polaridad invertida** (¡no cargar así, riesgo de explosión!).
- Actualización de firmware: `flash_download_tool_3.9.5.exe`, chip ESP32, modo Factory, baud hasta **921600**, por el USB Type-C central de la placa (requiere desarmar el rover).
- Serie stock: **115200 baudios**, con `setRTS(False)` y `setDTR(False)` en el host (evita resetear el ESP32 al abrir el puerto).

---

## 2. Placa "General Driver for Robots" — Detalle completo

Placa driver multifunción basada en **ESP32-WROOM-32**, programable con Arduino
IDE. Soporta WiFi, Bluetooth y ESP-NOW.

### Parámetros generales

| Parámetro | Valor |
|---|---|
| Controlador principal | ESP32-WROOM-32 |
| Alimentación | **DC 7–13 V** (batería 2S o 3S directa) |
| Puerto de alimentación | XH2.54 (alimenta directamente motores y servos de bus) |
| Conector de antena | IPEX1 |
| Interfaz de descarga | USB Type-C (con circuito de auto-descarga: no hace falta pulsar EN/BOOT) |
| Comunicación inalámbrica | WiFi, Bluetooth, ESP-NOW |
| Dimensiones | **65 × 65 mm** |
| Separación de taladros | 49 × 58 mm, Ø 3 mm |

### Recursos a bordo (numeración de la wiki)

| # | Recurso | Descripción / dato clave |
|---|---|---|
| 1 | ESP32-WROOM-32 | MCU principal, desarrollable con Arduino IDE |
| 2 | Conector IPEX1 | Antena WiFi externa |
| 3 | Interfaz LIDAR | Integra la función de placa adaptadora del radar |
| 4 | Interfaz de expansión IIC | Para OLED u otros sensores I2C (bus S_SDA/S_SCL) |
| 5 | Botón Reset | Reinicia el ESP32 |
| 6 | Botón Download | ESP32 entra en modo descarga si se enciende con él pulsado |
| 7 | Regulador DC-DC **5 V** | Alimenta el host (Raspberry Pi / Jetson) por el header 40PIN |
| 8 | Type-C (LIDAR) | Salida de datos del LiDAR vía CP2102 |
| 9 | Type-C (USB) | UART del ESP32 / subida de firmware vía CP2102 |
| 10 | Puerto XH2.54 | Entrada DC 7–13 V; alimenta directo servos de bus y motores |
| 11 | **INA219** | Chip de monitoreo de tensión/corriente — **dirección I2C 0x42** |
| 12 | Interruptores Power ON/OFF | Controlan la alimentación externa (uno limita/conmuta la salida a servos de bus, máx. **5 A** continuos) |
| 13 | Interfaz servo bus ST3215 | Hasta 253 servos ST3215 con retroalimentación |
| 14 | Motor PH2.0 6P (grupo B) | Motor **con encoder**, grupo B |
| 15 | Motor PH2.0 6P (grupo A) | Motor **con encoder**, grupo A |
| 16 | Motor PH2.0 2P (grupo A) | Motor **sin encoder**, grupo A |
| 17 | Motor PH2.0 2P (grupo B) | Motor **sin encoder**, grupo B |
| 18 | **AK09918C** | Brújula electrónica de 3 ejes (magnetómetro) — en nuestro bus responde en **0x0C** |
| 19 | **QMI8658** | Sensor de movimiento de 6 ejes (acel + gyro) — en nuestro bus responde en **0x6B** |
| 20 | **TB6612FNG** | Driver de motores DC (2 canales H-bridge) |
| 21 | Circuito de control de servos de bus | Expansión de múltiples ST3215 con feedback |
| 22 | Ranura SD/TF | Logs o configuración WiFi (FAT32) |
| 23–24 | 2 × header 40PIN | Conexión a Raspberry Pi / Horizon Sunrise X3 Pi; expone pines del host montado |
| 25 | CP2102 (#1) | UART→USB para datos del radar/LiDAR |
| 26 | CP2102 (#2) | UART→USB para la UART del ESP32 |
| 27 | Circuito de auto-descarga | Sube firmware sin pulsar EN/BOOT |

### Mapa de pines del ESP32 (consolidado de los tutoriales)

| Función | Pin ESP32 | Notas |
|---|---|---|
| **Motores (TB6612FNG)** | | |
| PWMA | GPIO 25 | canal ledc 0, **100 kHz**, resolución 8 bits (0–255) |
| AIN1 / AIN2 | GPIO 21 / GPIO 17 | dirección motor A |
| PWMB | GPIO 26 | canal ledc 1 |
| BIN1 / BIN2 | GPIO 22 / GPIO 23 | dirección motor B |
| **Encoders (solo variante con encoder)** | | |
| AENCA (A_C2, B) | GPIO 35 | entrada, INPUT_PULLUP |
| AENCB (A_C1, A) | GPIO 34 | interrupción RISING |
| BENCA (B_C1, A) | GPIO 27 | entrada, INPUT_PULLUP |
| BENCB (B_C2, B) | GPIO 16 | interrupción RISING |
| **Bus I2C periférico** | | |
| S_SDA | **GPIO 32** | INA219 (0x42), OLED SSD1306 (0x3C), QMI8658 (0x6B), AK09918 (0x0C) |
| S_SCL | **GPIO 33** | mismo bus — es el que exponemos a la RPi como `/dev/i2c-1` |
| **Servos de bus ST3215 (Serial1)** | | |
| S_RXD | GPIO 18 | UART1 a **1 000 000 baudios**, 8N1 |
| S_TXD | GPIO 19 | librería SCServo (clase `SMS_STS`) |
| **Servo PWM / IO libres** | | |
| PSERVO / IO4 | GPIO 4 | canal ledc 7 en el demo; controlable por `T:132` |
| IO5 | GPIO 5 | segundo canal PWM libre (`T:132`) |
| **SD card (HSPI)** | | |
| SCK | GPIO 14 | `SPIClass(HSPI)` a 80 MHz |
| MISO | GPIO 12 | |
| MOSI | GPIO 13 | |
| CS | GPIO 15 | |
| **UART0 (USB / host)** | GPIO 1 / 3 (por defecto) | 115200 baudios en firmware stock |

### Variantes de motor con / sin encoder

- **Con encoder** (conector PH2.0 6P, grupos A y B): 2 motores máx., lazo cerrado. Cada encoder da 2 señales Hall; el demo cuenta flancos RISING de un canal y lee el otro para el sentido. Ejemplo de la wiki: motor DCGM3865, reducción 1:42, **11 ppr** por Hall → `shaft_ppr = 42 × 11 = 462` flancos por vuelta del eje de salida.
- **Sin encoder** (conector PH2.0 2P, grupos A y B): hasta 4 motores (2 por grupo, en paralelo), solo lazo abierto. **El WAVE ROVER usa esta variante** (4 × GF12-N20 sin encoder, un canal TB6612 por lado).
- El PWM servo recomendado es el WP90; la placa **no** soporta MG996R/MG90S ni servos PWM de alta potencia.
- Servos de bus: límite de corriente por interruptor, **máx. 5 A continuos**; con ST3215 hasta ~5 servos simultáneos sin bloqueo.

---

## 3. Set completo de comandos JSON del firmware stock

Vías de envío: web app (`192.168.4.1` → FEEDBACK INFORMATION), HTTP
(`http://IP/js?json=<cmd>`), ESP-NOW, o UART/USB (115200). Heartbeat: los
comandos de movimiento caducan a los 3 s.

### Movimiento del chasis

| Comando | Ejemplo | Explicación |
|---|---|---|
| **T:1** — CMD_SPEED_CTRL | `{"T":1,"L":0.5,"R":0.5}` | Velocidad de rueda izquierda/derecha. Rango **−0.5 … +0.5** (positivo = adelante). En WAVE ROVER (sin encoders) 0.5 ≡ 100 % del PWM de ese lado, 0.25 ≡ 50 %. **Comando recomendado.** |
| **T:11** — CMD_PWM_INPUT | `{"T":11,"L":164,"R":164}` | PWM crudo por motor, rango **−255 … +255**. Solo para depuración; con \|PWM\| bajo el motor puede no girar (mala característica a baja velocidad de los motorreductores DC). |
| **T:13** — CMD_ROS_CTRL | `{"T":13,"X":0.1,"Z":0.3}` | X = velocidad lineal (m/s), Z = velocidad angular (rad/s). **Solo para UGV01 con encoders** (no aplica a WAVE ROVER). |
| **T:2** — PID de motores | `{"T":2,"P":200,"I":2500,"D":0,"L":255}` | Coeficientes PID; `L` = Windup Limit (reservado, no usado por el PID por defecto). **Solo UGV01 con encoders.** |

### Pantalla OLED

| Comando | Ejemplo | Explicación |
|---|---|---|
| **T:3** — Control OLED | `{"T":3,"lineNum":0,"Text":"putYourTextHere"}` | Escribe una de las 4 líneas (`lineNum` 0–3) sin afectar las demás. Desactiva la pantalla de info del robot. |
| **T:-3** — Restaurar OLED | `{"T":-3}` | Restaura la pantalla al estado inicial (info del robot). |

### Información del producto

| Comando | Ejemplo | Explicación |
|---|---|---|
| **T:126** — IMU | `{"T":126}` | Devuelve datos IMU: heading, campo magnético, aceleración, actitud, temperatura, etc. |
| **T:130** — CMD_BASE_FEEDBACK | `{"T":130}` | Feedback puntual de información del chasis (modo pregunta-respuesta). |
| **T:131** — Feedback continuo | `{"T":131,"cmd":1}` (on) / `{"T":131,"cmd":0}` (off, por defecto) | Activa el streaming continuo por serie, pensado para ROS (evita polling con T:130). |
| **T:143** — Echo serie | `{"T":143,"cmd":1}` (on) / `{"T":143,"cmd":0}` (off, por defecto) | Con echo activado, todo comando enviado aparece en el feedback serie. |

### GPIO libres

| Comando | Ejemplo | Explicación |
|---|---|---|
| **T:132** — IO4/IO5 | `{"T":132,"IO4":255,"IO5":255}` | Fija el PWM de las salidas IO4 (GPIO4) e IO5 (GPIO5), 0–255. |

### Módulos externos

| Comando | Ejemplo | Explicación |
|---|---|---|
| **T:4** — Tipo de módulo | `{"T":4,"cmd":0}` | 0 = ninguno, 1 = brazo RoArm-M2, 3 = pan-tilt (gimbal). |
| **T:133** — Control pan-tilt | `{"T":133,"X":45,"Y":45,"SPD":0,"ACC":0}` | X = ángulo horizontal (+izquierda/−derecha), Y = vertical (+arriba/−abajo), con velocidad y aceleración. |

### ESP-NOW (T:301–T:306)

| Comando | Ejemplo | Explicación |
|---|---|---|
| **T:301** — Modo ESP-NOW | `{"T":301,"mode":0}` (off) / `{"T":301,"mode":3}` (on, por defecto) | Habilita/deshabilita la recepción de comandos por ESP-NOW. |
| **T:303** — Añadir peer | `{"T":303,"mac":"CC:DB:A7:5C:1C:40"}` | Añade una MAC al peer list. Broadcast: `"FF:FF:FF:FF:FF:FF"`. Recomendado ≤ 20 peers (sin mezclar broadcast en multicast). |
| **T:304** — Borrar peer | `{"T":304,"mac":"CC:DB:A7:5C:1C:40"}` | Elimina una MAC del peer list. |
| **T:305** — Envío multicast | `{"T":305,"dev":0,"b":0,"s":0,"e":1.57,"h":1.57,"cmd":1,"megs":"{\"T\":114,\"led\":255}"}` | Envía el JSON de `megs` a todos los peers registrados. Los demás campos son para otras funciones: no tocar. |
| **T:306** — Envío unicast/broadcast | `{"T":306,"mac":"CC:DB:A7:5C:1C:40","dev":0,"b":0,"s":0,"e":0,"h":0,"cmd":1,"megs":"{\"T\":114,\"led\":255}"}` | Envía `megs` a la MAC dada (o a `FF:FF:FF:FF:FF:FF` para broadcast). |

### Archivos / misiones / WiFi

| Comando | Ejemplo | Explicación |
|---|---|---|
| **T:222** — Añadir paso a misión | `{"T":222,"name":"boot","step":"{\"T\":301,\"mode\":0}"}` | Agrega un comando al archivo `boot.mission` (se ejecuta en cada arranque). Ej.: desactivar ESP-NOW al bootear. |
| **T:203** — Borrar archivo | `{"T":203,"name":"boot.mission"}` | Borra un archivo (p.ej. `boot.mission`; se recrea vacío en el siguiente arranque). |
| **T:404** — CMD_WIFI_APSTA | `{"T":404,"ap_ssid":"UGV","ap_password":"12345678","sta_ssid":"your_ssid","sta_password":"password"}` | Configura AP+STA. Si conecta, la IP asignada aparece en la línea "ST" del OLED y la config se guarda de forma persistente. |

---

## 4. Tutoriales de la placa (I–VIII) — resumen técnico

> Nota: la numeración de los tutoriales difiere entre la página del WAVE ROVER
> (I–VIII) y la de la placa (I–XI, que añade demos extra de encoder y el de
> LiDAR/ROS2). Aquí se usa la numeración del WAVE ROVER.

### Tutorial I — Motor con encoder (lectura de velocidad, `speedget.ino`)

- Qué enseña: contar pulsos de encoder Hall por interrupción y calcular RPM del eje de salida.
- Librerías: ninguna externa (core ESP32; `attachInterrupt`, `IRAM_ATTR`).
- Pines: AENCA=35, AENCB=34, BENCA=27, BENCB=16, todos `INPUT_PULLUP`; interrupción RISING en AENCB/BENCB.
- Datos: ejemplo con motor DCGM3865, reducción **1:42**, **11 ppr**/Hall → 462 flancos por vuelta de eje; ventana de cálculo 100 ms; `rpm = (pulsos/shaft_ppr)·60·(1000/interval)`. Serie a 115200.
- No aplica al WAVE ROVER (motores sin encoder), pero define los pines si algún día se cambia a motores con encoder.

### Tutorial II — Motor sin encoder (`nospeedget.ino`)

- Qué enseña: control en lazo abierto de los 2 canales del TB6612FNG con LEDC.
- Librerías: core ESP32 (`ledcSetup`/`ledcAttachPin`/`ledcWrite`).
- Pines: PWMA=25, AIN1=21, AIN2=17, PWMB=26, BIN1=22, BIN2=23.
- Configuración: canales ledc **0 (A)** y **1 (B)**, frecuencia **100 000 Hz**, resolución **8 bits** (0–255). Sentido "adelante": `IN1=LOW, IN2=HIGH`.
- Este es el esquema de control que usa el WAVE ROVER real.

### Tutorial III — Servo de bus ST3215 (`Servo.ino`)

- Qué enseña: mover un servo serie ST3215 en posición/velocidad/aceleración.
- Librerías: **SCServo** (clase `SMS_STS`), instalada en `Arduino15/libraries`.
- Pines/bus: `Serial1.begin(1000000, SERIAL_8N1, S_RXD=18, S_TXD=19)`.
- API ejemplo: `st.WritePosEx(id=1, pos=4095, speed=3400, acc=50)` (rango de posición 0–4095).

### Tutorial IV — Servo PWM (`pwmServo.ino`)

- Qué enseña: mover un servo PWM estándar por el conector IO de la placa.
- Librerías: **ESP32Servo** (`ESP32_Servo.h`).
- Pines: PSERVO_PIN = **GPIO 4** (el mismo IO4 de `T:132`), canal ledc **7**, posición inicial 90°.
- Restricción: solo servos pequeños tipo WP90 (no MG996R/MG90S).

### Tutorial V — Lectura de IMU (`9DOF_Demo.ino`)

- Qué enseña: leer roll/pitch/yaw, datos crudos de gyro/acel/mag y temperatura del IMU de 9 ejes (QMI8658 + AK09918C).
- Librerías: `IMU.h` propia del demo (funciones `imuInit()`, `imuDataGet(&angles,&gyro,&accel,&mag)`, `QMI8658_readTemp()`).
- Estructuras: `IMU_ST_ANGLES_DATA` (fRoll/fPitch/fYaw), `IMU_ST_SENSOR_DATA` (crudos).
- Convención: Roll = rotación en X, Pitch = rotación en Y, Yaw = rotación en Z.
- La wiki no lista registros ni rangos del QMI8658 en esta página; existe un `Demo_v2` descargable. Direcciones I2C (verificadas en nuestro bus): QMI8658 = **0x6B**, AK09918 = **0x0C**.

### Tutorial VI — Lectura de tarjeta SD (`SDCard.ino`)

- Qué enseña: montar y leer/escribir/borrar archivos y test de I/O en la TF.
- Librerías: `FS.h`, `SD.h`, `SPI.h` (hay que borrar la carpeta `SD` duplicada de `Arduino15/libraries`).
- Pines: **HSPI** con SCK=14, MISO=12, MOSI=13, CS=15; `SD.begin(CS, spi, 80000000)` (80 MHz).
- Config: tarjeta en **FAT32**. Subir el sketch **antes** de insertar la SD (si no, falla la subida).

### Tutorial VII — Monitoreo INA219 (`INA219.ino`)

- Qué enseña: leer tensión de bus, tensión de shunt, corriente y potencia de la alimentación.
- Librerías: **INA219_WE** + `Wire`.
- Bus/dirección: `Wire.begin(S_SDA=32, S_SCL=33)`; **INA219_ADDRESS = 0x42**.
- **Calibración clave**: `setADCMode(BIT_MODE_9)`, `setPGain(PG_320)` (±320 mV), `setBusRange(BRNG_16)` (16 V), **`setShuntSizeInOhms(0.01)` → shunt de 0.01 Ω**.
- Cálculo: `loadVoltage_V = busVoltage_V + shuntVoltage_mV/1000`; también `getOverflow()`.

### Tutorial VIII — Control de pantalla OLED (`SSD1306.ino`)

- Qué enseña: mostrar texto en el OLED por I2C.
- Librerías: **Adafruit_SSD1306** + `Wire`.
- Bus/dirección: `Wire.begin(S_SDA=32, S_SCL=33)`; **SCREEN_ADDRESS = 0x3C** (0x3D sería para 128×64).
- Config: **128 × 32 px**, `OLED_RESET = -1` (comparte reset), `SSD1306_SWITCHCAPVCC`.

---

## 5. Recursos descargables

Archivos publicados por Waveshare (en `files.waveshare.com/upload/...`):

| Recurso | Archivo |
|---|---|
| Plano DXF del chasis | `WAVE_ROVER_DXF.rar` |
| Plano PDF del chasis | `WAVE_ROVER_PDF.rar` |
| Plano DXF de la placa de montaje | `WAVE_ROVER-EP_DXF.rar` |
| Plano PDF de la placa de montaje | `WAVE_ROVER-EP_PDF.rar` |
| Modelo 3D (STL) | `WAVE_ROVER_MODEL_STL.rar` |
| Demo open-source (Arduino) | `WAVE_ROVER_demo.zip` |
| Firmware de fábrica + flasher | `WAVE_ROVER_FACTORY-25.zip` (incluye `flash_download_tool_3.9.5.exe`) |

Otros:

- Programa de host para Raspberry Pi: **https://github.com/waveshareteam/ugv_rpi** (con `setup.sh`, `autorun.sh` y AccessPopup para conmutación automática WiFi/hotspot).
- Scripts de ejemplo de la wiki: `http_simple_ctrl.py` (HTTP: `http://IP/js?json=...`) y `serial_simple_ctrl.py` (serie 115200, RTS/DTR en False).
- Para la placa suelta: esquemático ("Circuit Diagram"), plano `GENERAL-DRIVER-FOR-ROBOTS-STR` (DXF/PDF) y modelo STEP, más el demo open-source de UGV01 — enlazados desde la página `General_Driver_for_Robots` de la wiki.

---

## 6. Notas de integración con nuestro stack (waver_slate_v2)

**Qué NO aplica del firmware stock.** Usamos firmware I2C custom
(`waver_slate_v2`) en el ESP32, no el firmware de fábrica, por lo tanto:

- Todo el **set de comandos JSON (§3) no existe** en nuestro robot: ni UART JSON a 115200, ni web app en 192.168.4.1, ni hotspot `UGV`, ni ESP-NOW, ni heartbeat de 3 s, ni `boot.mission`. Se documenta solo como referencia del comportamiento de fábrica y por si se reflashea el firmware stock (`WAVE_ROVER_FACTORY-25.zip`).
- `ugv_rpi` (host stock) tampoco se usa; nuestro host es ROS 2 en la RPi 5.
- T:13 (ROS_CTRL) y T:2 (PID) no aplicarían ni con firmware stock: son solo para UGV01 con encoders.
- La RPi lee **directamente por `/dev/i2c-1`** los sensores del bus periférico del ESP32 (S_SDA=GPIO32 / S_SCL=GPIO33): **QMI8658 @ 0x6B, AK09918 @ 0x0C, INA219 @ 0x42**. El ESP32 queda como esclavo I2C para el control de motores. Implicación: el firmware custom **no** debe hacer de master agresivo sobre ese bus mientras la Pi lo usa (bus compartido).

**Qué datos de la wiki alimentan la calibración:**

- **URDF**: dimensiones del chasis 194×168×100 mm; motores N20 de 34×12 mm con eje de 4×10 mm; placa driver de 65×65 mm (taladros 49×58 mm) para posicionar el frame del IMU respecto a `base_link`; convención IMU Roll=X, Pitch=Y, Yaw=Z.
- **`cmd_vel_to_motors`**: velocidad máxima real **1.25 m/s** a PWM 255 (mapeo lineal de referencia: 0.5 "speed" stock = 100 % PWM); PWM del TB6612 a **100 kHz / 8 bits**; existencia de **zona muerta** a PWM bajo (motores sin encoder, lazo abierto — la wiki lo advierte explícitamente); sin encoders no hay feedback de velocidad: cualquier odometría de ruedas es estimada por modelo.
- **Monitor de batería**: INA219 con **shunt de 0.01 Ω**, PG_320, rango de bus 16 V — misma calibración que debe usar nuestro nodo de la Pi al configurar el INA219 en 0x42; batería 3S (nominal 11.1 V, carga a 12.6 V) para los umbrales de alerta de tensión.
- **Reserva de pines**: si se añaden periféricos al ESP32, evitar GPIO 25/26/21/17/22/23 (motores), 18/19 (bus servo), 32/33 (I2C compartido con la Pi), 14/12/13/15 (SD), 4/5 (IO4/IO5 PWM libres) y 34/35/27/16 (encoders, hoy libres en WAVE ROVER).
