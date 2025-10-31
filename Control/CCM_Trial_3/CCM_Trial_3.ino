#include <AccelStepper.h>

// ===== Pins (Due -> CNC Shield signal rail) =====
// X axis (already working)
const int X_STEP = 2;   // D2  -> X.STEP
const int X_DIR  = 5;   // D5  -> X.DIR
// Y axis (new)
const int Y_STEP = 3;   // D3  -> Y.STEP
const int Y_DIR  = 6;   // D6  -> Y.DIR
// Global enable for all drivers on the shield
const int PIN_EN = 8;   // D8  -> EN (active LOW)

// ===== Microstepping & motor =====
// Set to match the jumpers under EACH driver. (If both full-step, set to 1)
const int MICROSTEP = 1;
const int STEPS_PER_REV = 200 * MICROSTEP;   // 1.8° motor

// ===== Geometry (mm) — same for both axes unless changed =====
const float R_CABLE_MM = 4.25;               // channel radius from centre
const float R_SPOOL_MM = 6.0;                // spool radius (12 mm dia)
const float CIRC_MM    = 2.0 * 3.1415926535 * R_SPOOL_MM;

// ===== Motion tuning (shared) =====
float maxSpeed = 80.0f;                      // steps/s (tame start)
float accel    = 160.0f;                     // steps/s^2

// Per-axis calibration scale (1.0 = theoretical)
// If measured bend > commanded, set CAL < 1.0 (e.g., 0.19 earlier)
float CALX = 1.0f;
float CALY = 1.0f;

// State
AccelStepper stepperX(AccelStepper::DRIVER, X_STEP, X_DIR);
AccelStepper stepperY(AccelStepper::DRIVER, Y_STEP, Y_DIR);

long zeroX = 0, zeroY = 0;
float targetDegX = 0.0f, targetDegY = 0.0f;

long angleDegToSteps(float deg, bool axisIsX) {
  float psi = deg * 3.1415926535f / 180.0f;     // rad
  float dLmm = psi * R_CABLE_MM;                // mm
  float turns = dLmm / CIRC_MM;
  float cal = axisIsX ? CALX : CALY;
  long steps = lroundf(turns * (float)STEPS_PER_REV * cal);
  return (axisIsX ? zeroX : zeroY) + steps;
}

