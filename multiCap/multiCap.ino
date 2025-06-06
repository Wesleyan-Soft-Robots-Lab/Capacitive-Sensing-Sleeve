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

#define TCAADDR1 0x70 // 1st link multiplexer
#define TCAADDR2 0x71 // 2nd link multiplexer (currently n/a)

#define UPPER_BOUND  0X4000                 // max readout capacitance
#define LOWER_BOUND  (-1 * UPPER_BOUND)
#define ONEA 0 // channel
#define ONEB 1
#define TWOA 2
#define TWOB 3

#define capdac 5 // Capacitance Digital-to-Analog Converter (subtracts baseline 0-15pF)
#define SENSOR_COUNT 3
FDC1004 FDC;
/* Defines Sensor obj: 
includes addr, channel, window, window_sum, capacitance, and software_offset; 
Sensor() sets defaults (i.e. address & channel = 0)*/
class Sensor {
  public:
    uint8_t bus; //which multiplexor port (0-7) fdc chip is connected to
    uint8_t channel; //fdc channel
    List<int32_t> window;
    int32_t window_sum = 0;
    int16_t capVal;
    int16_t software_offset = 0; // in femtoFarads (1000 fF = 1 pF)

  Sensor(uint8_t addr, uint8_t ch) : bus(addr), channel(ch){}
  Sensor() : bus(0), channel(0) {}
  // Specifies which mux and port to read from
  void SetBus(uint8_t bus) 
  {
    Wire.beginTransmission(TCAADDR1);
    Wire.write(1 << bus);
    Wire.endTransmission();
  }
  void ReadChannel() {
    SetBus(bus);
    FDC.configureMeasurementSingle(channel, channel, capdac);
    FDC.triggerSingleMeasurement(channel, FDC1004_100HZ);

    //wait for completion
    delay(15);
    uint16_t value[2];

    if (! FDC.readMeasurement(channel, value))
    {
      int16_t msb = value[0];
      int32_t capacitance = ((int32_t)457) * ((int32_t)msb); //in attofarads
      capacitance /= 1000;   //in femtofarads
      capacitance += ((int32_t)3028) * ((int32_t)capdac);

      capVal = (uint16_t)capacitance;
    }
  }
};

//capdac and hardware_offset are essentially the same thing (not entirely sure how they affect offset)
uint8_t hardware_offset = 9; // offset (in pF) = hardware_offset * 3.125 (14)

bool is_calibrated = false;
int MAX_WINDOW = 10; // max window size for the rolling window stability. Set to 1 to disable.
Sensor sensors[SENSOR_COUNT];

void initSensors(){
  sensors[0] = Sensor(0, TWOB);
  sensors[1] = Sensor(7, ONEB);
  sensors[2] = Sensor(0, ONEB);

  return;
}

void Debug()
{
  //Print statements
  String msg = "";
  for (int i=0; i<SENSOR_COUNT; i++)
  {
    int reading = sensors[i].capVal/100;
    msg = " | sensor_" + (String) i + ": " + (String) reading;
    Serial.print(msg);
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
  for (int i=0; i<SENSOR_COUNT; i++)
  {
    sensors[i].ReadChannel();
  }
  Debug();
}