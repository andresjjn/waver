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
| Motor 12GA-N20 hall 12V 300RPM | con bracket, compra proactiva | 1 | EN MANO? | mem #1899 |
| Horns disco aluminio 25T | p/ MG995/996, ~$15.598 COP x10 | 10 | EN MANO | mem #1905 + re-splines |
| Pinzas LG-KT (Lynxmotion style) | garra engranada de los brazos | 2 | EN MANO | banco |

## Potencia

| Ítem | Ref/Detalle | Cant | Estado | Fuente |
|---|---|---|---|---|
| Batería DeWalt DCB203-B3 | 20V MAX 2.0Ah, del taladro (con cargador) | 1 | EN MANO | mem #1825 + banco 10-ago |
| Packs 6Ah compatibles (Waitley) | 2×6Ah ~$323k COP, para marathon | 2 | DECIDIDO | mem #2162 |
| Adaptador/dock DeWalt salida cables | estilo Power Wheels c/ fusible (Amazon B0B9NPZM3M o ML equiv.) | 1 | EN MANO? | mem #1805/#1589 + banco 10-ago |
| UBEC Hobbywing 5A V2 | entrada 2-8S, jumper 5/6/7.4V | **2** | EN MANO | mem #1899/#1854 + banco |
| Conversor 20V→12V 240W | c/ switch y **protección de sobredescarga**, ~$80k COP | 1 | EN MANO | mem #1903 + banco 10-ago |
| Módulo MOSFET relay aislado | FR120N **o** LR7843 **o** AOD4184 (variante por leer en serigrafía) | ? | EN MANO? | mem #1899 |
| Módulos diodo ideal anti-retorno | DC5-60V 15A (protección carga/solar) | ? | EN MANO? | mem #1899 |
| Módulo ORing LM66200 (WeAct) | $7.098 COP, conmutación dual | ? | EVALUADO | mem #1903 |
| Placa dual switching 15A UPS | $41.285 COP, alternativa al ORing | ? | EVALUADO | mem #1903 |
| LiPo 2S + UBEC (banco original) | cadena de banco pre-DeWalt | 1 | EN MANO | banco |
| XT60 macho/hembra c/ cable | 100mm 14AWG silicona, item 1005012281077296 | set | EN MANO | mem #1855 + banco |
| Fusibles | tipo/amperaje por inventariar | ? | EN MANO? | mem #1850 |

## Sensores y monitoreo

| Ítem | Ref/Detalle | Cant | Estado | Fuente |
|---|---|---|---|---|
| INA3221 triple canal I2C | shunts 0.1Ω 2W, ±1.638A/canal, dir 0x40/41/44/45, $7.466 COP | ? | EN MANO? | mem #1900 + ANDRÉS 10-ago |
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

## POR CONFIRMAR con Andrés (checklist de banco, 10 min)

1. **MOSFET**: leer serigrafía del módulo — ¿FR120N, LR7843 o AOD4184? ¿cuántos?
2. **INA3221**: ¿cuántas unidades llegaron?
3. **Packs Waitley 6Ah**: ¿se compraron o quedó en decisión?
4. **ORing LM66200 / placa dual 15A**: ¿alguno se compró?
5. **Diodos ideales 15A**: ¿cuántos y dónde están?
6. **Adaptador DeWalt**: ¿cuál llegó (Amazon B0B9NPZM3M o el de MercadoLibre)?
7. **Fusibles**: amperajes disponibles.
8. **Conversor 12V**: umbral exacto de su protección de sobredescarga (medir).
9. Ítems Waver rover no listados aún (motores, lidar, etc.): sesión aparte.
