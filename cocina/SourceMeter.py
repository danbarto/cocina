#!/usr/bin/env python3
#
# User manual: 
#
# Example https://github.com/tektronix/keithley/blob/main/Instrument_Examples/DAQ6510/Scanning_Low_Level_DC_Voltage/DAQ6510_Scanning_Low_Level_DC_Voltage_SCPI.py
# If observe error -285, change command language to SCPI (from TSP)
from .colors import green, red, yellow, dummy
from .SkippyDevice import SkippyDevice

topline = "┏━" + "━"*20 + "━┓"
botline = "┗━" + "━"*20 + "━┛"

'''
# pyvisa version
import pyvisa as visa
rm = visa.ResourceManager()
smu = rm.open_resource("TCPIP::192.168.0.77::INSTR")
smu.write("*IDN?")
print(smu.read())
'''

'''
# pymeasure version
from pymeasure.instruments.keithley import Keithley2450 as Keithley
smu = Keithley("TCPIP::192.168.0.77::INSTR")
smu.id
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
        self.id()
        self.mode="V"

    def id(self):
        # identical to "echo "*IDN?" | netcat -q 1 {IP} {PORT}"
        res = self.query('*IDN?').split(',')
        try:
            self.manufacturer = res[0]
            self.model = res[1]
            self.sn = res[2]
            self.firmware = res[3]
        except IndexError:
            self.model = "Default"

    def measure(self):
        return float(self.query(":MEAS:CURR?"))

    def set_mode_voltage(self,
                         v_range: float=20,
                         voltage: float=0,
                         i_max: float=0.00005,
                         i_range: float=0.000105,
                         ):
        assert i_max<i_range, "Current limit is larger than range. Aborting."
        assert voltage < v_range, "Voltage is larger than voltage range. Aborting."
        self.send(':SENS:FUNC "CURR"')
        self.send(f":SENS:CURR:RANGE {i_range}")
        self.send(f":SOURCE:VOLT:ILIMIT {i_max}")
        self.send(":SOURCE:FUNCTION VOLT")
        self.send(f":SOURCE:VOLT 0")
        self.send(f":SOURCE:VOLT:RANGE {v_range}")
        self.send(f":SOURCE:VOLT {voltage}")
        self.mode="V"
        self.measure()

    def set_voltage(self,
                    voltage: float=0,
                    ):
        if self.mode=="V":
            self.send(f":SOURCE:VOLT {voltage}")
        self.measure()

    def get_voltage(self):
        return float(self.query(":SOURCE:VOLT?"))

    def is_tripped(self):
        if self.mode == "V":
            return self.query(":SOURCE:VOLT:ILIMIT:TRIP?") == "1"
        elif self.mode == "I":
            return self.query(":SOURCE:CURR:VLIMIT:TRIP?") == "1"


    def enable(self):
        '''
        Enable the output
        '''
        self.send(":OUTP ON")
        self.measure()

    def disable(self):
        '''
        Disable the output
        '''
        self.send(":OUTP OFF")
        self.measure()

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
        return self.query(":OUTP:STATE?")=="1"
    
    def beep(self, freq: int=2000, dur: float=1):
        '''
        Sound a beep on the instrument
        Parameters:
            freq (int): Frequency of the beep
            dur (int): Duration in seconds
        '''
        self.send(f":SYST:BEEP {freq}, {dur}")