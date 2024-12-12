#!/usr/bin/env python3
'''
Simple class for IDQ Time Tagger
'''
from .SkippyDevice import SkippyDevice

class TimeController(SkippyDevice):
    def __init__(self, ip: str, port: int, name: str = ""):

        super().__init__(ip, port, name)
        self.id()
        self.dark = False


    def id(self) -> str:
        cmd = "*IDN?"
        res = self.send(cmd)
        # do something with the returned ID here
        return res

    def dark_mode(self, on: bool = True):
        on_str = "ON" if on else "OFF"
        cmd = f"DEVICE:LEDS {on_str}"
        self.send(cmd)
        self.dark = on

    def config_clock(self, ch: int, period: int, count: int=-1, pw: int=0):
        '''
        ch - channel number
        period - in [ps]
        pw - pulse width in ps

        '''
        if pw == 0:
            pw = period/2
        if count < 0:
            count = "INF"
        cmd = f"GEN{ch}:enable ON;PNUM {count};PPER {period};PWID {pw}"
        setattr(self, f"GEN{ch}", 1)
        self.send(cmd)

    #def config_pulse(self, ch: int, period: int, count: int, pw: int, delay: int=0):
    #    cmd = f"GEN{ch}:enable ON;PNUM {count};PPER {period};PWID {pw}"

    def play(self, ch):
        self.send(f"GEN{ch}:PLAY")

    def stop(self, ch):
        self.send(f"GEN{ch}:STOP")

    def link(self, ch1, ch2):
        self.send(f"GEN{ch1}:TRIG:LINK GEN{ch2}")

    def delay(self, ch1, delay: int=0):
        self.send(f"GEN{ch1}:TRIG:DELAY {delay}")
