// ============================================================
//  Zuup Micropad - Open-Top Tray FINAL (from KiCad data)
//  PCB: 92.869 (X) x 61.913 (Y) mm
//
//  Coordinate system:
//    X = long axis (left to right)
//    Y = short axis (front to back)
//    Z = up
//
//  Mounting holes (M2, 2.2mm) — from KiCad:
//    1. Top-left:     rel(2.381,  2.381)   ← unnamed footprint, corner
//    2. Bottom-left:  rel(2.381,  59.531)  ← unnamed footprint, corner
//    3. Bottom-right: rel(88.106, 57.150)  ← MountingHole_2.2mm_M2
//
//  Arduino Pro Micro center: rel(80.486, 19.050)
//  USB-C port: on TOP wall (min-Y face = front wall)
//              X center = 80.486mm from left edge of PCB
//              Port is ~3.1mm from top board edge (Pro Micro sits near top)
// ============================================================

// PCB
pcb_l = 92.869;
pcb_w = 61.913;
pcb_t = 1.6;

// Tray settings
tolerance   = 0.3;
wall        = 2.5;
floor_t     = 1.5;
standoff_h  = 3.0;
standoff_od = 5.5;
m2_d        = 2.4;

// Derived
inner_l = pcb_l + 2 * tolerance;
inner_w = pcb_w + 2 * tolerance;
outer_l = inner_l + 2 * wall;
outer_w = inner_w + 2 * wall;
wall_h  = floor_t + standoff_h + pcb_t + 0.5;

// Mounting hole positions (relative to PCB origin, converted to tray coords)
// tray coord = wall + tolerance + pcb_relative_coord
mh1_x = wall + tolerance + 2.381;   // top-left X
mh1_y = wall + tolerance + 2.381;   // top-left Y (min Y = front)

mh2_x = wall + tolerance + 2.381;   // bottom-left X
mh2_y = wall + tolerance + 59.531;  // bottom-left Y

mh3_x = wall + tolerance + 88.106;  // bottom-right X
mh3_y = wall + tolerance + 57.150;  // bottom-right Y

// USB-C hole on FRONT wall (min-Y face, Y=0 side)
// Pro Micro center X = 80.486mm from left PCB edge
// USB-C connector: 9mm wide, 3.5mm tall — use pill shape with clearance
usb_x  = wall + tolerance + 80.486; // X center of hole in tray coords
usb_z  = floor_t + standoff_h + pcb_t / 2; // vertically at PCB level
usb_c_w = 10.0;  // hole width (X)
usb_c_h = 4.5;   // hole height (Z)

// ============================================================
module standoff(x, y) {
    translate([x, y, floor_t])
    difference() {
        cylinder(h=standoff_h, d=standoff_od, $fn=36);
        cylinder(h=standoff_h + 1, d=m2_d, $fn=36);
    }
}

module tray() {
    difference() {
        // Outer box
        cube([outer_l, outer_w, wall_h]);

        // Inner cavity (open top)
        translate([wall, wall, floor_t])
            cube([inner_l, inner_w, wall_h + 1]);

        // USB-C pill hole through FRONT wall (min-Y face, drill along Y)
        translate([usb_x, -0.01, usb_z])
        hull() {
            translate([-(usb_c_w/2 - usb_c_h/2), 0, 0])
                rotate([-90, 0, 0])
                    cylinder(h=wall + 0.02, r=usb_c_h/2, $fn=32);
            translate([ (usb_c_w/2 - usb_c_h/2), 0, 0])
                rotate([-90, 0, 0])
                    cylinder(h=wall + 0.02, r=usb_c_h/2, $fn=32);
        }
    }

    // 3x Standoffs at exact KiCad mounting hole positions
    standoff(mh1_x, mh1_y);  // top-left
    standoff(mh2_x, mh2_y);  // bottom-left
    standoff(mh3_x, mh3_y);  // bottom-right
}

tray();

// ============================================================
// TUNING
// usb_x   — move USB hole left/right
// usb_z   — move USB hole up/down
// wall_h  — total tray height
// standoff_h — PCB height above floor
// tolerance  — PCB fit (0.3 = standard, 0.1 = tight)
// ============================================================
