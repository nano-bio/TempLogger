/*****
Sends 2 Adafruit Temp Values via Serial, programmed for two amplifier boards
*****/

#include <SPI.h>
#include <stdio.h>
#include "Adafruit_MAX31856.h"

int i = 0;
String strng = "";
char command;


// digital IO pins.
#define CS1   2
#define DO1   3
#define CLK1  4
#define SDI1   8
//#define CS2   5
//#define DO2   6
//#define CLK2  7
//#define SDI2  9

// initialize the Thermocouples
Adafruit_MAX31856 thermocouple1 = Adafruit_MAX31856(CS1, SDI1, DO1, CLK1);
//Adafruit_MAX31856 thermocouple2 = Adafruit_MAX31856(CS2, SDI2, DO2, CLK2);

void setup() {  
  // initialize serial:
  Serial.begin(9600);
  thermocouple1.begin();
  //thermocouple2.begin();
  thermocouple1.setThermocoupleType(MAX31856_TCTYPE_K);
  //thermocouple2.setThermocoupleType(MAX31856_TCTYPE_K);

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
        //double T2 = thermocouple2.readThermocoupleTemperature();

        String sT = String(T1,2) + ",";
        //sT += String(T2,2) + ",";
        Serial.println(sT);
        strng = "";
      } 
  }
}
