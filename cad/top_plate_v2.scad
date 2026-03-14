// ============================================================
//  Zuup Macropad — TOP PLATE
//  PCB: 65.2 x 80.9mm  |  Plate: 1.5mm
//  Sits on top of tray rim, screws from top into tray bosses
// ============================================================
// ADJUST THESE if holes are off after first print:
//   MX_X0, MX_Y0 — shift entire switch grid
//   OLED_CX, OLED_CY — shift OLED window
//   ENC_CX, ENC_CY — shift encoder hole
// ============================================================

$fn = 64;

// ── PCB & plate dims ────────────────────────────────────────
PCB_W    = 65.2;
PCB_H    = 80.9;
TOP_T    = 1.5;
CORNER_R = 3.0;

// ── MX switches — 3x3 grid, 19.05mm pitch ──────────────────
// MX_X0/Y0 = centre of BOTTOM-LEFT switch (S7) from plate origin
MX_HOLE  = 14.0;
MX_PITCH = 19.05;
MX_X0    = 10.575;   // col 0 centre X  (tune me)
MX_Y0    = 14.275;   // row 0 centre Y  (tune me)

// ── OLED 0.91" (128x32) ─────────────────────────────────────
// Opening for display glass only
OLED_W   = 25.0;
OLED_H   = 10.5;
OLED_CX  = 20.5;     // centre X from plate left  (tune me)
OLED_CY  = 73.5;     // centre Y from plate bottom (tune me)
OLED_R   = 1.2;      // corner radius of opening

// ── Rotary encoder EC11 ─────────────────────────────────────
ENC_CX   = 54.5;     // (tune me)
ENC_CY   = 72.5;     // (tune me)
ENC_D    = 7.0;      // shaft hole — 6mm shaft + 0.5mm clearance

// ── SW1 tact reset button ───────────────────────────────────
SW1_CX   = 57.2;
SW1_CY   = 62.5;
SW1_W    = 4.0;
SW1_H    = 2.8;
SW1_R    = 0.8;

// ── M2 screws — 4 corners, countersunk from top ─────────────
// Matches boss positions in bottom tray
SCREW_D  = 2.4;      // M2 clearance through plate
CSNK_D   = 4.0;      // countersink head diameter
CSNK_H   = 1.2;      // countersink depth
BOSSES = [
    [5.5,  5.5 ],
    [59.7, 5.5 ],
    [5.5,  75.4],
    [59.7, 75.4],
];

// ============================================================

difference() {

    // ── Plate body ──────────────────────────────────────────
    hull()
        for (x = [CORNER_R, PCB_W - CORNER_R])
            for (y = [CORNER_R, PCB_H - CORNER_R])
                translate([x, y, 0])
                    cylinder(r=CORNER_R, h=TOP_T);

    // ── 9x MX switch holes (14x14mm square, sharp corners) ──
    for (row = [0:2])
        for (col = [0:2])
            translate([
                MX_X0 + col*MX_PITCH - MX_HOLE/2,
                MX_Y0 + row*MX_PITCH - MX_HOLE/2,
                -0.01
            ])
            cube([MX_HOLE, MX_HOLE, TOP_T + 0.02]);

    // ── OLED display window ──────────────────────────────────
    translate([OLED_CX - OLED_W/2, OLED_CY - OLED_H/2, -0.01])
        rslot(OLED_W, OLED_H, TOP_T + 0.02, OLED_R);

    // ── Encoder shaft hole ───────────────────────────────────
    translate([ENC_CX, ENC_CY, -0.01])
        cylinder(d=ENC_D, h=TOP_T + 0.02);

    // ── SW1 button hole ──────────────────────────────────────
    translate([SW1_CX - SW1_W/2, SW1_CY - SW1_H/2, -0.01])
        rslot(SW1_W, SW1_H, TOP_T + 0.02, SW1_R);

    // ── M2 countersunk screw holes ───────────────────────────
    for (b = BOSSES) {
        // through hole
        translate([b[0], b[1], -0.01])
            cylinder(d=SCREW_D, h=TOP_T + 0.02);
        // countersink (from top face down)
        translate([b[0], b[1], TOP_T - CSNK_H + 0.01])
            cylinder(d1=SCREW_D, d2=CSNK_D, h=CSNK_H + 0.01);
    }
}

// ── Helper ───────────────────────────────────────────────────
module rslot(w, h, d, r) {
    hull()
        for (x = [r, w-r])
            for (y = [r, h-r])
                translate([x, y, 0])
                    cylinder(r=r, h=d);
}
