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
const int movementStepsPerRevolution = 400;  // Movement motor steps per revolution
const int groutStepsPerRevolution = 800;     // Grout stepper motor steps per revolution
const float wheelDiameter = 12.0;            // Diameter of the wheel in cm
const float wheelBase = 40.0;                // Distance between the wheels in cm

// Variables for motor control
Servo myServo;        // Servo for controlling the bottle neck
String command = "";  // To store incoming commands

bool isGroutMotorRunning = false;  // Flag to track if the grout stepper motor is running

void setup() {
  // Initialize movement motor pins
  pinMode(ENA_PIN1, OUTPUT);
  pinMode(STEP_PIN1, OUTPUT);
  pinMode(DIR_PIN1, OUTPUT);
  pinMode(ENA_PIN2, OUTPUT);
  pinMode(STEP_PIN2, OUTPUT);
  pinMode(DIR_PIN2, OUTPUT);

  // Initialize grout motor pins
  pinMode(ENA, OUTPUT);
  pinMode(DIR, OUTPUT);
  pinMode(PUL, OUTPUT);

  // Enable all motors
  digitalWrite(ENA_PIN1, LOW);  // Enable movement motor 1
  digitalWrite(ENA_PIN2, LOW);  // Enable movement motor 2
  digitalWrite(ENA, LOW);       // Enable grout stepper motor

  // Servo setup
  myServo.attach(9);  // Attach servo motor to pin 9
  myServo.write(0);   // Close the bottle neck by default (0 degrees)

  // Start serial communication
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    command = Serial.readStringUntil('\n');  // Read command from Raspberry Pi
    command.trim();                          // Remove any trailing or leading whitespace
    Serial.println(command);
    // Parse the command and execute actions
    if (command.startsWith("MOVE_FORWARD")) {
      float distance = command.substring(13).toFloat();
      // applyGrout();
      moveForward(distance);
    } else if (command.startsWith("MOVE_BACKWARD")) {
      float distance = command.substring(14).toFloat();
      moveBackward(distance);
    } else if (command.startsWith("ROTATE_RIGHT")) {
      float angle = command.substring(13).toFloat();
      rotateRight(angle);
    } else if (command.startsWith("ROTATE_LEFT")) {
      float angle = command.substring(12).toFloat();
      rotateLeft(angle);
    } else if (command == "STOP") {
      stopMotors();
    } else if (command == "APPLY") {
      applyGrout();
    } else if (command == "EMPTY") {
      emptyGrout();
    } else if (command.startsWith("MOVE_FRONT")) {
      float distance = command.substring(11).toFloat();
      moveForwardWithoutGrout(distance);
    }

    Serial.println("DONE");
  }

  // Continuously run the grout stepper motor until a STOP command is received
  if (isGroutMotorRunning) {
    digitalWrite(PUL, HIGH);
    delayMicroseconds(500);  // Adjust pulse width for speed
    digitalWrite(PUL, LOW);
    delayMicroseconds(500);
  }
}

// Function to move the robot forward by a specific distance (in cm)
void moveForward(float distance_cm) {
  int steps = calculateMovementSteps(distance_cm);
  digitalWrite(DIR_PIN1, LOW);   // Motor 1 forward
  digitalWrite(DIR_PIN2, HIGH);  // Motor 2 forward

  myServo.write(90);        // Open the bottle neck
  digitalWrite(ENA, LOW);   // Enable grout stepper motor
  digitalWrite(DIR, HIGH);  // Set direction to forward


  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN1, HIGH);
    digitalWrite(STEP_PIN2, HIGH);
    digitalWrite(PUL, HIGH);

    delayMicroseconds(3000);
    digitalWrite(STEP_PIN1, LOW);
    digitalWrite(STEP_PIN2, LOW);
    digitalWrite(PUL, LOW);
    delayMicroseconds(3000);
  }

  digitalWrite(ENA, HIGH);
  isGroutMotorRunning = true;  // Flag to indicate motor is running
}

void moveForwardWithoutGrout(float distance_cm) {
  int steps = calculateMovementSteps(distance_cm);
  digitalWrite(DIR_PIN1, LOW);   // Motor 1 forward
  digitalWrite(DIR_PIN2, HIGH);  // Motor 2 forward

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN1, HIGH);
    digitalWrite(STEP_PIN2, HIGH);
    delayMicroseconds(3000);

    digitalWrite(STEP_PIN1, LOW);
    digitalWrite(STEP_PIN2, LOW);
    delayMicroseconds(3000);
  }
}

