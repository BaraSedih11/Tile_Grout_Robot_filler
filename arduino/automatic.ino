#include <Servo.h>  // Include the Servo library

// IR sensor pins
#define IR_SENSOR_LEFT_PIN 6   // Left IR sensor
#define IR_SENSOR_RIGHT_PIN 7  // Right IR sensor

// Movement motor control pins
#define ENA_PIN1 2
#define STEP_PIN1 3
#define DIR_PIN1 4
#define ENA_PIN2 11
#define STEP_PIN2 12
#define DIR_PIN2 13

// Grout stepper motor control pins
#define ENA A0  // Enable pin for grout stepper
#define DIR A1  // Direction pin for grout stepper
#define PUL A2  // Pulse pin for grout stepper

// Constants for movement and grout steppers
const int movementStepsPerRevolution = 800;  // Movement motor steps per revolution
const int groutStepsPerRevolution = 200;     // Grout stepper motor steps per revolution
const float wheelDiameter = 12.0;            // Diameter of the wheel in cm
const float wheelBase = 40.0;                // Distance between the wheels in cm

Servo myServo; // Servo for controlling the bottle neck

void setup() {
  // Movement motor setup
  pinMode(ENA_PIN1, OUTPUT);
  pinMode(STEP_PIN1, OUTPUT);
  pinMode(DIR_PIN1, OUTPUT);
  pinMode(ENA_PIN2, OUTPUT);
  pinMode(STEP_PIN2, OUTPUT);
  pinMode(DIR_PIN2, OUTPUT);

  // Grout motor setup
  pinMode(ENA, OUTPUT);
  pinMode(DIR, OUTPUT);
  pinMode(PUL, OUTPUT);
  
  // IR sensors setup
  pinMode(IR_SENSOR_LEFT_PIN, INPUT);
  pinMode(IR_SENSOR_RIGHT_PIN, INPUT);

  // Enable all motors
  digitalWrite(ENA_PIN1, LOW);  // Enable movement motor 1
  digitalWrite(ENA_PIN2, LOW);  // Enable movement motor 2
  digitalWrite(ENA, LOW);       // Enable grout stepper motor

  // Servo setup
  myServo.attach(9);            // Attach servo motor to pin 9
  myServo.write(0);             // Close the bottle neck by default (0 degrees)

  // Start serial communication
  Serial.begin(9600);
  Serial.println("Line follower with grout system ready...");
}

void loop() {
  int irLeftState = digitalRead(IR_SENSOR_RIGHT_PIN);  // Read the left IR sensor
  int irRightState = digitalRead(IR_SENSOR_LEFT_PIN);  // Read the right IR sensor

  Serial.print("Right Sensor: ");
  Serial.print(irLeftState);
  Serial.print(" | Left Sensor: ");
  Serial.println(irRightState);
  // applyGrout();    // Apply grout when moving forward
  // emptyGrout();
  if (irLeftState == LOW && irRightState == LOW) {
    moveForward(3);  // Move 3 cm forward
  } else if (irLeftState == LOW && irRightState == HIGH) {
    turnRight(1);    // Turn right
  } else if (irLeftState == HIGH && irRightState == LOW) {
    turnLeft(1);     // Turn left
  } else if (irLeftState == HIGH && irRightState == HIGH) {
    moveForward(3);  // Move forward on detecting black line
  } else {
    stopMotors();
  }

  delay(250);  // Small delay for stability
}

// Function to move the robot forward by a specific distance (in cm)
void moveForward(float distance_cm) {
  int steps = calculateMovementSteps(distance_cm);
  digitalWrite(DIR_PIN1, LOW);   // Motor 1 forward
  digitalWrite(DIR_PIN2, HIGH);  // Motor 2 forward
  digitalWrite(DIR, HIGH);  // Set direction to forward

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN1, HIGH);
    digitalWrite(STEP_PIN2, HIGH);
    digitalWrite(PUL, HIGH);// for grout

    delayMicroseconds(3000);
    digitalWrite(STEP_PIN1, LOW);
    digitalWrite(STEP_PIN2, LOW);
    digitalWrite(PUL, LOW);
    delayMicroseconds(3000);
  }
}

void moveBackward(float distance_cm) {
  int steps = calculateMovementSteps(distance_cm);
  digitalWrite(DIR_PIN1, HIGH);   // Motor 1 forward
  digitalWrite(DIR_PIN2, LOW);  // Motor 2 forward

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN1, LOW);
    digitalWrite(STEP_PIN2, LOW);

    delayMicroseconds(3000);
    digitalWrite(STEP_PIN1, HIGH);
    digitalWrite(STEP_PIN2, HIGH);
    delayMicroseconds(3000);
  }
}

// Function to apply grout using the stepper and servo motor
void applyGrout() {
  myServo.write(90);  // Open the bottle neck

  // Move grout stepper forward
  for (int i = 0; i < groutStepsPerRevolution; i++) {
    digitalWrite(DIR, HIGH);  // Set direction to forward
    digitalWrite(PUL, HIGH);
    delayMicroseconds(500);   // Adjust pulse width for speed
    digitalWrite(PUL, LOW);
    delayMicroseconds(500);
  }
}

void emptyGrout() {
  myServo.write(0);  // Open the bottle neck

  // Move grout stepper forward
  for (int i = 0; i < groutStepsPerRevolution; i++) {
    digitalWrite(DIR, LOW);  // Set direction to forward
    digitalWrite(PUL, LOW);
    delayMicroseconds(500);   // Adjust pulse width for speed
    digitalWrite(PUL, HIGH);
    delayMicroseconds(500);
  }
}

// Function to rotate the robot left by a specific angle (in degrees)
void turnLeft(float angle_deg) {
  float arcLength = (wheelBase * PI * angle_deg) / 360.0;
  int steps = calculateMovementSteps(arcLength);

  digitalWrite(DIR_PIN1, HIGH);  // Motor 1 backward
  digitalWrite(DIR_PIN2, HIGH);  // Motor 2 forward

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN1, HIGH);
    digitalWrite(STEP_PIN2, HIGH);
    delayMicroseconds(1500);
    digitalWrite(STEP_PIN1, LOW);
    digitalWrite(STEP_PIN2, LOW);
    delayMicroseconds(1500);
  }
}

// Function to rotate the robot right by a specific angle (in degrees)
void turnRight(float angle_deg) {
  float arcLength = (wheelBase * PI * angle_deg) / 360.0;
  int steps = calculateMovementSteps(arcLength);

  digitalWrite(DIR_PIN1, LOW);  // Motor 1 forward
  digitalWrite(DIR_PIN2, LOW);  // Motor 2 backward

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN1, HIGH);
    digitalWrite(STEP_PIN2, HIGH);
    delayMicroseconds(1500);
    digitalWrite(STEP_PIN1, LOW);
    digitalWrite(STEP_PIN2, LOW);
    delayMicroseconds(1500);
  }
}

// Function to stop all motors
void stopMotors() {
  digitalWrite(STEP_PIN1, LOW);
  digitalWrite(STEP_PIN2, LOW);
  digitalWrite(PUL, LOW);  // Stop grout stepper motor
  myServo.write(0);  // Close servo
}

// Function to calculate movement steps for a given distance (in cm)
int calculateMovementSteps(float distance_cm) {
  float stepsPerCm = movementStepsPerRevolution / (PI * wheelDiameter);
  return distance_cm * stepsPerCm;
}
