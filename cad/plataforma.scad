// ============================================================================
//  WAVER CRAB — Montaje superior completo del Wave Rover
//  Bio-inspirado (cangrejo) / profesional / futurista — para impresión 3D
//
//  Origen: centro de la TAPA del rover. X adelante, Y izquierda, Z arriba.
//  Medidas del chasis tomadas del URDF (waver.urdf.xacro): 194 x 110 x 55.
//  [calibrar] = medir con calibrador antes de imprimir.
//
//  Uso:  F5 preview | girar con mouse | 'mostrar' elige pieza para exportar
// ============================================================================

$fa = 3; $fs = 0.6;

// ------------------------- MODO DE VISUALIZACION ---------------------------
mostrar = "ensamblaje";  // ensamblaje | bandeja | caparazon | torre | bahia
                         // brazo | garra | visor
explode = 0;             // 0 = armado; sube a 25 para vista explosionada
fantasma_chasis = true;  // rover translucido debajo, para contexto

// pose de demo de los brazos (grados)
pose_yaw     = 52;       // 0 = brazo lateral puro, 90 = apuntando al frente
pose_hombro  = 26;       // elevacion del humero
pose_codo    = -58;      // flexion del antebrazo (abraza hacia adelante)
pose_muneca  = -14;      // inclinacion de la garra
pose_pinza   = 24;       // apertura de la garra

// ------------------------- CHASIS (del URDF) -------------------------------
chasis_l = 194;  chasis_w = 110;  chasis_h = 55;
rueda_r  = 30;   rueda_w  = 26;   rueda_sep = 125;  rueda_base = 110;

// ------------------------- PLATAFORMA / BANDEJA ----------------------------
plat_l = 200;  plat_w = 144;  plat_t = 4;
// patron de tornillos M3 de la tapa del rover [calibrar]
tornillos = [[70,35],[70,-35],[-70,35],[-70,-35],[0,42],[0,-42]];
tornillo_d = 3.4;

// ------------------------- BATERIA TALADRO (rear, bajo) --------------------
bat_l = 116; bat_w = 76; bat_h = 62;      // pack DeWalt-compat [calibrar]
cuna_h = 14;                               // cuna adaptadora bajo el pack
bay_pared = 3;
bay_cx = -38;                              // centro de la bahia (atras)
holgura = 1.0;

// ------------------------- LIDAR LD06 (torre periscopio) -------------------
lidar_d = 38; lidar_h = 34;
torre_h = 58;                              // deja el plano de barrido sobre TODO
torre_d_base = 52; torre_d_top = 44;

// ------------------------- OAK-D LITE (visor frontal) ----------------------
oak = [17, 91, 28];
visor_x = 94;  visor_z = 26;  visor_tilt = 8;   // asoma del caparazon como ojos

// ------------------------- SERVOS ------------------------------------------
mg  = [40.7, 19.7, 42.9];   // MG996R cuerpo
mg_flange_l = 54.5;  mg_eje_off = 10.3;    // eje descentrado hacia el frente
s3  = [40.0, 20.0, 38.0];   // S3003

// ------------------------- BRAZOS CANGREJO ---------------------------------
hombro_x = 12;                             // los brazos parten del centro
hombro_y = plat_w/2 - 12;
l_humero = 78;                             // hombro -> codo
l_ante   = 66;                             // codo -> muneca
l_garra  = 72;                             // muneca -> punta de pinza
carcasa_esp = 3;

// ------------------------- PALETA ------------------------------------------
c_shell   = "#262a30";   // caparazon grafito
c_acento  = "#ff7a18";   // naranja cangrejo/futurista
c_panel   = "#3a4048";
c_servo   = "#17181c";
c_sensor  = "#1e3a5f";
c_garra   = "#e8e4dc";   // marfil de pinza

// ============================================================================
//  UTILIDADES
// ============================================================================
module prisma(v, ch=2) {  // caja con chaflanes verticales (look facetado)
  hull() for (dx=[-1,1], dy=[-1,1])
    translate([dx*(v[0]/2-ch), dy*(v[1]/2-ch), 0])
      cylinder(h=v[2], r=ch, $fn=8);
}
module espejo_y() { children(); mirror([0,1,0]) children(); }