// Function to move the robot backward by a specific distance (in cm)
void moveBackward(float distance_cm) {
  int steps = calculateMovementSteps(distance_cm);
  digitalWrite(DIR_PIN1, HIGH);  // Motor 1 backward
  digitalWrite(DIR_PIN2, LOW);   // Motor 2 backward

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN1, HIGH);
    digitalWrite(STEP_PIN2, HIGH);
    delayMicroseconds(3000);
    digitalWrite(STEP_PIN1, LOW);
    digitalWrite(STEP_PIN2, LOW);
    delayMicroseconds(3000);
  }
}

// Function to rotate the robot right by a specific angle (in degrees)
void rotateRight(float angle_deg) {
  float arcLength = (wheelBase * PI * angle_deg) / 360.0;
  int steps = calculateMovementSteps(arcLength);

  digitalWrite(DIR_PIN1, LOW);  // Motor 1 forward
  digitalWrite(DIR_PIN2, LOW);  // Motor 2 backward

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN1, HIGH);
    digitalWrite(STEP_PIN2, HIGH);
    delayMicroseconds(3000);
    digitalWrite(STEP_PIN1, LOW);
    digitalWrite(STEP_PIN2, LOW);
    delayMicroseconds(3000);
  }
}

// Function to rotate the robot left by a specific angle (in degrees)
void rotateLeft(float angle_deg) {
  float arcLength = (wheelBase * PI * angle_deg) / 360.0;
  int steps = calculateMovementSteps(arcLength);

  digitalWrite(DIR_PIN1, HIGH);  // Motor 1 backward
  digitalWrite(DIR_PIN2, HIGH);  // Motor 2 forward

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN1, HIGH);
    digitalWrite(STEP_PIN2, HIGH);
    delayMicroseconds(3000);
    digitalWrite(STEP_PIN1, LOW);
    digitalWrite(STEP_PIN2, LOW);
    delayMicroseconds(3000);
  }
}

// Function to stop both motors
void stopMotors() {
  digitalWrite(STEP_PIN1, LOW);
  digitalWrite(STEP_PIN2, LOW);
  digitalWrite(PUL, LOW);       // Stop grout stepper motor
  isGroutMotorRunning = false;  // Stop the grout motor from running
  myServo.write(0);             // Close the bottle neck
}

// Function to apply grout using the stepper and servo motor
void applyGrout() {
  myServo.write(90);        // Open the bottle neck
  digitalWrite(ENA, LOW);   // Enable grout stepper motor
  digitalWrite(DIR, HIGH);  // Set direction to forward

  for (int i = 0; i < groutStepsPerRevolution; i++) {
    digitalWrite(PUL, HIGH);
    delayMicroseconds(500);  // Adjust pulse width for speed
    digitalWrite(PUL, LOW);
    delayMicroseconds(500);
  }
  isGroutMotorRunning = true;  // Flag to indicate motor is running
}

// Function to empty grout using the stepper and servo motor
void emptyGrout() {
  myServo.write(0);        // Close the bottle neck
  digitalWrite(ENA, LOW);  // Enable grout stepper motor
  digitalWrite(DIR, LOW);  // Set direction to backward

  for (int i = 0; i < groutStepsPerRevolution; i++) {
    digitalWrite(PUL, HIGH);
    delayMicroseconds(500);  // Adjust pulse width for speed
    digitalWrite(PUL, LOW);
    delayMicroseconds(500);
  }
  isGroutMotorRunning = true;  // Flag to indicate motor is running
}


// Function to calculate the number of steps for a given distance (in cm)
int calculateMovementSteps(float distance_cm) {
  const int STEPS_PER_REV = 800;                             // Steps per revolution (with microstepping)
  const float WHEEL_DIAMETER_CM = 12.0;                      // Diameter of the wheel in cm
  const float WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER_CM * PI;  // Circumference of the wheel

  // Calculate steps per cm based on wheel circumference
  const float STEPS_PER_CM = STEPS_PER_REV / WHEEL_CIRCUMFERENCE;

  // Calculate the total number of steps for the given distance
  return distance_cm * STEPS_PER_CM * 100 / 53;
}
