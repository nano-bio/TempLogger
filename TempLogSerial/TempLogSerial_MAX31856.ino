/*****
Sends 3 Adafruit Temp Values via Serial, programmed for three Adafruit MAX31856 amplifier boards
*****/

#include <SPI.h>
#include <stdio.h>
#include "Adafruit_MAX31856.h"

String strng = "";
char command;


// digital IO pins.
#define SCK  2
#define SDO  3
#define SDI  4
#define CS1  8
#define CS2  9
#define CS3  10

// initialize the Thermocouples
Adafruit_MAX31856 thermocouple1 = Adafruit_MAX31856(CS1, SDI, SDO, SCK);
Adafruit_MAX31856 thermocouple2 = Adafruit_MAX31856(CS2, SDI, SDO, SCK);
Adafruit_MAX31856 thermocouple3 = Adafruit_MAX31856(CS3, SDI, SDO, SCK);

void setup() {  
  // initialize serial:
  Serial.begin(9600);
  thermocouple1.begin();
  thermocouple2.begin();
  thermocouple3.begin();
  thermocouple1.setThermocoupleType(MAX31856_TCTYPE_K);
  thermocouple2.setThermocoupleType(MAX31856_TCTYPE_K);
  thermocouple3.setThermocoupleType(MAX31856_TCTYPE_K);

  establishContact();  // send a byte to establish contact until receiver responds
}

void establishContact() {
  while (Serial.available() <= 0) {
    Serial.print('A');   // send a capital A
    delay(500);
  }
}

void loop() {
  // check if serial input
  if (Serial.available() > 0) {
      // idle if no command
      while(Serial.available() > 0)
      {
        command = ((byte)Serial.read());
        if(command == '\n'){
          break;
        }  
        else{
          strng += command;
        }
      }

      // identify on *IDN? command
      if(strng.equals("*IDN?")){
        Serial.write("Arduino\n");
        strng = "";
      }
      
      // print temperatures on *TMP? command
      if (strng.equals("*TMP?")){
        // send temperatures
       double T1 = thermocouple1.readThermocoupleTemperature();
       double T2 = thermocouple2.readThermocoupleTemperature();
       double T3 = thermocouple3.readThermocoupleTemperature();

       // internal temperature reading
       // double T1 = thermocouple1.readCJTemperature();
       // double T2 = thermocouple2.readCJTemperature();
       // double T3 = thermocouple3.readCJTemperature();

        String sT = String(T1,2) + ",";
        sT += String(T2,2) + ",";
        sT += String(T3,2) + ",";
        Serial.println(sT);
        strng = "";
      } 
  }
}
