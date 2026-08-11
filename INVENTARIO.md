# INVENTARIO.md — Contexto maestro de hardware del ecosistema Waver/SOMA

**Regla de oro: toda compra se registra aquí AL LLEGAR, con referencia exacta,
cantidad, estado y ubicación.** Este archivo existe porque el 2026-08-10 se
descubrió que la información de compras vivía solo en chats y se perdió.
Reconstruido ese día desde la memoria de sesiones (etiquetas `mem #ID`),
correos de envío (`correo`) y confirmación directa de Andrés (`ANDRÉS`).

Estados: **EN MANO** (visto y usado) · **EN MANO?** (llegó, falta verificar
referencia/cantidad) · **DECIDIDO** (elegido en sesión, compra sin confirmar) ·
**EVALUADO** (investigado, no elegido).

---

## Cómputo y visión

| Ítem | Ref/Detalle | Cant | Estado | Fuente |
|---|---|---|---|---|
| Jetson Orin Nano Super Dev Kit | 8GB, JetPack 7.2 en NVMe, MAXN_SUPER | 1 | EN MANO | correo Amazon 08-jul + sesiones |
| SSD NVMe (boot Jetson) | ref por confirmar | 1 | EN MANO? | sesión 30-jul |
| Raspberry Pi 5 | corre stack Waver | 1 | EN MANO | sesiones |
| OAK-D Lite | 3 demos funcionando en Jetson | 1 | EN MANO | sesión 30-jul |
| Cable USB 3.1 10Gbps 13cm | PD 100W, A→C OTG (para OAK) | 1 | EN MANO? | mem #1899 |
| ESP32 (driver board Waveshare) | en el rover Wave Rover | 1 | EN MANO | sesiones Waver |

## Actuación

| Ítem | Ref/Detalle | Cant | Estado | Fuente |
|---|---|---|---|---|
| Brazos ROT3U 6DOF aluminio | kit 490g s/servos, 460mm alto, alcance 355mm | 2 | EN MANO | mem #2109 + banco |
| Servos MG996R (en brazos) | 12 instalados y calibrados 03-ago | 12 | EN MANO | banco |
| Servos MG995/MG996R (repuesto) | lote AliExpress | 5 | EN MANO? | mem #1899 |
| Actuonix L16-140-63-6-R | torso; ch3; convención INVERTIDA | 1 | EN MANO | banco 22-jul |
| Motores 12GA-N20 hall 12V 300RPM | con bracket, para tracción rover (cant. exacta por contar) | 2+ | EN MANO | mem #1899 + ANDRÉS 10-ago |
| Horns disco aluminio 25T | p/ MG995/996, ~$15.598 COP x10 | 10 | EN MANO | mem #1905 + re-splines |
| Pinzas LG-KT (Lynxmotion style) | garra engranada de los brazos | 2 | EN MANO | banco |

## Potencia

| Ítem | Ref/Detalle | Cant | Estado | Fuente |
|---|---|---|---|---|
| Baterías DeWalt DCB203-B3 | 20V MAX 2.0Ah, del taladro (con cargador); rotación trabajo/carga | **2** | EN MANO | ANDRÉS 10-ago |
| Packs 6Ah compatibles (Waitley) | 2×6Ah ~$323k COP, para marathon | 2 | DECIDIDO (no comprados; con 2×2Ah alcanza por ahora) | mem #2162 + ANDRÉS 10-ago |
| Adaptador/dock DeWalt salida cables | **Amazon B0B9NPZM3M**: kit Power Wheels c/ switch, fusible y 12AWG | 1 | EN MANO | ANDRÉS 10-ago |
| UBEC Hobbywing 5A V2 | entrada 2-8S, jumper 5/6/7.4V | **2** | EN MANO | mem #1899/#1854 + banco |
| Conversor-dock 20V→12V 240W | **Amazon B0FP1B1F86**: el pack se monta EN el dock; salida 12V/20A regulada; **UVLO 15.2V** + sobrecorriente/corto/sobretemp; fusible 30A incluido; **cable AMARILLO=positivo** | 1 | EN MANO | listing 10-ago |
| Módulo MOSFET relay | **D4184 (AOD4184)**, serigrafía "HeilandLv D4184": 40V/50A, entrada lógica 3.3V OK, conmutación lado bajo | 1+ | EN MANO | ANDRÉS 10-ago |
| Módulos diodo ideal anti-retorno | DC5-60V 15A | **2** | EN MANO | ANDRÉS 10-ago |
| Módulo ORing LM66200 (WeAct) | $7.098 COP, conmutación dual | 0 | EVALUADO, no comprado | ANDRÉS 10-ago |
| Placa dual switching 15A UPS | $41.285 COP, alternativa al ORing | 0 | EVALUADO, no comprado | ANDRÉS 10-ago |
| LiPo 2S + UBEC (banco original) | cadena de banco pre-DeWalt | 1 | EN MANO | banco |
| XT60 macho/hembra c/ cable | 100mm 14AWG silicona, item 1005012281077296 | set | EN MANO | mem #1855 + banco |
| Fusibles | repuestos ~30A (ubicación olvidada); el del kit B0B9NPZM3M probablemente 30A | var | EN MANO? | ANDRÉS 10-ago |
| **Fusibles 7.5A-10A (COMPRAR)** | para la rama servos: 30A no protege un arnés de 14-16AWG | 0 | **PENDIENTE COMPRA** | análisis 10-ago |
| Conector barrel DC 5.5×2.5mm macho | para la Jetson desde el dock 12V; centro POSITIVO; **verificado: entra justo y firme** | 1 | EN MANO | ANDRÉS 10-ago |