// ============================================================================
//  SERVOS (siluetas realistas para verificar encaje)
// ============================================================================
module servo_mg996r() {
  color(c_servo) {
    translate([-mg_eje_off, -mg[1]/2, -mg[2]+11.5]) cube([mg[0], mg[1], mg[2]-11.5]);
    // orejas de montaje
    translate([-mg_flange_l/2 + (mg[0]/2 - mg_eje_off), -mg[1]/2, -14])
      cube([mg_flange_l, mg[1], 2.6]);
  }
  color("goldenrod") cylinder(h=4, d=5.9);          // spline
  color(c_servo) translate([0,0,-11.5]) cylinder(h=11.5, d=13);
}
module servo_s3003() {
  color(c_servo) translate([-10, -s3[1]/2, -s3[2]+10]) cube([s3[0], s3[1], s3[2]-10]);
  color("white") cylinder(h=4, d=5.9);
}

// ============================================================================
//  BANDEJA BASE (se atornilla a la tapa del rover)
// ============================================================================
module bandeja() {
  color(c_panel) difference() {
    translate([0,0,0]) linear_extrude(plat_t)
      offset(r=8) offset(delta=-8) square([plat_l, plat_w], center=true);
    for (p = tornillos) translate([p[0], p[1], -1])
      cylinder(h=plat_t+2, d=tornillo_d);
    // ventana de la bateria: el pack atraviesa la bandeja (CG lo mas bajo)
    translate([bay_cx, 0, plat_t/2])
      cube([bat_l+2*holgura, bat_w+2*holgura, plat_t+4], center=true);
    // ranuras de peso/ventilacion estilo branquias
    for (i=[-2:2]) translate([55, i*14, plat_t/2])
      prisma([26, 6, plat_t+4], 2);
  }
}

// ============================================================================
//  BAHIA DE BATERIA (acceso trasero, rieles laterales, techo abovedado)
// ============================================================================
module bahia() {
  wl = bat_l + 2*holgura;  ww = bat_w + 2*holgura;
  alto = cuna_h + bat_h + 4;
  color(c_shell) translate([bay_cx, 0, plat_t]) difference() {
    prisma([wl + 2*bay_pared, ww + 2*bay_pared, alto], 4);
    translate([0,0,-1]) prisma([wl, ww, alto+2], 3);
    // boca trasera: el pack se desliza hacia atras
    translate([-wl/2 - bay_pared - 1, -ww/2, -1])
      cube([bay_pared + wl/2, ww, alto+2]);
    // ventanas laterales de agarre y ventilacion
    espejo_y() translate([0, ww/2, alto*0.55])
      rotate([90,0,0]) prisma([wl*0.6, alto*0.5, bay_pared*4], 5);
  }
  // rieles internos donde asienta la cuna
  color(c_acento) espejo_y()
    translate([bay_cx, ww/2 - 4, plat_t]) cube([wl*0.8, 3, 4], center=false);
  // pestillo trasero (clip impreso, mantiene el pack adentro)
  color(c_acento) translate([bay_cx - wl/2 - bay_pared, 0, plat_t + alto - 6])
    rotate([0,90,0]) prisma([8, 26, 4], 2);
  // fantasma del pack para verificar encaje
  %translate([bay_cx, 0, plat_t + cuna_h + bat_h/2])
    cube([bat_l, bat_w, bat_h], center=true);
}

