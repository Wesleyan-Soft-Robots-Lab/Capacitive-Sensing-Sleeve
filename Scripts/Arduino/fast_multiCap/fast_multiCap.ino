/*
Name: Miles Modeste **edited from 'singlecapacitor.ino' by Katelyn Rosethorn
Date Created: 6/2/2025
Last Updated: 6/10/2025

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

#define TCAADDR1 0x70  // 1st link multiplexer
#define TCAADDR2 0x71  // 2nd link multiplexer (currently unused)

#define UPPER_BOUND 0x6ACFC0 //7mill
#define LOWER_BOUND 0x3D0900 //4mill
#define CAPDAC_MAX (0x1F)
#define FDC_SCALAR 0x80000
#define CAPDAC_SCALAR 3.125
static const uint8_t MAX_CHANNELS = 4;

typedef enum {
  ONEA = 0,
  ONEB = 1,
  TWOA = 2,
  TWOB = 3
} fdc1004_channel_t;

class Sensor: public FDC1004 {
public:
  uint8_t _mux = TCAADDR1;  //multiplexor port (0-1) fdc chip is connected to
  uint8_t _port;            //multiplexor port (0-7) fdc chip is connected to

  float _channelValues[MAX_CHANNELS];  // 4 bytes
  uint8_t _capdacValues[MAX_CHANNELS];
  bool _capdacAdjusted[MAX_CHANNELS];

  Sensor(uint8_t muxAddr = TCAADDR1, uint8_t port = 0)
    :FDC1004(FDC1004_100HZ), _mux(muxAddr), _port(port) {
    for (int i = 0; i <= FDC1004_CHANNEL_MAX; ++i) {
      _capdacValues[i] = 0;
      _capdacAdjusted[i] = false;
    }
  }

  // Switch I2C wire to self
  void SetBus() {
    Wire.beginTransmission(_mux);
    Wire.write(1 << _port);
    Wire.endTransmission();
  }

  //Reads the sensor's values
  void UpdateSensor() {
    SetBus();

    for (uint8_t channel = 0; channel < 4; channel++) {
      configureMeasurementSingle(channel, channel, _capdacValues[channel]);
      triggerSingleMeasurement(channel, FDC1004_100HZ);
      delay(11);

      uint16_t value[2];
      if (!readMeasurement(channel, value)) {
        uint32_t raw_val = ((uint32_t)(uint16_t)value[0] << 8) | (value[1] >> 8);
        //Serial.print((int16_t)value[0]);
        Serial.print(raw_val);
        Serial.print("  ");
        if ((raw_val > (uint32_t)UPPER_BOUND) && (_capdacValues[channel] < FDC1004_CAPDAC_MAX)) {
          _capdacValues[channel] += 1;
          _capdacAdjusted[channel] = true;
        }else if ((raw_val < (uint32_t)LOWER_BOUND) && (_capdacValues[channel] > 0)) {
          _capdacValues[channel] -= 1;
          _capdacAdjusted[channel] = true;
        }
        _channelValues[channel] = ConvertToPF(raw_val, _capdacValues[channel]);
      }
    }
  }
  float ConvertToPF(int32_t raw_value, uint8_t capdac) const {
    // Convert from raw measurement to picofarads 
    //Capacitance (pf) = (measurement [23:0]) / 2^19 ) + C_offset
    float C_offset = (float)capdac * (float)CAPDAC_SCALAR;
    float capacitance_pF = ((float)raw_value / (float)FDC_SCALAR) + C_offset;
    return capacitance_pF;
  }
};

/*************************
      Define Sensors
**************************/
#define SENSOR_COUNT 2
Sensor sensors[SENSOR_COUNT];

void initSensors() {
  sensors[0] = Sensor(TCAADDR1, 7);
  sensors[1] = Sensor(TCAADDR1, 4);
  /* sensors[4] = Sensor(7, ONEA);
  sensors[5] = Sensor(7, ONEB);
  sensors[6] = Sensor(7, TWOA);
  sensors[7] = Sensor(7, TWOB); */
  return;
}

//Print capacitance in femtoFarads of each sensor
void Debug() {
  /* for (int i = 0; i < SENSOR_COUNT; i++) {
    if (i != 0) {
      Serial.print(";");
    }
    for (int c=0; c<MAX_CHANNELS; c++)
    {
      Serial.print("sensor_" + (String)(i*4+c) + ",");
      Serial.print(sensors[i]._capdacValues[c]);
      Serial.print("  ");
    }
  } */
  Serial.println();
  return;
}

void TransmitData() {
  /*
  Format in bytes:
  |  0xAA  |      n       [      Sensor Data       ] *n| "\n" | 
  | header | sensor_count | id | val_msb | val_lsb |...| tail |

  TODO: add checksum
  */
  /* int msgSize = 3 + SENSOR_COUNT * 3;

  byte header = 0xAA;
  byte count = SENSOR_COUNT;
  byte tail = 0x11;

  byte data[msgSize];
  data[0] = header;
  data[1] = count;
  // Construct payload
  for (int i = 0; i < SENSOR_COUNT; i++) {
    int n = 3 * i;
    data[2 + n] = (byte)i;
    uint16_t val = sensors[i].capacitance;
    data[3 + n] = (val >> 8) & 0xFF;
    data[4 + n] = (val)&0xFF;
  }
  data[-1] = tail;
  Serial.write(data, msgSize); */
  return;
}

/*
MAIN
*/

void setup() {
  Serial.begin(1000000);
  Wire.begin();
  initSensors();
  while (!Serial)
    ;
}

void loop() {
  for (int i = 0; i < SENSOR_COUNT; i++) {
    sensors[i].UpdateSensor();
  }
  //TransmitData();
  Debug();
}