## Sensores y monitoreo

| Ítem | Ref/Detalle | Cant | Estado | Fuente |
|---|---|---|---|---|
| INA3221 triple canal I2C | shunts 0.1Ω 2W, ±1.638A/canal, dir 0x40/41/44/45, $7.466 COP | **3** | EN MANO | ANDRÉS 10-ago |
| INA219 (rover) | monitor batería 3S del Wave Rover | 1 | EN MANO | mem #857 |
| Iluminador IR 850nm 12V IP66 | 4 LED gran angular | 1 | EN MANO? | mem #1899 |
| Pogo pins magnéticos | 10A 24V/18A M/H (dock futuro; largo de cable en duda) | set | EN MANO? | mem #1899/#2170 |
| OLED SSD1306 | I2C 0x3C, panel batería rover | 1 | EN MANO | mem #2162 |

## Conectores, cables y mecánica

| Ítem | Ref/Detalle | Cant | Estado | Fuente |
|---|---|---|---|---|
| Extensiones servo Futaba/JR | 22AWG trenzadas 75-1000mm, item 1005007301246561, x10 | 10 | EN MANO | mem #1860 + arnés 10-ago |
| PCA9685 16ch I2C | **comprados 2 por redundancia** | **2** | EN MANO | mem #1850/#1899 |
| Tornillería ISO7380 inox 304 | surtido M2-M12 hex socket | kit | EN MANO? | mem #1899 |
| Regleta pines hembra (header Jetson) | arnés definitivo I2C, soldada 10-ago | 1 | EN MANO | banco 10-ago |
| Duponts / pines largos | para cortar-soldar-termoencoger | var | EN MANO | mem #1905 |
| Soporte de monitor (rig banco) | columna + placa, banco colgante SOMA | 1 | EN MANO | banco |

## Mapa I2C oficial (bus i2c-7 en Jetson)

| Dir | Dispositivo | Nota |
|---|---|---|
| 0x40 | PCA9685 #1 | actual |
| 0x41 | PCA9685 #2 | futuro plan dos rieles (puente A0) |
| 0x44 | INA3221 | **no 0x42**: el módulo salta 0x40/41/44/45 |

## Checklist VERIFICADO por Andrés el 10-ago-2026

Todo lo mandado a comprar llegó. Confirmaciones incorporadas arriba.
Quedan vivos:

1. **LISTA DE COMPRAS COMPLETA (solo 2 ítems)**: fusible 7.5-10A para la rama de servos + **pila 9V para el multímetro**.
2. **Ubicar los fusibles de repuesto** de 30A (guardados en lugar olvidado).
3. **Contar los motores N20** con encoder (cantidad exacta).
4. ~~Umbral de sobredescarga del conversor~~ **RESUELTO 10-ago: 15.2V** (listing B0FP1B1F86). El piso de software se alineó a 15.2V. Regla extra del fabricante: **sacar la batería del dock cuando no se use** (drenaje parásito).
5. Ítems del rover Waver (lidar, ruedas, etc.): sesión de inventario aparte.
