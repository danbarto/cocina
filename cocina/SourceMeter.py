#!/usr/bin/env python3
#
# User manual: 
#
# Example https://github.com/tektronix/keithley/blob/main/Instrument_Examples/DAQ6510/Scanning_Low_Level_DC_Voltage/DAQ6510_Scanning_Low_Level_DC_Voltage_SCPI.py
# If observe error -285, change command language to SCPI (from TSP)
from .colors import green, red, yellow, dummy
from .SkippyDevice import SkippyDevice
from .GlobalLock import GlobalLock

import numpy as np

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
                 wait=0.01,
                 ):

        # NOTE not sure if this needs locking
        super().__init__(ip, port, name, timeout, wait)
        self.timeout = timeout
        self.id()
        self.mode="V"
        self.buffers = []

    def id(self):
        with GlobalLock(self.ip):
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
        with GlobalLock(self.ip):
            return float(self.query(":MEAS:CURR?"))

    def set_mode_voltage(self,
                         v_range: float=20,
                         voltage: float=0,
                         i_max: float=0.00005,
                         i_range: float=0.000105,
                         ):
        assert i_max<i_range, f"Current limit {i_max} is larger than range {i_range}. Aborting."
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

    def set_current_range(self,
                          i_range: float = 0.000105,
                          i_max:   float = 0.00005,
                          ):
        assert i_max<i_range, f"Current limit {i_max} is larger than range {i_range}. Aborting."
        self.write(":SENS:CURR:RANGE", i_range, strict=False)
        self.write(":SOURCE:VOLT:ILIMIT", i_max, strict=False)
        self.measure()

    def set_voltage(self,
                    voltage: float=0,
                    ):
        if self.mode=="V":
            self.send(f":SOURCE:VOLT {voltage}")
        self.measure()

    def averaged_current(self,
                         count: int = 10,
                         voltage: float = 0,
                         ):
        '''
        NOTE: WIP
        This function should check if the used buffer already exists.
        '''
        buffer_name = 'ivbuffer'
        if not buffer_name in self.buffers:
            self.send(f'TRACe:MAKE "{buffer_name}", {count}')
            self.buffers.append(buffer_name)
            print(self.buffers)
        self.send(f'TRIGger:LOAD "SimpleLoop", {count}, 0, "{buffer_name}"')
        self.send(f"SOURCE:VOLT {voltage}")
        self.send("INIT")
        self.send("*WAI")
        res = np.fromstring(self.query(f'TRAC:DATA? 1, {count}, "{buffer_name}", READ, SOUR, REL'), sep=",")

        return res[::3], res[1::3], res[2::3]  # current, voltage, timestamp

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
        Select front terminal
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
