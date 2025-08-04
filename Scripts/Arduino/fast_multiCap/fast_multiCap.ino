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

#define UPPER_BOUND 0x6ACFC0            //7mill
#define LOWER_BOUND (-1 * UPPER_BOUND)  //0x16E360 //1mill
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

class Sensor : public FDC1004 {
public:
  uint8_t _mux = TCAADDR1;  //multiplexor port (0-1) fdc chip is connected to
  uint8_t _port;            //multiplexor port (0-7) fdc chip is connected to

  float _channelValues[MAX_CHANNELS];
  uint8_t _capdacValues[MAX_CHANNELS];
  bool _capdacAdjusted[MAX_CHANNELS];

  Sensor(uint8_t muxAddr = TCAADDR1, uint8_t port = 0)
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
      triggerSingleMeasurement(channel, FDC1004_100HZ);
      delay(11);

      uint16_t value[2];
      if (!readMeasurement(channel, value)) {
        int32_t raw_val = ((int32_t)(int16_t)value[0] << 8) | (value[1] >> 8);  // raw_val is signed 24bit; value[0] = signed; value[1] = unsigned

        if ((raw_val > (int32_t)UPPER_BOUND) && (_capdacValues[channel] < FDC1004_CAPDAC_MAX)) {
          _capdacValues[channel] += 1;
          _capdacAdjusted[channel] = true;
        } else if ((raw_val < (int32_t)LOWER_BOUND) && (_capdacValues[channel] > 0)) {
          _capdacValues[channel] -= 1;
          _capdacAdjusted[channel] = true;
        }

        _channelValues[channel] = ConvertToPF(raw_val, _capdacValues[channel]);
        //_channelValues[channel] = (int16_t)value[0] << 8 | (value[1] >> 8);
      }
    }
  }
  float ConvertToPF(uint32_t raw_value, uint8_t capdac){
    //Convert from raw measurement to picofarads
    //Capacitance (pf) = (measurement [23:0]) / 2^19 ) + C_offset
    float C_offset = (float)capdac * (float)CAPDAC_SCALAR;
    float capacitance_pF = (float)raw_value / (float)FDC_SCALAR + C_offset;
    return capacitance_pF;
  }
};

/****************************
      Define FDC Sensors     
*****************************/
#define SENSOR_COUNT 1
Sensor sensors[SENSOR_COUNT];

void initSensors() {
  sensors[0] = Sensor(TCAADDR1, 7);
  //sensors[1] = Sensor(TCAADDR1, 4);
  return;
}

//Print capacitance in femtoFarads of each sensor
void Debug() {
  for (int i = 0; i < SENSOR_COUNT; i++) {
    if (i != 0) {
      Serial.print(";");
    }
    for (int c = 0; c < MAX_CHANNELS; c++) {
      Serial.print("sensor_" + (String)(i * 4 + c) + ",");
      Serial.print(sensors[i]._channelValues[c], 3);
      Serial.print("  ");
    }
  }
  Serial.println();
  return;
}


void TransmitData() {
  /*
  Format in bytes:
  |  0xAA  |      n       {       id        |   Sensor Data  } *n| "\n" | 
  | header | sensor_count | mux | port | ch | capdac | value |...| tail |

  TODO: add checksum? more data from sensors: current capdac, capdac adjusted?
  */
  int dataSize = SENSOR_COUNT * MAX_CHANNELS * 3;

  byte header = 0xAA;
  byte tail = 0x11;

  //header
  Serial.write(header);
  uint8_t count = SENSOR_COUNT * MAX_CHANNELS;
  Serial.write(count);
  // Construct payload
  byte data[dataSize];
  for (int i = 0; i < SENSOR_COUNT; i++) {
    for (int cha = 0; cha < MAX_CHANNELS; cha++) {
      int n = i * MAX_CHANNELS * 3 + cha * 3;
      //id
      data[n] = sensors[i]._mux << 5 | sensors[i]._port << 2 | (uint8_t)cha;
      uint16_t val = sensors[i]._channelValues[cha] * 1000;
      // msb
      data[1 + n] = val>>8;
      // lsb
      data[2 + n] = val;
      // capdac
      //data[3 + n] = (uint8_t)sensors[i]._capdacValues[cha]; // 3 bits of unused data (feel free to use)
    }
  }
  Serial.write(data, dataSize);
  // tail hopefully a checksum if not too cpu demanding
  //Serial.write(tail);
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
  //Debug();
}