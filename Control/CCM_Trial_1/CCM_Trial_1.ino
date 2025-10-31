#include <AccelStepper.h>

// ===== Pins (Due -> CNC Shield signal rail) =====
const int PIN_STEP = 2;   // D2  -> X.STEP
const int PIN_DIR  = 5;   // D5  -> X.DIR
const int PIN_EN   = 8;   // D8  -> EN (active LOW)

// ===== Microstepping & motor =====
// Set this to your jumper setting (1,2,4,8,16,32...)
const int MICROSTEP = 16;
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

void loop() {
  // ---- Serial command parser ----
  if (Serial.available()) {
    char c = Serial.read();

    if (c == 'Z' || c == 'z') {
      zero_steps = stepper.currentPosition();
      target_deg = 0.0f;
      Serial.println(F("Zero set at current position."));
    }
    else if (c == 'A' || c == 'a') {
      float deg = Serial.parseFloat();
      target_deg = deg;
      stepper.moveTo(angleDegToSteps(target_deg));
      Serial.print(F("Target angle -> ")); Serial.print(target_deg); Serial.println(F(" deg"));
    }
    else if (c == 'J' || c == 'j') {
  // Read rest of the line, trim spaces
  String rest = Serial.readStringUntil('\n');
  rest.trim();                   // e.g., "+", "-5", "+ 2.5"
  // Remove any internal spaces
  rest.replace(" ", "");

  float delta = 0.0f;
  if (rest.length() == 0) {
    // default jog if no sign/number provided
    delta = JOG_DEG;
  } else {
    char sign = rest.charAt(0);
    if (sign == '+') {
      if (rest.length() > 1) delta = rest.substring(1).toFloat();
      else delta = JOG_DEG;
    } else if (sign == '-') {
      if (rest.length() > 1) delta = -rest.substring(1).toFloat();
      else delta = -JOG_DEG;
    } else {
      // If user typed a number without sign, treat as +number
      delta = rest.toFloat();
      if (delta == 0) delta = JOG_DEG; // fallback
    }
  }

  target_deg += delta;
  long ts = angleDegToSteps(target_deg);
  stepper.moveTo(ts);
  Serial.print(F("Jog by ")); Serial.print(delta);
  Serial.print(F(" deg -> target ")); Serial.print(target_deg);
  Serial.print(F(" deg, targetSteps=")); Serial.println(ts);
}

    else if (c == 'S' || c == 's') {
      // allow "SPD <value>"
      String rest = Serial.readStringUntil('\n');
      rest.trim();
      if (rest.startsWith("PD")) {
        float spd = rest.substring(2).toFloat();
        if (spd > 0) {
          maxSpeed = spd;
          stepper.setMaxSpeed(maxSpeed);
          Serial.print(F("Max speed = ")); Serial.print(maxSpeed); Serial.println(F(" steps/s"));
        }
      }
    }
   // --- put this BEFORE the single-letter R/E handlers ---
else if (c == 'R' || c == 'r') {
  // Peek ahead to see if user typed REV...
  while (Serial.available() && isspace(Serial.peek())) Serial.read();
  if (Serial.peek() == 'E' || Serial.peek() == 'e') {
    Serial.read(); // eat 'E'
    if (Serial.available()) {
      char v = Serial.read(); // should be 'V' or 'v'
      if (v == 'V' || v == 'v') {
        // parse turns after optional spaces
        String rest = Serial.readStringUntil('\n');
        rest.trim();
        float turns = rest.toFloat();
        long steps = lroundf(turns * (float)STEPS_PER_REV);
        stepper.moveTo(stepper.currentPosition() + steps);
        Serial.print(F("Revolve: ")); Serial.print(turns);
        Serial.print(F(" turns -> ")); Serial.print(steps);
        Serial.println(F(" steps"));
      }
    }
  } else {
    // Plain 'R' = return to zero
    target_deg = 0.0f;
    long ts = angleDegToSteps(0.0f);
    stepper.moveTo(ts);
    Serial.print(F("Return-to-zero: targetSteps=")); Serial.println(ts);
  }
}
else if (c == 'E' || c == 'e') {
  // disable driver
  digitalWrite(PIN_EN, HIGH); // DRV8825: HIGH = disable
  Serial.println(F("Driver disabled (EN=HIGH)."));
}
else if (c == 'N' || c == 'n') {
  // enable driver
  digitalWrite(PIN_EN, LOW);  // DRV8825: LOW = enable
  Serial.println(F("Driver enabled (EN=LOW)."));
}

else if (c == 'A' || c == 'a') { // <-- replace your existing A handler with this:
  float deg = Serial.parseFloat();
  target_deg = deg;
  long ts = angleDegToSteps(target_deg);
  stepper.moveTo(ts);
  Serial.print(F("A cmd: deg=")); Serial.print(target_deg);
  Serial.print(F(", currentPos=")); Serial.print(stepper.currentPosition());
  Serial.print(F(", targetSteps=")); Serial.println(ts);
}

else if (c == 'H' || c == 'h') {
  Serial.println(F("Running 10° back-and-forth demo..."));
  
  float start_deg = target_deg;   // remember where we started
  int cycles = 3;                  // number of back-and-forths
  float move_deg = -10.0;           // bend amount
  
  for (int i = 0; i < cycles; i++) {
    // Move to +10° from zero
    long ts1 = angleDegToSteps(move_deg);
    stepper.moveTo(ts1);
    while (stepper.distanceToGo() != 0) stepper.run();
    delay(500); // pause at bend
    
    // Move back to zero
    long ts0 = angleDegToSteps(0.0);
    stepper.moveTo(ts0);
    while (stepper.distanceToGo() != 0) stepper.run();
    delay(500); // pause at straight
  }
  
  // Return to original position if not zero
  long ts_start = angleDegToSteps(start_deg);
  stepper.moveTo(ts_start);
  while (stepper.distanceToGo() != 0) stepper.run();
  
  Serial.println(F("Demo complete."));
}

    // clear remainder of line
    while (Serial.available()) Serial.read();
  }

  // ---- Run motor toward target ----
  stepper.run();
}
