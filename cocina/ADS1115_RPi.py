#!/usr/bin/env python3

from smbus import SMBus
import os
from yaml import load, dump
from yaml import CLoader as Loader, CDumper as Dumper
from .RPi_I2C_Device import I2C_Device

def ffs(x):
    '''
    Returns the index, counting from 0, of the
    least significant set bit in `x`.
    from https://stackoverflow.com/questions/5520655/return-index-of-least-significant-bit-in-python
    There really is no better way!
    '''
    return (x&-x).bit_length()-1

def load_yaml(f_in):
    with open(f_in, 'r') as f:
        res = load(f, Loader=Loader)
    return res

gain = {
    0: 6.144,
    1: 4.096,
    2: 2.048,
    3: 1.024,
    4: 0.512,
    5: 0.256,
    6: 0.256,
    7: 0.256,
}

here = os.path.dirname(os.path.abspath(__file__))

class ADS(I2C_Device):
    def __init__(self,
                 channel=1,
                 address=0x48,
                 address_table='../address_table/ADS1115.yaml',
                 register_size=2,
                 debug=False,
                 ):
        super().__init__(channel, address, address_table, register_size, debug)

    def set_default(self):
        self.write("MODE", 0)
        self.write("MUX", 0x4)

    def get_gain(self):
        return gain[self.read("PGA")]

    def read_voltage(self):
        res = self.read("CONV")
        sign = (res & 0x8000) >> 15
        val = res & 0x7FFF

        if self.debug:
            print(sign, val)
        if sign == 1:
            # negative voltage
            return -(0x7FFF-val)*self.get_gain()/(2**15)
        else:
            return val*self.get_gain()/(2**15)
