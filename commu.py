#!/usr/bin/python
import serial
import re
import time

class Commu():
    def __init__(self, port = 'COM1'):
        self.port = port
        self.ser = serial.Serial(self.port, 9600, timeout=1)

        # check whether we are actually connecting to an Arduino
        self.ser.write('*IDN?'.encode())
        response = self.ser.readline().decode()
        if u'Arduino' not in response:
            raise RuntimeError(u'This does not seem to be an Arduino!')

        # compile the regex to parse read out values
        self.valuepattern = re.compile('^([+|-][0-9]{1}\.[0-9]{2,6}E-[0-9]{2}A).*$')

        # save connected state
        self.connected = True

    def read_value(self):
        if self.connected:

            #flush buffer and read twice if corrupt
            self.ser.flushInput()
            self.ser.write(b'*TMP?\n')
            value = self.ser.readline().decode("utf-8")

            values = value.split(',')
            if len(values)<4:
                self.ser.write(b'*TMP?\n')
                value = self.ser.readline().decode("utf-8")
                values = value.split(',')


            # check if serial input makes sense
            val2=[]
            for val in values:
                if 'N' in val:
                    val = ('N/A')
                val2.append(val)

            return val2

    def close(self):
        if self.connected:
            self.ser.close()