// ============================================================================
//  CAPARAZON (domo facetado con cola alzada sobre la bateria y branquias)
// ============================================================================
module caparazon_solido() {
  hull() {
    // frente bajo y afilado (rostro del cangrejo)
    translate([plat_l/2-30, 0, plat_t]) prisma([50, plat_w*0.62, 16], 8);
    // centro: lomo
    translate([10, 0, plat_t]) prisma([90, plat_w*0.96, 30], 12);
    // cola alta: cubre la bahia de la bateria
    translate([bay_cx, 0, plat_t]) prisma([bat_l*0.95, plat_w*0.9, cuna_h+bat_h+10], 10);
  }
}
module caparazon() {
  color(c_shell) difference() {
    caparazon_solido();
    // vaciado interior
    translate([0,0,-carcasa_esp]) scale([0.94,0.92,0.97]) caparazon_solido();
    // paso de la torre del lidar
    translate([0,0,plat_t]) cylinder(h=200, d=torre_d_base+1);
    // tunel de la bahia (que el caparazon no tape el swap trasero)
    translate([bay_cx-6, 0, plat_t + (cuna_h+bat_h)/2])
      cube([bat_l+2*bay_pared+14, bat_w+2*bay_pared+2, cuna_h+bat_h+6], center=true);
    // ventana del visor OAK
    translate([visor_x-6, 0, visor_z]) rotate([0,visor_tilt,0])
      cube([26, oak[1]+6, oak[2]+8], center=true);
    // vanos de los hombros
    espejo_y() translate([hombro_x, hombro_y, plat_t+14]) prisma([70, 46, 60], 8);
    // branquias laterales (x3 por flanco)
    espejo_y() for (i=[0:2])
      translate([48 - i*20, plat_w/2 - 6, plat_t + 10])
        rotate([0, -18, 0]) rotate([90, 0, 0]) prisma([9, 26, 30], 3);
    // linea de luz frontal (canal para tira LED futurista)
    translate([plat_l/2 - 22, 0, plat_t + 13]) rotate([0,96,0])
      prisma([4, plat_w*0.5, 8], 1.5);
  }
  // cejas/acentos naranjas sobre las branquias
  color(c_acento) espejo_y() for (i=[0:2])
    translate([48 - i*20, plat_w/2 - 3.2, plat_t + 24])
      rotate([0, -18, 0]) cube([2.5, 2.5, 14], center=true);
}

// ============================================================================
//  TORRE PERISCOPIO DEL LIDAR (el ojo elevado: barrido 360 despejado)
// ============================================================================
module torre_lidar() {
  color(c_shell) difference() {
    cylinder(h=torre_h, d1=torre_d_base, d2=torre_d_top);
    translate([0,0,-1]) cylinder(h=torre_h+2, d1=torre_d_base-8, d2=torre_d_top-8);
  }
  // costillas exteriores (estetica + rigidez de impresion)
  color(c_acento) for (a=[0:60:359]) rotate([0,0,a])
    translate([torre_d_base/2-2, 0, 0])
      linear_extrude(torre_h, scale=0.86) square([2.4, 3], center=true);
  // plato superior + LD06
  color(c_panel) translate([0,0,torre_h]) cylinder(h=3, d=torre_d_top);
  translate([0,0,torre_h+3]) {
    color(c_sensor) cylinder(h=lidar_h, d=lidar_d);
    color("black") translate([0,0,lidar_h-9]) cylinder(h=6, d=lidar_d+1);
    // plano de barrido (fantasma, anillo fino): NADA debe cruzarlo
    %translate([0,0,lidar_h-6]) difference() {
      cylinder(h=0.8, d=320);
      translate([0,0,-1]) cylinder(h=3, d=312);
    }
  }
}

// ============================================================================
//  VISOR OAK (ojos frontales bajo una visera angular)
// ============================================================================
module visor_oak() {
  translate([visor_x, 0, visor_z]) rotate([0, visor_tilt, 0]) {
    color(c_shell) difference() {
      prisma([16, oak[1]+14, oak[2]+12], 5);
      translate([3, 0, 0]) cube([16, oak[1]+0.8, oak[2]+0.8], center=true);
    }
    // OAK-D Lite (fantasma de encaje)
    %color(c_sensor) cube([oak[0], oak[1], oak[2]], center=true);
    // ceja-visera
    color(c_acento) translate([6, 0, oak[2]/2 + 5])
      rotate([0, 18, 0]) prisma([3, oak[1]+14, 6], 1.5);
  }
}