// ------------ Command handling ------------
void handleSerialLine(String line) {
  line.trim(); if (!line.length()) return;
  line.toUpperCase();
  int sp = line.indexOf(' ');
  String cmd = (sp==-1) ? line : line.substring(0,sp);
  String arg = (sp==-1) ? ""   : line.substring(sp+1); arg.trim();

  // --- Global ---
  if (cmd == "E") { digitalWrite(PIN_EN, HIGH); Serial.println(F("Driver disabled (EN=HIGH).")); return; }
  if (cmd == "N") { digitalWrite(PIN_EN, LOW);  Serial.println(F("Driver enabled (EN=LOW)."));  return; }
  if (cmd == "SPD"){ float v = arg.toFloat(); if(v>0){ maxSpeed=v; stepperX.setMaxSpeed(v); stepperY.setMaxSpeed(v);} Serial.print(F("Max speed = ")); Serial.println(maxSpeed); return; }
  if (cmd == "ACC"){ float a = arg.toFloat(); if(a>0){ accel=a; stepperX.setAcceleration(a); stepperY.setAcceleration(a);} Serial.print(F("Acceleration = ")); Serial.println(accel); return; }
  if (cmd == "CALX"){ float s=arg.toFloat(); if(s>0){ CALX=s; } Serial.print(F("CALX=")); Serial.println(CALX,4); return; }
  if (cmd == "CALY"){ float s=arg.toFloat(); if(s>0){ CALY=s; } Serial.print(F("CALY=")); Serial.println(CALY,4); return; }

  // --- Zeroing ---
  if (cmd == "Z")   { zeroX = stepperX.currentPosition(); zeroY = stepperY.currentPosition(); targetDegX=0; targetDegY=0; Serial.println(F("Zero set (X,Y).")); return; }
  if (cmd == "ZX")  { zeroX = stepperX.currentPosition(); targetDegX=0; Serial.println(F("Zero X set.")); return; }
  if (cmd == "ZY")  { zeroY = stepperY.currentPosition(); targetDegY=0; Serial.println(F("Zero Y set.")); return; }

  // --- X axis (legacy + specific) ---
  if (cmd == "A")   { float d=arg.toFloat(); targetDegX=d; stepperX.moveTo(angleDegToSteps(targetDegX,true)); Serial.print(F("AX -> ")); Serial.print(targetDegX); Serial.print(F(" deg, steps=")); Serial.println(angleDegToSteps(targetDegX,true)); return; }
  if (cmd == "J") {  String a=arg; a.replace(" ",""); float delta=(a.length()? a.toFloat():5.0f); targetDegX+=delta; stepperX.moveTo(angleDegToSteps(targetDegX,true));
                     Serial.print(F("JX by ")); Serial.print(delta); Serial.print(F(" -> ")); Serial.println(targetDegX); return; }
  if (cmd == "R")   { targetDegX=0; stepperX.moveTo(angleDegToSteps(0,true)); Serial.println(F("Return X to zero.")); return; }
  if (cmd == "REV") { float t=arg.toFloat(); long s=lroundf(t*(float)STEPS_PER_REV); stepperX.moveTo(stepperX.currentPosition()+s);
                     Serial.print(F("REV X ")); Serial.print(t); Serial.print(F(" -> ")); Serial.println(s); return; }

  // --- Y axis (new) ---
  if (cmd == "AY")  { float d=arg.toFloat(); targetDegY=d; stepperY.moveTo(angleDegToSteps(targetDegY,false)); Serial.print(F("AY -> ")); Serial.print(targetDegY); Serial.print(F(" deg, steps=")); Serial.println(angleDegToSteps(targetDegY,false)); return; }
  if (cmd == "JY")  { String a=arg; a.replace(" ",""); float delta=(a.length()? a.toFloat():5.0f); targetDegY+=delta; stepperY.moveTo(angleDegToSteps(targetDegY,false));
                     Serial.print(F("JY by ")); Serial.print(delta); Serial.print(F(" -> ")); Serial.println(targetDegY); return; }
  if (cmd == "RY")  { targetDegY=0; stepperY.moveTo(angleDegToSteps(0,false)); Serial.println(F("Return Y to zero.")); return; }
  if (cmd == "REVY"){ float t=arg.toFloat(); long s=lroundf(t*(float)STEPS_PER_REV); stepperY.moveTo(stepperY.currentPosition()+s);
                     Serial.print(F("REV Y ")); Serial.print(t); Serial.print(F(" -> ")); Serial.println(s); return; }

  // --- Simple demo for X only (kept) ---
  if (cmd == "H") {
    Serial.println(F("Demo X: 10° back-and-forth x3"));
    const int cycles=3; const float move_deg=10.0f;
    long ts0=angleDegToSteps(0.0f,true), ts1=angleDegToSteps(move_deg,true);
    for(int i=0;i<cycles;i++){ stepperX.moveTo(ts1); while(stepperX.distanceToGo()) stepperX.run(); delay(500);
                               stepperX.moveTo(ts0); while(stepperX.distanceToGo()) stepperX.run(); delay(500); }
    Serial.println(F("Demo complete."));
    return;
  }

  Serial.print(F("Unknown cmd: ")); Serial.println(cmd);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_EN, OUTPUT);
  digitalWrite(PIN_EN, LOW); // enable drivers

  stepperX.setMaxSpeed(maxSpeed); stepperX.setAcceleration(accel);
  stepperY.setMaxSpeed(maxSpeed); stepperY.setAcceleration(accel);

  stepperX.setCurrentPosition(0); stepperY.setCurrentPosition(0);

  Serial.println(F("CCM Controller: X & Y online"));
  Serial.println(F("X: A <deg>, J <±deg>, R, REV <turns>, ZX, CALX <s>"));
  Serial.println(F("Y: AY <deg>, JY <±deg>, RY, REVY <turns>, ZY, CALY <s>"));
  Serial.println(F("Globals: Z, E/N, SPD <steps/s>, ACC <steps/s^2>, H (X demo)"));
}

void loop() {
  // line-based parser
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    handleSerialLine(line);
  }
  stepperX.run();
  stepperY.run();
}
