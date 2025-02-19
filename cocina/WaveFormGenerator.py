#!/usr/bin/env python3
# Designed and tested for SDG 6000 series
# User manual: https://siglentna.com/wp-content/uploads/dlm_uploads/2024/08/SDG6000X_UserManual_UM0206X-E01C.pdf
# Programming guide: https://siglentna.com/wp-content/uploads/dlm_uploads/2024/06/SDG_Programming-Guide_PG02-E05C.pdf
# (bad) socket example hinting at necessary wait times between send and receive, as well as port 5024 instead of 5025:
# https://www.siglenteu.com/application-note/programming-example-using-python-to-configure-a-basic-waveform-with-an-sdg-x-series-generator-via-open-sockets-lan/
import socket
import time

from .SkippyDevice import SkippyDevice
from .colors import green, red, yellow, dummy

topline = "┏━" + "━"*20 + "━┓"
botline = "┗━" + "━"*20 + "━┛"

class WaveFormGenerator(SkippyDevice):
    def __init__(self,
                 name,
                 ip,
                 port=5024,
                 timeout=1,
                 wait=0.1,
                 ):
        super().__init__(ip, port, name, timeout, wait)

        self.name   = name
        self.ip     = ip
        self.port   = port
        self.channels = ['CH1', 'CH2']
        self.timeout = timeout
        _ = self.read()
        #print(self.dev.recv(4096).decode('utf-8'))
        self.id()
        #self.status()

    def id(self):
        # identical to "echo "*IDN?" | netcat -q 1 {IP} {PORT}"
        res = self.query('*IDN?').split(',')
        self.model = res[1]
        #self.sn = res[2]
        self.firmware = res[3]
        self.hardware = res[2]

    def get_ip(self):
        res = self.query('SYST:COMM:LAN:IPAD?')
        print(res)

    def set_wave(self):
        '''
        This function is a stub.
        '''
        self.send('C1:BSWV WVTP,SINE')
        self.send('C1:BSWV FRQ,2500')
        self.send('C1:BSWV AMP,2.1')

    def set_pulse(self,
                  channel: int=1,
                  freq: float=0.1,
                  width: float=0.001,
                  amplitude: float=2.8,
                  offset: float=1.4,
                  delay: float=0,
                  period: float=0,
                  ):
        '''
        Configure the Waveform Generator output to generate pulses.
        Parameters:
            channel (int): select channel 1 or 2
            freq (float): frequency of the pulse in Hz
            width (float): width of the pulse in s
            amplitude (float): amplitude peak to peak in V
            offset (float): offset in V (half amp for 0-amp signal)
            delay (float): offset in s
            period (float): period in s, overwrites frequency
        '''
        self.send(f'C{channel}:BSWV WVTP,PULSE')
        if period>0:
            self.send(f'C{channel}:BSWV PERI,{period}')
        else:
            self.send(f'C{channel}:BSWV FRQ,{freq}')
        self.send(f'C{channel}:BSWV WIDTH,{width}')
        self.send(f'C{channel}:BSWV AMP,{amplitude}')
        self.send(f'C{channel}:BSWV OFST,{offset}')
        self.send(f'C{channel}:BSWV DLY,{delay}')

    def set_burst(self,
                  channel: int=1,
                  period: float=5.1,
                  trigger: str='MAN',
                  cycles: int=1,
                  ):
        '''
        Set a channel into burst mode, with a defined number of cycles.
        Parameters:
            channel (int): select channel 1 or 2
            period (float): period in s
            trigger (str): trigger mode, MANual, INTernal, EXTernal
            cycles (int): number of cycles of burst for a single trigger
        '''
        assert trigger in ['MAN', 'EXT', 'INT'], f"Don't know trigger mode {trigger}"
        self.send(f'C{channel}:BTWV STATE,ON')
        self.send(f'C{channel}:BTWV PRD,{period}')
        self.send(f'C{channel}:BTWV TRSR,{trigger}')
        self.send(f'C{channel}:BTWV TIME,{cycles}')


    def send_trigger(self, channel: int=1):
        '''
        Send a manual trigger pulse
        Parameters:
            channel (int): select channel 1 or 2
        '''
        self.send(f'C{channel}:BTWV MTRIG')

    def enable(self, channel: int=1, hiz: bool=True):
        '''
        Enable a channel
        Parameters:
            channel (int): the channel to enable
            hiz (bool): set output to High Z (default) or 50Ohm
        '''
        self.send(f'C{channel}:OUTP ON')
        if hiz:
            self.send(f'C{channel}:OUTP LOAD,HZ')
        else:
            self.send(f'C{channel}:OUTP LOAD,50')

    def disable(self, channel: int=0):
        '''
        Enable a channel
        Parameters:
            channel (int): the channel to enable
        '''
        if channel==0:
            self.send(f'C1:OUTP OFF')
            self.send(f'C2:OUTP OFF')
        else:
            self.send(f'C{channel}:OUTP OFF')

    def status(self):
        res = int(self.query('SYSTEM:STATUS?'))
        #print(res)
        #self.CH1 = (res >> 4) & 0x1
        #self.CH2 = (res >> 5) & 0x1
        
    def reset(self):
        res = self.send('*RST')
        if res:
            self.logger.info(f"{self.lstr}: Device has been reset")


