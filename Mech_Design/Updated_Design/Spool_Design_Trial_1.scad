// NEMA17 spool with 5mm bore and flange holes
$fn = 100;

bore_dia = 5;
drum_dia = 12;
flange_dia = 30;
drum_length = 20;
flange_thickness = 2;
flange_hole_dia = 1.5;

module spool() {
    difference() {
        union() {
            // Drum
            cylinder(d=drum_dia, h=drum_length);
            // Flange top
            cylinder(d=flange_dia, h=flange_thickness);
            // Flange bottom
            translate([0,0,drum_length])
                cylinder(d=flange_dia, h=flange_thickness);
        }
        // Bore through
        translate([0,0,-1])
            cylinder(d=bore_dia, h=drum_length + 2*flange_thickness + 2);
        // Flange holes (2 opposite)
        for (angle = [0,180]) {
            rotate([0,0,angle])
                translate([flange_dia/2 - 3,0,drum_length + flange_thickness/2])
                    rotate([90,0,0])
                        cylinder(d=flange_hole_dia, h=flange_dia);
        }
    }
}

// Call module
spool();
