/* 
Name: Miles Modeste **edited from 'singlecapacitor.ino' by Katelyn Rosethorn
Date Created: 7/24/2025
Last Updated: 7/24/2025

Description:
  Quickly reads full range of multiple capacitors connected 
  to FDC1004 chips on TCA9548A multiplexor via I2C.
  This is using the protocentral library for lower lvl FDC communication
  with maybe more accurate readings/ less noise.

  ***************************
  *
  *   !!!  As of 7/31/2025 Protocentral_FDC1004.h version 2.0.0 DOES NOT WORK 
  *         (setting the capdac doesn't change anything about offset)
  *
  ***************************
Hardware Setup (Example):
  + 5v
  + One sensor patch connected to channel ONEA via multiplexor on port 7
  + One sensor patch connected to channel TWOA via multiplexor on port 7

  ** Tip you can change hardware setup in the init function
*/

#include <Wire.h>
#include <Protocentral_FDC1004.h>

#define TCAADDR1 0x70  // 1st link multiplexer
#define TCAADDR2 0x71  // 2nd link multiplexer (currently unused)
#define ONEA 0         // channels
#define ONEB 1
#define TWOA 2
#define TWOB 3
static const uint8_t MAX_CHANNELS = 4;
//============================
// Expand FDC as Sensor
//============================
class Sensor : public FDC1004 {
public:
  uint8_t _mux = TCAADDR1;
  uint8_t _port;
  fdc1004_channel_t _channels[MAX_CHANNELS] = { ONEA, ONEB, TWOA, TWOB };

  int32_t _channelValues[MAX_CHANNELS];
  bool _channelValid[MAX_CHANNELS];
  uint8_t _capdacValues[MAX_CHANNELS];
  bool _capdacAdjusted[MAX_CHANNELS];

  Sensor(uint8_t addr = 0, uint8_t port = 0)
    : FDC1004(&Wire,FDC1004_RATE_400HZ,FDC1004_I2C_ADDRESS), _mux(addr), _port(port) {}

  void ReadChannels() {
    for (uint8_t chan = 0; chan < MAX_CHANNELS; ++chan) {
      fdc1004_capacitance_t measurement = getCapacitanceMeasurement((fdc1004_channel_t)chan);

      if (!isnan(measurement.capacitance_pf)) {
        _channelValues[chan] = measurement.capacitance_pf;
        Serial.print(measurement.capacitance_pf,2);
        Serial.print(" ");
        _channelValid[chan] = true;
        _capdacValues[chan] = measurement.capdac_used;
        _capdacAdjusted[chan] = measurement.capdac_out_of_range;
      } else {
        _channelValues[chan] = 0.0;
        _channelValid[chan] = false;
        _capdacValues[chan] = 0;
        _capdacAdjusted[chan] = false;
      }
      /* Serial.print(_channelValues[chan],4);
      Serial.print(" "); */
      // Small delay between channels for stability
      delay(10);
    }
  }

  void UpdateSensor() {
    ReadChannels();
    return;
  }
};

void SetBus(uint8_t mux, uint8_t port) {
  Wire.beginTransmission(mux);
  Wire.write(1 << port);
  Wire.endTransmission();
}

#define FDC_COUNT 1
Sensor sensors[FDC_COUNT];

void initSensors() {
  SetBus(TCAADDR1, 4);
  sensors[0] = Sensor(TCAADDR1, 4);
  sensors[0].begin();
  sensors[0].setCapdac(FDC1004_CHANNEL_3, (uint8_t)10);
  

  /* SetBus(TCAADDR1, 7);
  sensors[1] = Sensor(TCAADDR1, 7);
  sensors[1].begin(); */
  return;
}

void setup() {
  Serial.begin(1000000);
  Wire.begin();
  initSensors();
  while (!Serial)
    ;
}

void loop() {
  for (int i = 0; i < FDC_COUNT; i++) {
    SetBus(sensors[i]._mux, sensors[i]._port);
    sensors[i].UpdateSensor();

    /* for (int c = 0; c < MAX_CHANNELS; ++c) {
      Serial.print("Sensor_");
      Serial.print(i);
      Serial.print(c);
      Serial.print("; ");
      Serial.print(sensors[i]._channelValues[c]);
      Serial.print(", ");
    } */
  }
  Serial.println();
}