// ============================================================================
//  BRAZO CANGREJO:  yaw (S3003) -> hombro (MG996R) -> codo (MG996R)
//                   -> muneca (S3003) -> garra (MG996R)
// ============================================================================
module segmento(l, d1, d2) {   // carcasa facetada de un eslabon
  hull() {
    sphere(d=d1, $fn=10);
    translate([l,0,0]) sphere(d=d2, $fn=10);
  }
}
module garra(apertura) {
  // palma con MG996R de la pinza
  color(c_garra) segmento(24, 26, 30);
  translate([16,0,10]) rotate([180,0,0]) scale(0.72) servo_mg996r();
  // dedo fijo (abajo) — curva de pinza con dientes
  color(c_garra) translate([22,0,-6]) {
    hull() { sphere(d=16,$fn=10); translate([l_garra-30, 0, 6]) sphere(d=7,$fn=8); }
    for (i=[1:4]) translate([8 + i*9, 0, 4 - i*0.4])
      rotate([0,32,0]) cube([3.2, 4, 7], center=true);
  }
  // dedo movil (arriba) — rota con el servo
  color(c_garra) translate([22,0,8]) rotate([0, -apertura, 0]) {
    hull() { sphere(d=16,$fn=10); translate([l_garra-30, 0, -5]) sphere(d=7,$fn=8); }
    for (i=[1:4]) translate([8 + i*9, 0, -3.5 + i*0.4])
      rotate([0,-32,0]) cube([3.2, 4, 7], center=true);
  }
  // acento
  color(c_acento) translate([22,0,1]) sphere(d=10, $fn=10);
}
module nudillo(d) {  // articulacion facetada: envuelve el servo del joint
  color(c_shell) sphere(d=d, $fn=10);
  color(c_acento) rotate([90,0,0]) cylinder(h=d+2, d=d*0.32, center=true, $fn=8);
}
module brazo_izq() {  // brazo del lado +Y; el derecho es su espejo
  translate([hombro_x, hombro_y, plat_t + explode/2]) {
    // pod del hombro: S3003 de yaw en vertical dentro de un torreon facetado
    color(c_shell) difference() {
      prisma([56, 42, 34], 7);
      translate([0,0,8]) prisma([44, 26, 34], 5);
    }
    translate([0, 0, 28]) servo_s3003();
    // cadena: yaw -> hombro -> codo -> muneca -> garra
    rotate([0, 0, 90 - pose_yaw]) translate([0, 0, 34 + explode]) {
      nudillo(34);
      rotate([0, -pose_hombro, 0]) {
        color(c_shell) segmento(l_humero, 30, 24);
        color(c_acento) translate([l_humero*0.45, 0, 13]) prisma([20,3,4],1);
        translate([l_humero + explode, 0, 0]) {
          nudillo(30);                       // codo (MG996R adentro)
          %rotate([90,0,0]) scale(0.85) servo_mg996r();
          rotate([0, -pose_codo, 0]) {
            color(c_shell) segmento(l_ante, 24, 18);
            translate([l_ante + explode, 0, 0]) {
              nudillo(24);                   // muneca (S3003 adentro)
              rotate([0, pose_muneca, 0])
                translate([6 + explode, 0, 0]) garra(pose_pinza);
            }
          }
        }
      }
    }
  }
}

// ============================================================================
//  CHASIS FANTASMA (contexto: el rover debajo)
// ============================================================================
module chasis_fantasma() {
  %translate([0,0,-chasis_h/2]) cube([chasis_l, chasis_w, chasis_h], center=true);
  %for (dx=[-1,1], dy=[-1,1])
    translate([dx*rueda_base/2, dy*(rueda_sep+rueda_w)/2, -chasis_h+rueda_r-20])
      rotate([90,0,0]) cylinder(h=rueda_w, r=rueda_r, center=true);
}

// ============================================================================
//  ENSAMBLAJE
// ============================================================================
module ensamblaje() {
  if (fantasma_chasis) chasis_fantasma();
  bandeja();
  translate([0,0,explode])     bahia();
  translate([0,0,explode*2])   caparazon();
  translate([0,0,plat_t + 30 + explode*3]) torre_lidar();
  translate([explode,0,0])     visor_oak();
  brazo_izq();
  mirror([0,1,0]) brazo_izq();
}

if (mostrar == "ensamblaje") ensamblaje();
else if (mostrar == "bandeja")   bandeja();
else if (mostrar == "bahia")     bahia();
else if (mostrar == "caparazon") caparazon();
else if (mostrar == "torre")     torre_lidar();
else if (mostrar == "visor")     visor_oak();
else if (mostrar == "brazo")     brazo_izq();
else if (mostrar == "garra")     garra(pose_pinza);
