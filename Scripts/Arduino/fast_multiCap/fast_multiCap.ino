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
  1. Specify FDC_COUNT, MUX_COUNT
  2. In initialize(), Create multiplexor and sensor objects, adding sensors to array with corresponding multiplexor pointer and connecting port.

  BITMASK ORDER {TWOB, TWOA, ONEB, ONEA}
*/

#include <Wire.h>
#include <Protocentral_FDC1004.h>

/* 
a0  a1  a2
0   0   0   = 0x70
1   0   0   = 0x71
0   1   0   = 0x72
1   1   0   = 0x73
*/
#define ADDR1 0x72  // 1st link multiplexer
#define ADDR2 0x71
#define ADDR3 0x70
#define ADDR4 0x73
#define ADDR5 0x74

#define UPPER_BOUND 0x6ACFC0  //7mill   possible bug might need to adjust
#define LOWER_BOUND (-1 * UPPER_BOUND)
#define CAPDAC_MAX (0x1F)
/* #define FDC_SCALAR 0x80000
#define CAPDAC_SCALAR 3.125 */
static const uint8_t MAX_CHANNELS = 4;

class Multiplexor {
public:
  uint8_t _addr;
  Multiplexor* _prev;
  uint8_t _connectingPort;  // port on previous mux this mux is connected to

  /* 
  name : address associated with the a-pins on the back of the multiplexor.
  previous : address location of the previous multiplexor object (not the a-pins). leave blank if its the root.
  connectingPort : the channel on the previous multiplexor that THIS multiplexor is connected by. leave blank if root.
  */
  Multiplexor(uint8_t name, Multiplexor* previous = nullptr, uint8_t connectingPort = 0)
    : _addr(name), _prev(previous), _connectingPort(connectingPort) {}
};

// Cache to store the current state of each multiplexer to avoid redundant I2C writes
static uint8_t muxState[128] = {0}; // Initialize with 0 (no ports selected, or just a default state)

// sets correct i2c wire based on chain
void ChangeWire(Multiplexor* mux, uint8_t port) {
  if (mux->_prev != nullptr) {
    ChangeWire(mux->_prev, mux->_connectingPort);
  }
  
  if (muxState[mux->_addr] != (1 << port)) {
    Wire.beginTransmission(mux->_addr);
    Wire.write(1 << port);
    Wire.endTransmission();
    muxState[mux->_addr] = (1 << port);
  }
}

/* 
FDC sensor object
 */
class Sensor : public FDC1004 {
public:
  Multiplexor* _mux;  // pointer to multiplexor object
  uint8_t _port;      // multiplexor port (0-7) FDC is connected to

  bool _activeChannels[MAX_CHANNELS];
  int32_t _channelValues[MAX_CHANNELS];  // raw FDC units. see ConvertToPF() for equation
  uint8_t _capdacValues[MAX_CHANNELS];
  bool _capdacAdjusted[MAX_CHANNELS];  // not used

  Sensor(Multiplexor* muxAddr = nullptr, uint8_t port = 0, uint8_t channelMask = 0b1111)
    : FDC1004(FDC1004_100HZ), _mux(muxAddr), _port(port) {
    for (int i = 0; i <= FDC1004_CHANNEL_MAX; ++i) {
      _capdacValues[i] = 0;
      _capdacAdjusted[i] = false;
      _activeChannels[i] = channelMask & (1 << i);
    }
  }

  // Trigger measurement for a specific channel
  void TriggerChannel(uint8_t channel) {
    if (_activeChannels[channel]) {
      ChangeWire(_mux, _port);
      configureMeasurementSingle(channel, channel, _capdacValues[channel]);
      triggerSingleMeasurement(channel, FDC1004_400HZ);
    }
  }

