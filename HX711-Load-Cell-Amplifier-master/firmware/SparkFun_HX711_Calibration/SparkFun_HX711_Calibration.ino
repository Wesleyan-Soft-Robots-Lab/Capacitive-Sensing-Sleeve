/*
  HX711 Calibration Sketch (Modified)
  Based on SparkFun + bogde HX711 library
  Features:
    - Connection check for HX711
    - Raw ADC value output
    - Tare before each reading (optional)
    - Real-time calibration factor tuning via Serial

  Author: Nathan Seidle + Modified by ChatGPT
  License: Beerware (and GPL via bogde's library)
*/

#include "HX711.h"

#define LOADCELL_DOUT_PIN  3
#define LOADCELL_SCK_PIN   2

HX711 scale;

float calibration_factor = -200;  // Start value for 10kg load cell

void setup() {
  Serial.begin(9600);
  Serial.println("HX711 calibration sketch");

  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);

  if (!scale.is_ready()) {
    Serial.println("ERROR: HX711 not found. Check wiring.");
    while (1); // Stop here
  }

  Serial.println("HX711 connected successfully.");
  Serial.println("Remove all weight from scale...");
  delay(2000);

  scale.set_scale(); // No calibration yet
  scale.tare();      // Zero the scale

  long zero_factor = scale.read_average();
  Serial.print("Zero factor (no weight): ");
  Serial.println(zero_factor);
}

void loop() {
  scale.set_scale(calibration_factor);

  // Optional: tare before every reading (can be disabled)
  // scale.tare();

  long raw = scale.read_average();
  float weight = scale.get_units();

  Serial.print("Raw ADC: ");
  Serial.print(raw);
  Serial.print(" | Reading: ");
  Serial.print(weight, 2);
  Serial.print(" kg");
  Serial.print(" | Calibration factor: ");
  Serial.println(calibration_factor);

  // Serial input to adjust calibration factor
  if (Serial.available()) {
    char input = Serial.read();
    if (input == '+' || input == 'a')
      calibration_factor += 10;
    else if (input == '-' || input == 'z')
      calibration_factor -= 10;
  }

  delay(500);
}
