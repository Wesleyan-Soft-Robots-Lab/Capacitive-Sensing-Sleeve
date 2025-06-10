/*
Name: Miles Modeste **built on 'singlecapacitor.ino' by Katelyn Rosethorn
Date Created: 6/2/2025
Last Updated: 6/9/2025

Description:
  Quickly reads full range of multiple capacitors connected to FDC1004 chips on TCA9548A multiplexor via I2C.
  Offers easy edits to read more sensors via more multiplexors. 

Hardware Setup:
  + 5v
  + One sensor patch connected to channel ONEA via multiplexor on port 7
  + One sensor patch connected to channel TWOA via multiplexor on port 7

  ** Tip you can change hardware setup in the init function
*/

#include <Wire.h>
#include <Protocentral_FDC1004.h>
#include <List.hpp>

#define TCAADDR1 0x70  // 1st link multiplexer
#define TCAADDR2 0x71  // 2nd link multiplexer (currently unused)

#define UPPER_BOUND 0x7FFF // max val for uint16_t
#define LOWER_BOUND (-1 * UPPER_BOUND)
#define ONEA 0  // channel
#define ONEB 1
#define TWOA 2
#define TWOB 3

FDC1004 FDC;

/* Defines Sensor obj: 
includes addr, channel, window, window_sum, capacitance, and ; 
Sensor() sets defaults (i.e. address & channel = 0)*/
class Sensor {
public:
  uint8_t mux = TCAADDR1; //multiplexor port (0-1) fdc chip is connected to
  uint8_t bus;            //multiplexor port (0-7) fdc chip is connected to
  uint8_t channel;        //chip channel

  uint16_t value[2];
  int16_t msb, lsb;       //most and least significant byte. displaying lsb only helps with viewing full range of msb

  uint8_t capdac = 9;     // Capacitance Digital-to-Analog Converter (subtracts baseline 0-15pF). Used for calibrating max capVal
  int32_t capacitance;    // In femtoFarads 

  Sensor(uint8_t addr=0, uint8_t ch=0, uint8_t muxPort=TCAADDR1)
    : bus(addr), channel(ch), mux(muxPort) {}

  // Switches mux port to read from
  void SetBus(uint8_t mux, uint8_t bus) {
    if (bus > 7) {
      Serial.println("Error: bus must be between 0 and 7");
      return;
    }

    Wire.beginTransmission(mux);
    Wire.write(1 << bus);
    Wire.endTransmission();
  }

  //Reads the sensor's values
  void UpdateSensor() {
    SetBus(mux, bus);
    FDC.configureMeasurementSingle(channel, channel, capdac);
    FDC.triggerSingleMeasurement(channel, FDC1004_100HZ);

    delay(15);

    if (!FDC.readMeasurement(channel, value)) {
      msb = value[0];
      lsb = value[1]; //LEAST significant byte

      //hard press to calibrate capdac
      if ((msb >= UPPER_BOUND)) {
        Serial.println("msb too high:"+ (String) msb+ "| Increasing capdac...");
        capdac = (capdac < 15)? capdac+1: 15;
        return;
      } else if (msb <= LOWER_BOUND) {
        Serial.println("msb too low:"+ (String) msb+ "| Decreasing capdac...");
        capdac = (capdac > 0)? capdac-1: 0;
      }

      capacitance = ((int32_t)457) * ((int32_t)msb);  //in attofarads
      capacitance /= 1000;                              //in femtofarads
      capacitance += ((int32_t)3028) * ((int32_t)capdac);
    }
  }
};

/*************************
      Define Sensors
**************************/
#define SENSOR_COUNT 2
Sensor sensors[SENSOR_COUNT];

void initSensors() {
  sensors[0] = Sensor(7, ONEA);
  sensors[1] = Sensor(7, ONEB);
  return;
}

//Print capacitance in femtoFarads of each sensor
void Debug() {
  for (int i = 0; i < SENSOR_COUNT; i++) {
    if (i != 0) {
      Serial.print(", ");
    }
    Serial.print("sensor_" + (String)i + ":");
    Serial.print(sensors[i].capacitance);
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
  delay(500);
}

void loop() {
  for (int i = 0; i < SENSOR_COUNT; i++) {
    sensors[i].UpdateSensor();
  }
  Debug();
}