  // Read measurement for a specific channel
  void ReadChannel(uint8_t channel) {
    if (_activeChannels[channel]) {
      ChangeWire(_mux, _port);
      uint16_t value[2];
      if (!readMeasurement(channel, value)) {
        int32_t raw_val = ((int32_t)(int16_t)value[0] << 8) | (value[1] >> 8);

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
};

//=======================================
//=   Define FDC Sensors, Multiplexors
//=======================================

#define FDC_COUNT 3 //10
#define MUX_COUNT 2  //3
Sensor sensors[FDC_COUNT];
Multiplexor* mux[MUX_COUNT];

void initialize() {
  //store addresses in heap
  mux[0] = new Multiplexor(ADDR5);
  mux[1] = new Multiplexor(ADDR3, mux[0], 7);
  // mux[1] = new Multiplexor(ADDR2, mux[0], 3);
  // mux[2] = new Multiplexor(ADDR3, mux[1], 4);

  sensors[0] = Sensor(mux[0], 0);

  sensors[1] = Sensor(mux[0], 4);
  sensors[2] = Sensor(mux[1], 0);
  //sensors[2] = Sensor(mux[0], 2);
  // sensors[3] = Sensor(mux[0], 3);
  // sensors[4] = Sensor(mux[0], 4);
  // sensors[5] = Sensor(mux[0], 5);
  // sensors[6] = Sensor(mux[0], 6);
  // sensors[7] = Sensor(mux[0], 7);

  return;
}

/*
Prints the channelValues in the serial monitor.
cannot work if TransmitData() is also running
*/
void Debug() {
  for (int i = 0; i < FDC_COUNT; i++) {
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
  delay(500);
  return;
}

/*
Creates and sends binary message of every sensors: index/id, raw value, capdac used

Format in bytes:
| 0xAA | 0xBB |      n       {       id        |   Sensor Data  } *n|
| hdr1 | hdr2 | sensor_count | mux | port | ch | value | capdac |...|

TODO: add checksum? more data from sensors: capdac adjusted? is sensor active?
*/
void TransmitData() {
  //header
  byte header[] = {0xAA, 0xBB};
  Serial.write(header, 2);
  //count
  uint8_t count = FDC_COUNT * MAX_CHANNELS;
  Serial.write(count);
  // Constructs the payload
  int dataSize = FDC_COUNT * MAX_CHANNELS * 5;
  byte data[dataSize];
  for (int i = 0; i < FDC_COUNT; i++) {
    for (int cha = 0; cha < MAX_CHANNELS; cha++) {
      int n = i * MAX_CHANNELS * 5 + cha * 5;
      //id
      data[n] = i * MAX_CHANNELS + cha;
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

//TODO: recieve specific keycode from python to change active channels on a particular sensor
void ReceiveData() {
  byte data = Serial.read();
  // uint8_t code = (data & 0b11110000)>> 4;
  // if (code == 1) {
  //   data = data & 0b00001111;
  //   sensor = Serial.read();
  // }
}

/*
MAIN
*/

void setup() {
  Serial.begin(250000);
  Wire.begin();
  Wire.setClock(400000);
  initialize();
  while (!Serial);
}

void loop() {
  unsigned long loopStart = micros();
  for (uint8_t channel = 0; channel < MAX_CHANNELS; channel++) {
    // 1. Trigger this channel on all sensors
    for (int i = 0; i < FDC_COUNT; i++) {
      sensors[i].TriggerChannel(channel);
    }
    
    // 2. Wait once for the measurement to complete (400Hz -> 2.5ms, so 3ms is safe)
    delay(3);
    
    // 3. Read the measurements
    for (int i = 0; i < FDC_COUNT; i++) {
      sensors[i].ReadChannel(channel);
    }
  }
  
  unsigned long elapsedFDC = micros() - loopStart;
  // Serial.print("All sensors total read time(micros): ");
  // Serial.println(elapsedFDC);

  unsigned long transmitData = micros();
  TransmitData();
  //  Debug();  //cant use Transmit and Debug at the same time
  // if (Serial.available() > 0) {
  //    ReceiveData();
  // }
  unsigned long elapsedData = micros() - transmitData;
  // Serial.print("Transmit time (micros): ");
  // Serial.println(elapsedData);
}