// ============================================================
//  Zuup Macropad — BOTTOM TRAY v3
//  Based on reference keyboard design language
//  PCB: 65.2 x 80.9mm
//  Floor: 3mm  |  Walls: 3mm  |  Inner H: 13.4mm
//  4x screw bosses (OD=10mm, ID=2.2mm)
//  XIAO platform + USB-C slot
//  Rubber feet recesses
// ============================================================

$fn = 64;

PCB_W    = 65.2;
PCB_H    = 80.9;
WALL     = 3.0;      // from reference
FLOOR_T  = 3.0;      // from reference
INNER_H  = 13.4;     // from reference
CORNER_R = 3.0;

// ── Screw bosses — from reference: OD=10mm, corner ones 7.2mm
BOSS_OD     = 9.0;    // scaled slightly for macropad
BOSS_ID     = 2.2;    // M2 self-tap
BOSS_H      = INNER_H - 1.0;  // stop 1mm below rim
BOSS_R      = 1.5;    // boss corner fillet
BOSSES = [
    [5.5,  5.5 ],
    [59.7, 5.5 ],
    [5.5,  75.4],
    [59.7, 75.4],
];

// ── XIAO RP2040 platform ─────────────────────────────────────
// Top-right of tray, raises XIAO so USB-C hits wall slot
XIAO_W   = 22.0;
XIAO_H   = 19.0;
XIAO_Z   = 3.5;      // platform height above floor
XIAO_X   = PCB_W - XIAO_W - 0.5;
XIAO_Y   = PCB_H - XIAO_H - 0.5;

// ── USB-C slot — in top wall (Y=max side) ────────────────────
USBC_W   = 9.5;
USBC_H   = 4.0;
USBC_CX  = XIAO_X + XIAO_W/2;
USBC_Z   = FLOOR_T + XIAO_Z + 1.6 + 0.3;  // floor + platform + PCB + offset

// ── Rubber feet ──────────────────────────────────────────────
FOOT_D     = 10.0;
FOOT_DEPTH = 1.2;
FOOT_IN    = 8.5;
FEET = [
    [FOOT_IN,         FOOT_IN        ],
    [PCB_W - FOOT_IN, FOOT_IN        ],
    [FOOT_IN,         PCB_H - FOOT_IN],
    [PCB_W - FOOT_IN, PCB_H - FOOT_IN],
];

// ── Outer dims ───────────────────────────────────────────────
OW = PCB_W + WALL*2;
OH = PCB_H + WALL*2;
OZ = FLOOR_T + INNER_H;

// ============================================================

difference() {
    union() {

        // ── Outer tray shell ─────────────────────────────────
        hull()
            for (x = [CORNER_R, OW - CORNER_R])
                for (y = [CORNER_R, OH - CORNER_R])
                    translate([x, y, 0])
                        cylinder(r=CORNER_R, h=OZ);

        // ── Screw bosses (solid cylinders, holes cut below) ──
        for (b = BOSSES)
            translate([WALL + b[0], WALL + b[1], FLOOR_T])
                cylinder(d=BOSS_OD, h=BOSS_H);

        // ── XIAO controller platform ─────────────────────────
        translate([WALL + XIAO_X + XIAO_W/2,
                   WALL + XIAO_Y + XIAO_H/2,
                   FLOOR_T + XIAO_Z/2])
            hull()
                for (dx = [-XIAO_W/2+1.5, XIAO_W/2-1.5])
                    for (dy = [-XIAO_H/2+1.5, XIAO_H/2-1.5])
                        translate([dx, dy, 0])
                            cylinder(r=1.5, h=XIAO_Z, center=true);
    }

    // ── Interior pocket ──────────────────────────────────────
    translate([WALL, WALL, FLOOR_T])
        cube([PCB_W, PCB_H, INNER_H + 0.01]);

    // ── Boss screw holes ─────────────────────────────────────
    for (b = BOSSES)
        translate([WALL + b[0], WALL + b[1], -0.01])
            cylinder(d=BOSS_ID, h=OZ + 0.02);

    // ── USB-C slot through top wall ──────────────────────────
    translate([
        WALL + USBC_CX - USBC_W/2,
        OH - WALL - 0.01,
        USBC_Z
    ])
    // Rounded slot for clean look
    hull() {
        translate([1, 0, 1])
            rotate([90, 0, 0])
                cylinder(d=2, h=WALL+0.02);
        translate([USBC_W-1, 0, 1])
            rotate([90, 0, 0])
                cylinder(d=2, h=WALL+0.02);
        translate([1, 0, USBC_H-1])
            rotate([90, 0, 0])
                cylinder(d=2, h=WALL+0.02);
        translate([USBC_W-1, 0, USBC_H-1])
            rotate([90, 0, 0])
                cylinder(d=2, h=WALL+0.02);
    }

    // ── Rubber foot recesses (underside) ─────────────────────
    for (f = FEET)
        translate([WALL + f[0], WALL + f[1], 0])
            cylinder(d=FOOT_D, h=FOOT_DEPTH + 0.01);

    // ── Chamfer bottom outer edge (small, clean look) ────────
    translate([0, 0, -0.01])
    difference() {
        cube([OW + 0.1, OH + 0.1, 1.0]);
        translate([0.8, 0.8, -0.01])
            hull()
                for (x = [CORNER_R, OW - CORNER_R])
                    for (y = [CORNER_R, OH - CORNER_R])
                        translate([x - 0.8, y - 0.8, 0])
                            cylinder(r=CORNER_R - 0.8, h=1.2);
    }
}
