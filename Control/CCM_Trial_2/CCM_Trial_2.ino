#include <AccelStepper.h>

// ===== Pins (Due -> CNC Shield signal rail) =====
const int PIN_STEP = 2;   // D2  -> X.STEP
const int PIN_DIR  = 5;   // D5  -> X.DIR
const int PIN_EN   = 8;   // D8  -> EN (active LOW)

// ===== Microstepping & motor =====
// Set this to your jumper setting (1,2,4,8,16,32...)
const int MICROSTEP = 1;
const int STEPS_PER_REV = 200 * MICROSTEP;   // 1.8° motor

// ===== Geometry (mm) =====
const float R_CABLE_MM = 4.25;               // channel radius from centre
const float R_SPOOL_MM = 6.0;                // spool radius (12 mm dia)
const float CIRC_MM    = 2.0 * 3.1415926535 * R_SPOOL_MM;

// ===== Motion tuning =====
float maxSpeed = 2000.0f;                    // steps/s
const float ACCEL = 2000.0f;                 // steps/s^2
const float JOG_DEG = 5.0f;                  // jog increment

AccelStepper stepper(AccelStepper::DRIVER, PIN_STEP, PIN_DIR);

long zero_steps = 0;     // step offset when you press 'Z'
float target_deg = 0.0;

long angleDegToSteps(float deg) {
  // psi (rad) = deg * pi/180
  float psi = deg * 3.1415926535f / 180.0f;
  // ΔL (mm) = psi * r_cable
  float dLmm = psi * R_CABLE_MM;
  // turns = ΔL / circumference
  float turns = dLmm / CIRC_MM;
  // steps = turns * steps/rev
  long steps = lroundf(turns * (float)STEPS_PER_REV);
  return zero_steps + steps;
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_EN, OUTPUT);
  digitalWrite(PIN_EN, LOW); // LOW = enable (DRV8825)

  stepper.setMaxSpeed(maxSpeed);
  stepper.setAcceleration(ACCEL);
  stepper.setCurrentPosition(0);

  Serial.println(F("CCM 1-DoF Controller (Due + CNC Shield X)"));
  Serial.println(F("Commands:"));
  Serial.println(F("  Z              -> zero here (after pre-tension)"));
  Serial.println(F("  A <deg>        -> go to bend angle (e.g. A 30)"));
  Serial.println(F("  J + / J -      -> jog +5 / -5 deg"));
  Serial.println(F("  SPD <steps/s>  -> set max speed (e.g. SPD 1200)"));
  Serial.println();
}

void handleSerialLine(String line) {
  line.trim();
  if (line.length() == 0) return;

  // Uppercase for easy matching
  line.toUpperCase();

  // Split into tokens
  int sp = line.indexOf(' ');
  String cmd = (sp == -1) ? line : line.substring(0, sp);
  String arg = (sp == -1) ? ""   : line.substring(sp + 1);
  arg.trim();

  if (cmd == "Z") {
    zero_steps = stepper.currentPosition();
    target_deg = 0.0f;
    Serial.println(F("Zero set."));
  }
  else if (cmd == "A") {                 // A <deg>
    float deg = arg.toFloat();
    target_deg = deg;
    long ts = angleDegToSteps(target_deg);
    stepper.moveTo(ts);
    Serial.print(F("A -> ")); Serial.print(target_deg);
    Serial.print(F(" deg, steps=")); Serial.println(ts);
  }
  else if (cmd == "J") {                 // J [+/-deg] (e.g., "J +", "J -2.5", "J 3")
    String a = arg; a.replace(" ", "");
    float delta = 0.0f;
    if (a.length() == 0) delta = JOG_DEG;
    else {
      char sgn = a.charAt(0);
      if (sgn == '+' || sgn == '-') delta = a.toFloat();
      else                           delta = a.toFloat(); // treat as +number
      if (delta == 0) delta = JOG_DEG;
    }
    target_deg += delta;
    long ts = angleDegToSteps(target_deg);
    stepper.moveTo(ts);
    Serial.print(F("Jog by ")); Serial.print(delta);
    Serial.print(F(" -> target ")); Serial.print(target_deg);
    Serial.print(F(" deg, steps=")); Serial.println(ts);
  }
  else if (cmd == "R") {                 // Return to zero
    target_deg = 0.0f;
    long ts = angleDegToSteps(0.0f);
    stepper.moveTo(ts);
    Serial.print(F("Return-to-zero: steps=")); Serial.println(ts);
  }
  else if (cmd == "REV") {               // REV <turns>
    float turns = arg.toFloat();
    long steps = lroundf(turns * (float)STEPS_PER_REV);
    stepper.moveTo(stepper.currentPosition() + steps);
    Serial.print(F("Revolve ")); Serial.print(turns);
    Serial.print(F(" turns -> ")); Serial.print(steps); Serial.println(F(" steps"));
  }
  else if (cmd == "SPD") {               // SPD <steps/s>
    float spd = arg.toFloat();
    if (spd > 0) { maxSpeed = spd; stepper.setMaxSpeed(maxSpeed); }
    Serial.print(F("Max speed = ")); Serial.println(maxSpeed);
  }
  else if (cmd == "ACC") {               // ACC <steps/s^2>
    float a = arg.toFloat();
    if (a > 0) { stepper.setAcceleration(a); }
    Serial.print(F("Acceleration = ")); Serial.println(a);
  }
  else if (cmd == "E") {                 // Disable driver
    digitalWrite(PIN_EN, HIGH);          // DRV8825: HIGH = disable
    Serial.println(F("Driver disabled (EN=HIGH)."));
  }
  else if (cmd == "N") {                 // Enable driver
    digitalWrite(PIN_EN, LOW);           // DRV8825: LOW = enable
    Serial.println(F("Driver enabled (EN=LOW)."));
  }
  else if (cmd == "H") {                 // demo: 10° back & forth 3x
    Serial.println(F("Demo: 10° back-and-forth x3"));
    const int cycles = 3;
    const float move_deg = 10.0f;
    long ts0 = angleDegToSteps(0.0f);
    long ts1 = angleDegToSteps(move_deg);
    for (int i = 0; i < cycles; i++) {
      stepper.moveTo(ts1); while (stepper.distanceToGo()) stepper.run(); delay(500);
      stepper.moveTo(ts0); while (stepper.distanceToGo()) stepper.run(); delay(500);
    }
    Serial.println(F("Demo complete."));
  }
  else {
    Serial.print(F("Unknown cmd: ")); Serial.println(cmd);
  }
}

void loop() {
  // read full line
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    handleSerialLine(line);
  }
  stepper.run();
}
