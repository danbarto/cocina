#!/usr/bin/env python3
'''
Dummy class
'''
from .ZeroMQDevice import ZeroMQDevice

def s_to_ps(time):
    return int(time*1e12)

class ZMQDummy(ZeroMQDevice):

    def __init__(self,
                 name,
                 ip: str,
                 port: int,
                 timeout: int=1,
                 wait: float=0.01,
                 ):
        '''
        Parameters:
            ip (str): IP Address of the device
            port (int): port that is used on the device
            name (str): arbitrary name of the device
        '''

        super().__init__(ip, port, name, timeout, wait)
