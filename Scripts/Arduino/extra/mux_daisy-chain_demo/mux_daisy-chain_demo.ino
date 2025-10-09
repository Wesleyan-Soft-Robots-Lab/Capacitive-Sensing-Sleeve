/*
Name: Miles Modeste
Date Created: 8/7/2025

Description:
  Trying to test out how to communicate with i2c 
  devices connected to multiplexors daisy-chained together

Hardware:
  2 multiplexors
  1 sparkfun vcnl4040 proximity sensor
*/

#include <Wire.h>
#include "SparkFun_VCNL4040_Arduino_Library.h"

#define ADDR1 0x73  // 1st link multiplexer
#define ADDR2 0x70
#define ADDR3 0x74

class Multiplexor {
public:
  uint8_t _addr;
  Multiplexor* _prev;
  uint8_t _connectingPort;  // port on previous mux this mux is connected to

  Multiplexor(uint8_t name, Multiplexor* previous = nullptr, uint8_t connectingPort = 0)
    : _addr(name), _prev(previous), _connectingPort(connectingPort) {}
};
// set correct i2c wire based on chain
void ChangeWire(Multiplexor* mux, uint8_t port) {
  if (mux->_prev != nullptr) {
    ChangeWire(mux->_prev, mux->_connectingPort);
  }

  Wire.beginTransmission(mux->_addr);
  Wire.write(1 << port);
  Wire.endTransmission();
}

class Sensor {
public:
  Multiplexor* _mux;  // pointer to multiplexor
  uint8_t _port;      // multiplexor port (0-7) FDC is connected to

  VCNL4040 proximitySensor;

  unsigned int _proxValue;

  Sensor(Multiplexor* muxAddr = nullptr, uint8_t port = 0)
    : _mux(muxAddr), _port(port) {}

  //Reads all 4 channels. updates _channelValues[]
  void UpdateChannels() {
    ChangeWire(_mux, _port);
    _proxValue = proximitySensor.getProximity();
  }
};

Sensor s[1];

void setup() {
  Serial.begin(115200);
  Wire.begin();
  while (!Serial)
    ;

  Multiplexor root(ADDR1);
  Multiplexor mux2(ADDR2, &root, 3);
  Multiplexor mux3(ADDR3, &mux2, 4);
  s[0] = Sensor(&mux3, 0);

  s[0].proximitySensor.begin();
  //ChangeWire(s[0]._mux, 5);
}

void loop() {
  //unsigned int proxValue = proximitySensor.getProximity();
  //ChangeWire(s[0]._mux, s[0]._port);
  s[0].UpdateChannels();
  Serial.print("Proximity Value: ");
  Serial.print(s[0]._proxValue);
  Serial.println();

  delay(10);
}