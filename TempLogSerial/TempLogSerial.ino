/*****
Sends 3 Adafruit Temp Values via Serial 
*****/

#include <SPI.h>
#include <stdio.h>
#include "Adafruit_MAX31855.h"

int i = 0;
String strng = "";
char command;


// digital IO pins.
#define DO1   3
#define CS1   4
#define CLK1  5
#define DO2   6
#define CS2   7
#define CLK2  8
#define DO3   9
#define CS3   10
#define CLK3  11

// initialize the Thermocouples
Adafruit_MAX31855 thermocouple1(CLK1, CS1, DO1);
Adafruit_MAX31855 thermocouple2(CLK2, CS2, DO2);
Adafruit_MAX31855 thermocouple3(CLK3, CS3, DO3);

void setup() {  
  // initialize serial:
  Serial.begin(9600);

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
        double T1 = thermocouple1.readCelsius();
        double T2 = thermocouple2.readCelsius();
        double T3 = thermocouple3.readCelsius();

        String sT = String(T1,2) + ",";
        sT += String(T2,2) + ",";
        sT += String(T3,2) + ",";  
        Serial.println(sT);
        strng = "";
      } 
  }
}
