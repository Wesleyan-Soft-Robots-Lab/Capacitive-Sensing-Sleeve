/*
Name: Miles Modeste **edited from 'singlecapacitor.ino' by Katelyn Rosethorn
Date Created: 6/2/2025
Last Updated: 8/5/2025

Description:
  Fastest known method to read from mutliple FDC1004 chips.
  Includes simple, straightforward scalability.

Hardware Setup:
  + PCA9548A multiplexor connected via Pins: 3.3v, GND, 20(SDA), 21(SCL)
  + FDC1004 or other MUX's daisy chained together
  *Assumes each FDC has all four channels connected

How To Use:
  1. Redefine SENSOR_COUNT
  2. In initSensors(), Add sensor to sensors array with mux address and mux port.
*/

#include <Wire.h>
#include <Protocentral_FDC1004.h>

#define ADDR1 0x70  // 1st link multiplexer
#define ADDR2 0x71  // 2nd link multiplexer

#define UPPER_BOUND 0x6ACFC0  //7mill   possible bug might need to adjust
#define LOWER_BOUND (-1 * UPPER_BOUND)
#define CAPDAC_MAX (0x1F)
/* #define FDC_SCALAR 0x80000
#define CAPDAC_SCALAR 3.125 */
static const uint8_t MAX_CHANNELS = 4;

class Sensor : public FDC1004 {
public:
  uint8_t _mux = ADDR1;  // multiplexor address. see doc on how to set
  uint8_t _port;         // multiplexor port (0-7) FDC is connected to

  int32_t _channelValues[MAX_CHANNELS];  // raw FDC units. see ConvertToPF() for equation
  uint8_t _capdacValues[MAX_CHANNELS];
  bool _capdacAdjusted[MAX_CHANNELS];  // not used

  Sensor(uint8_t muxAddr = ADDR1, uint8_t port = 0)
    : FDC1004(FDC1004_100HZ), _mux(muxAddr), _port(port) {
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

  //Reads all 4 channels. updates _channelValues[]
  void UpdateChannels() {
    SetBus();

    for (uint8_t channel = 0; channel < 4; channel++) {
      configureMeasurementSingle(channel, channel, _capdacValues[channel]);
      triggerSingleMeasurement(channel, FDC1004_100HZ);  // check Protocentral_FDC1004.cpp for delay associated with rate (e.g 100HZ -> 11)
      delay(11);

      uint16_t value[2];  // first element is signed int16_t. second element is unsigned and last 8bits are all 0
      if (!readMeasurement(channel, value)) {
        int32_t raw_val = ((int32_t)(int16_t)value[0] << 8) | (value[1] >> 8);  // hence, raw_val is signed 24bits

        if ((raw_val > (int32_t)UPPER_BOUND) && (_capdacValues[channel] < FDC1004_CAPDAC_MAX)) {
          _capdacValues[channel] += 1;
          _capdacAdjusted[channel] = true;
        } else if ((raw_val < (int32_t)LOWER_BOUND) && (_capdacValues[channel] > 0)) {
          _capdacValues[channel] -= 1;
          _capdacAdjusted[channel] = true;
        }
        _channelValues[channel] = raw_val;
      }
    }
  }
  /*
  float ConvertToPF(uint32_t raw_value, uint8_t capdac) {                  ** this equation is now done in python (left it here for curious ppo)
    //Convert from raw measurement to picofarads
    //Capacitance (pf) = (measurement [23:0]) / 2^19 ) + C_offset
    float C_offset = (float)capdac * (float)CAPDAC_SCALAR;
    float capacitance_pF = (float)raw_value / (float)FDC_SCALAR + C_offset;
    return capacitance_pF;
  } */
};

//==================================
//=       Define FDC Sensors
//==================================

#define SENSOR_COUNT 3
Sensor sensors[SENSOR_COUNT];

void initSensors() {
  sensors[0] = Sensor(ADDR1, 7);
  sensors[1] = Sensor(ADDR1, 4);
  sensors[2] = Sensor(ADDR1, 5);
  return;
}

//needs tweaking
void Debug() {
  for (int i = 0; i < SENSOR_COUNT; i++) {
    if (i != 0) {
      Serial.print(";");
    }
    for (int c = 0; c < MAX_CHANNELS; c++) {
      Serial.print("sensor_" + (String)(i * 4 + c) + ",");
      Serial.print(sensors[i]._channelValues[c], 3);
      Serial.print(" ");
    }
  }
  Serial.println();
  return;
}


void TransmitData() {
  /*
  Format in bytes:
  |  0xAA  |      n       {       id        |   Sensor Data  } *n|
  | header | sensor_count | mux | port | ch | value | capdac |...|

  TODO: add checksum? more data from sensors: capdac adjusted? is sensor active?
  */

  //header
  byte header = 0xAA;
  Serial.write(header);
  //count
  uint8_t count = SENSOR_COUNT * MAX_CHANNELS;
  Serial.write(count);
  // Construct payload
  int dataSize = SENSOR_COUNT * MAX_CHANNELS * 5;
  byte data[dataSize];
  for (int i = 0; i < SENSOR_COUNT; i++) {
    for (int cha = 0; cha < MAX_CHANNELS; cha++) {
      int n = i * MAX_CHANNELS * 5 + cha * 5;
      //id
      data[n] = sensors[i]._mux << 5 | sensors[i]._port << 2 | (uint8_t)cha;
      //value
      int32_t val = sensors[i]._channelValues[cha];
      data[1 + n] = (val >> 16) & 0xFF;
      data[2 + n] = (val >> 8) & 0xFF;
      data[3 + n] = val & 0xFF;
      //capdac
      data[4 + n] = (uint8_t)sensors[i]._capdacValues[cha];  // 3 bits of unused data (feel free to use)
    }
  }
  Serial.write(data, dataSize);
  return;
}

/*
MAIN
*/

void setup() {
  Serial.begin(115200);
  Wire.begin();
  initSensors();
  while (!Serial)
    ;
}

void loop() {
  for (int i = 0; i < SENSOR_COUNT; i++) {
    sensors[i].UpdateChannels();
  }
  TransmitData();
  //Debug();        //cant use Transmit and Debug at the same time
}