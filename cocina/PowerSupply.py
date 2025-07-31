#!/usr/bin/env python3
#
# User manual: https://siglentna.com/wp-content/uploads/dlm_uploads/2022/11/SPD3303X_QuickStart_E02A.pdf
#
import time

from .colors import green, red, yellow, dummy
from .SkippyDevice import SkippyDevice
from .GlobalLock import GlobalLock

topline = "┏━" + "━"*20 + "━┓"
botline = "┗━" + "━"*20 + "━┛"

class PowerSupply(SkippyDevice):
    def __init__(self,
                 name,
                 ip,
                 port=5025,
                 timeout=1,
                 ):

        self.key = False
        with GlobalLock(ip, key=self.key):
            super().__init__(ip, port, name, timeout)
            self.channels = ['CH1', 'CH2', 'CH3']
            self.mon_channels = ['CH1', 'CH2'] # CH3 not working
            self.timeout = timeout
            self.key = True
            try:
                self.id()
                self.status()
            except:
                print("Couldn't query ID or status")
                raise
            self.key=False
            print(f"Connected to PSU@{self.ip}")
            print(f" - ID: {self.model}, {self.sn}")


    def id(self):
        # identical to "echo "*IDN?" | netcat -q 1 {IP} {PORT}"
        with GlobalLock(self.ip, key=self.key):
            res = self.query('*IDN?').split(',')
            try:
                self.model = res[1]
                self.sn = res[2]
                self.firmware = res[3]
                self.hardware = res[4]
            except IndexError:
                print("Unexpected ID", res)
                self.model = "Default"

    def status(self):
        with GlobalLock(self.ip, key=self.key):
            res = int(self.query('SYSTEM:STATUS?'), 16)
            self.CH1 = (res >> 4) & 0x1
            self.CH2 = (res >> 5) & 0x1

    def measure(self, channel='CH1', parameter='VOLTAGE'):
        with GlobalLock(self.ip):
            parameter = parameter.upper()
            channel = channel.upper()
            assert parameter in ['VOLTAGE', 'CURRENT', 'POWER'], f"Don't know what to do with parameter {parameter}"
            assert channel in self.mon_channels, f"Don't know what to do with channel {channel}"

            cmd = f"MEASURE:{parameter}? {channel}"
            return float(self.query(cmd))

    def monitor(self):

        status = self.status()

        res = {}
        for channel in self.mon_channels:
            res[channel] = {}
            res[channel]['Voltage'] = self.measure(channel = channel, parameter = 'VOLTAGE')
            res[channel]['Current'] = self.measure(channel = channel, parameter = 'CURRENT')


        for channel in self.mon_channels:
            if getattr(self, channel) == 1: colored = green
            elif getattr(self, channel) == 0: colored = red
            print(colored(topline))
            print(colored( "┃ {:10}{:10} ┃".format("Channel", channel) ))
            print(colored( "┃ {:10}{:10} ┃".format("Voltage", res[channel]["Voltage"]) ))
            print(colored( "┃ {:10}{:10} ┃".format("Current", res[channel]["Current"]) ))
            print(colored(botline))

    def power_down(self, channel):
        assert channel.upper() in self.channels, "Selected channel does not exist"
        self.send(f"OUTPUT {channel.upper()},OFF")

    def power_up(self, channel):
        assert channel.upper() in self.channels, "Selected channel does not exist"
        self.send(f"OUTPUT {channel.upper()},ON")

    def cycle(self, channel=None, wait=2):
        print(f"Turning OFF channel {channel}.")
        self.power_down(channel)
        time.sleep(wait)
        print(f"Turning ON channel {channel}.")
        self.power_up(channel)

    def set_voltage(self, channel, value):
        with GlobalLock(self.ip):
            self.send(f"{channel}:VOLT {value}")

    def set_current(self, channel, value):
        self.send(f"{channel}:CURR {value}")
