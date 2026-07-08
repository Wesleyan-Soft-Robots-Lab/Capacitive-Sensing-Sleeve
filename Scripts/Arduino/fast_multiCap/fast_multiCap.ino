/* RCTiming_capacitance_meter_pF
 * Updated for Picofarad (pF) measurements using microseconds
 *
 * Theory:   
 * TC = R * C
 * TC = time constant period in seconds
 * R  = resistance in ohms
 * C  = capacitance in farads
 *
 * To get picofarads (10^-12 F) from microseconds (10^-6 s):
 * C (Farads) = TC (seconds) / R
 * C (pF) = (elapsedTime_uS * 10^-6) / R * 10^12
 * C (pF) = (elapsedTime_uS * 1,000,000) / R
 */

#define analogPin      0          // analog pin for measuring capacitor voltage
#define chargePin      13         // pin to charge the capacitor 
#define dischargePin   11         // pin to discharge the capacitor

// NOTE: Changed to 1 Megohm (1,000,000 ohms) because a 10k resistor 
// charges pF-scale capacitors too fast for the Arduino ADC to catch.
#define resistorValue  1000000.0F   

unsigned long startTime;
unsigned long elapsedTime;
float picoFarads;                

void setup(){
  pinMode(chargePin, OUTPUT);     // set chargePin to output
  digitalWrite(chargePin, LOW);
  Serial.begin(9600);             // initialize serial transmission
}

void loop(){
  digitalWrite(chargePin, HIGH);  // start charging the capacitor
  startTime = micros();           // record start time in microseconds

  // 648 is roughly 63.2% of 1023 (full 5V scale)
  while(analogRead(analogPin) < 648){       
    // Wait until the capacitor charges to 1 time constant
  }

  elapsedTime = micros() - startTime;

  // Math: (Microseconds * 1,000,000) / Ohms = Picofarads
  picoFarads = ((float)elapsedTime * 1000000.0) / resistorValue;

  // Print results to Serial Monitor
  Serial.print(elapsedTime);       
  Serial.print(" uS    ");         

  Serial.print((long)picoFarads);       
  Serial.println(" pF");         

  /* Discharge the capacitor */
  digitalWrite(chargePin, LOW);             // stop charging
  pinMode(dischargePin, OUTPUT);            // set discharge pin to output
  digitalWrite(dischargePin, LOW);          // pull it down to ground

  while(analogRead(analogPin) > 0){         // wait until completely drained
  }

  pinMode(dischargePin, INPUT);             // set discharge pin back to high-impedance
  
  delay(500);                               // brief pause to make serial data readable
}