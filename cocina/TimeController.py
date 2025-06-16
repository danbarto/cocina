#!/usr/bin/env python3
'''
Simple class for IDQ Time Tagger
'''
from .SkippyDevice import SkippyDevice

class TimeController(SkippyDevice):
    def __init__(self,
                 name,
                 ip: str,
                 port: int,
                 timeout: int=1,
                 wait: float=0.01,
                 ):
        '''
        Initialize the TimeController

        Parameters:
            ip (str): IP Address of the device
            port (int): port that is used on the device
            name (str): arbitrary name of the device
        '''

        super().__init__(ip, port, name, timeout, wait)
        self.id()
        self.dark = False


    def id(self) -> str:
        '''
        Get the ID from the device
        
        Parameters:
            None

        Return:
            str: the full ID string returned from the device
        '''
        cmd = "*IDN?"
        res = self.send(cmd)
        # do something with the returned ID here
        return res

    def dark_mode(self, on: bool = True):
        '''
        Turn on/off the LEDs on the Time Controller Device
        Parameter:
            on (bool): turn the dark mode on (LEDs off)
        '''
        on_str = "OFF" if on else "ON"
        cmd = f"DEVICE:LEDS {on_str}"
        self.send(cmd)
        self.dark = on

    def config_clock(self, ch: int, period: int, count: int=-1, pw: int=0):
        '''
        Configure a clock in a gnerator block

        Parameters:
            ch (int): channel number
            period (int): period of the clock in [ps]
            count (int): number of pulses to send, -1 for infinite / continuous running
            pw (int): pulse width of the clock pulse in [ps]

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

    def play(self, ch: int):
        '''
        Set a generator block into play mode

        Parameters:
            ch (int): Channel number
        '''

        self.send(f"GEN{ch}:PLAY")

    def stop(self, ch: int):
        '''
        Set a generator block into stop mode

        Parameters:
            ch (int): Channel number
        '''
        self.send(f"GEN{ch}:STOP")

    def link(self, ch1: int, ch2: int):
        '''
        Link two generator channels. Channel 2 (servant) will get triggered by Channel 1 (main).

        Parameters:
            ch1 (int): Channel 1 (main)
            ch2 (int): Channel 2 (servant)
        '''
        self.send(f"GEN{ch1}:TRIG:LINK GEN{ch2}")

    def delay(self, ch1: int, delay: int=0):
        '''
        Delay a generator channel with respect to its trigger
        
        Parameters:
            ch1 (int): Channel number
            delay (int): Delay in [ps] wrt the trigger
        '''
        self.send(f"GEN{ch1}:TRIG:DELAY {delay}")
