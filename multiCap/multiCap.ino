/*
Name: Miles Modeste **built on 'singlecapacitor.ino' by Katelyn Rosethorn
Date Created: 6/2/2025
Last Updated: 6/5/2025

Description:
  Reads multiple capacitors connected to FDC1004 chips on TCA9548A multiplexor via I2C.
*/

#include <Wire.h>
#include <Protocentral_FDC1004.h>
#include <List.hpp>

#define TCAADDR1 0x70  // 1st link multiplexer
#define TCAADDR2 0x71  // 2nd link multiplexer (currently n/a)

#define UPPER_BOUND 0x7FFF
#define LOWER_BOUND (-1 * UPPER_BOUND)
#define ONEA 0  // channel
#define ONEB 1
#define TWOA 2
#define TWOB 3

#define MAX_WINDOW 10  //set 1 to disable; max: 255
#define SENSOR_COUNT 1
FDC1004 FDC;

/* Defines Sensor obj: 
includes addr, channel, window, window_sum, capacitance, and ; 
Sensor() sets defaults (i.e. address & channel = 0)*/
class Sensor {
public:
  uint8_t bus;      //multiplexor port (0-7) fdc chip is connected to
  uint8_t channel;  //chip channel

  uint8_t capdac = 0;  // Capacitance Digital-to-Analog Converter (subtracts baseline 0-15pF). Used for calibrating max capVal
  List<int16_t> window;
  uint8_t window_len = 0;
  int32_t window_sum = 0;

  uint16_t capVal;  //avg raw units

  bool isCalibrated = false;

  Sensor(uint8_t addr, uint8_t ch)
    : bus(addr), channel(ch) {}
  Sensor()
    : bus(0), channel(0) {}

  // Switches mux port to read from
  void SetBus(uint8_t bus) {
    Wire.beginTransmission(TCAADDR1);
    Wire.write(1 << bus);
    Wire.endTransmission();
  }

  void UpdateSensor() {
    SetBus(bus);
    FDC.configureMeasurementSingle(channel, channel, capdac);
    FDC.triggerSingleMeasurement(channel, FDC1004_100HZ);

    //wait for completion
    delay(15);
    uint16_t value[2];

    if (!FDC.readMeasurement(channel, value)) {
      uint16_t msb = value[0];

      if (window_len < MAX_WINDOW) {
        window_sum += msb;
        window.add(msb);
        window_len++;
      }
      else {
        window_sum -= window[0];
        window.removeFirst();
        window_sum += msb;
        window.add(msb);
      }
      capVal = window_sum/window_len;

      /* int32_t capacitance = ((int32_t)457) * ((int32_t)msb);  //in attofarads
      capacitance /= 1000;                                    //in femtofarads
      capacitance += ((int32_t)3028) * ((int32_t)capdac);
      */
    }
  }
  // Sets appropriate capdac
  long period = 200;

  void Calibrate() {
    // set lowAvg
    uint16_t lo,hi;
    isCalibrated = false;
    capdac = 0;
    //reset window
    window.clear();
    window_len = 0;
    window_sum = 0;
    unsigned long start = millis();
    while(true)
    {
      UpdateSensor();
      unsigned long timeDelta = start - millis();
      if (timeDelta >= period){
        lo = capVal;
        capdac ++;
        break;
      }
    }
    //set hiAvg
    while (!isCalibrated) {
      //reset window
      window.clear();
      window_len = 0;
      window_sum = 0;
      unsigned long start = millis();
      while (true)
      {
        UpdateSensor();
        unsigned long timeDelta = start - millis();
        if (timeDelta >= period)
        {
          hi = capVal;
          if (abs(lo) > abs(hi)) 
          {
            lo = hi;
            capdac++;
          }
          else if (abs(lo) <= abs(hi))
          {
            isCalibrated = true;
            return;
          }
        }
      }
    }
  }
};

Sensor sensors[SENSOR_COUNT];

void initSensors() {
  //**Note** adjust SENSORCOUNT accordingly
  /* sensors[0] = Sensor(0, TWOB);
  sensors[1] = Sensor(7, ONEB);
  sensors[2] = Sensor(0, ONEB);
  sensors[3] = Sensor(0, TWOA); */
  sensors[0] = Sensor(7, ONEA);
  for (int i=0; i<SENSOR_COUNT; i++){
    sensors[i].Calibrate();
  }
  return;
}

void Debug() {
  //Print statements
  String msg = "";
  for (int i = 0; i < SENSOR_COUNT; i++) {
    if (i != 0) {
      msg = ", ";
    }
    int reading = sensors[i].capVal;
    int offset = sensors[i].capdac;
    //msg += "sensor_" + (String)i + ":" + (String)reading;
    Serial.print("sensor_" + (String)i + ":");
    Serial.print(reading);
  }
  Serial.println();
}

/*
MAIN
*/

void setup() {
  Serial.begin(9600);
  Wire.begin();
  while (!Serial);
  initSensors();
  delay(1000);
}

void loop() {
  //1st Multiplexer
  for (int i = 0; i < SENSOR_COUNT; i++) {
    sensors[i].UpdateSensor();
  }
  Debug();
}