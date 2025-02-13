#!/usr/bin/env python3
#
# User manual: 
#
# Example https://github.com/tektronix/keithley/blob/main/Instrument_Examples/DAQ6510/Scanning_Low_Level_DC_Voltage/DAQ6510_Scanning_Low_Level_DC_Voltage_SCPI.py
# If observe error -285, change command language to SCPI (from TSP)
import socket
import time
#import pyvisa as visa
from pymeasure.instruments.keithley import Keithley2450 as Keithley

from .colors import green, red, yellow, dummy
from .SkippyDevice import SkippyDevice

topline = "┏━" + "━"*20 + "━┓"
botline = "┗━" + "━"*20 + "━┛"

'''
# pyvisa version
rm = visa.ResourceManager()
smu = rm.open_resource("TCPIP::192.168.0.77::INSTR")
smu.write("*IDN?")
print(smu.read())

'''

'''
# pymeasure version
smu = Keithley("TCPIP::192.168.0.77::INSTR")


'''


class SourceMeter(SkippyDevice):
    def __init__(self,
                 name,
                 ip,
                 port=5025,
                 timeout=1,
                 wait=0.5,
                 ):

        super().__init__(ip, port, name, timeout, wait)
        self.timeout = timeout
        self.connect()
        self.id()

    def id(self):
        # identical to "echo "*IDN?" | netcat -q 1 {IP} {PORT}"
        res = self.query('*IDN?').split(',')
        #print(res)

    def measeure(self):
        self.query(":MEAS:CURR?")

    def set_mode(self):
        self.send(":SOURCE:FUNCTION VOLT")
        smu.send(":SOURCE:VOLT:RANGE 200")

    def enable(self):
        '''
        Enable the output
        '''
        self.send(":OUTP ON")

    def disable(self):
        '''
        Disable the output
        '''
        self.send(":OUTP OFF")

    def set_front_term(self):
        '''
        Select fron terminal
        '''
        self.send(":ROUT:TERM FRON")

    def get_output(self) -> bool:
        '''
        Get output status:
        ON - TRUE
        OFF - FALSE
        '''
        return self.query(":OUTP:STATE?")=="ON"
    
    def beep(self, freq: int=200, dur: int=1):
        '''
        Sound a beep on the instrument
        Parameters:
            freq (int): Frequency of the beep
            dur (int): Duration in seconds
        '''
        self.send(f":SYST:BEEP {freq},{dur}")