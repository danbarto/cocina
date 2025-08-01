#!/usr/bin/env python3

from smbus import SMBus
import os
from yaml import load, dump
from yaml import CLoader as Loader, CDumper as Dumper

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

here = os.path.dirname(os.path.abspath(__file__))

class I2C_Device():
    def __init__(self,
                 channel=1,
                 address=0x40,
                 address_table='../address_table/dummy.yaml',
                 register_size=1,
                 debug=False,
                 ):
        self.channel = channel
        self.i2c_adr = address
        self.reg_size = register_size
        self.bus = SMBus(channel)
        self.regs = load_yaml(os.path.join(here, address_table))
        self.debug = debug

    def _swap_endiness(self, word):
        return ((word & 0xFF) << 8) | ((word & 0xFF00) >> 8)  # swap the bytes

    def _read_address(self, adr):
        if self.reg_size == 1:
            return self.bus.read_byte_data(self.i2c_adr, adr)
        elif self.reg_size == 2:
            res = self.bus.read_word_data(self.i2c_adr, adr)
            return self._swap_endiness(res)  # NOTE: swapping is currently hardcoded
        else:
            raise NotImplementedError("Can't read more than 2 bytes currently")

    def _write_address(self, adr, val):
        if self.debug:
            print(f"Writing: {hex(val)} = {bin(val)} = {val} to address {adr}")
        if self.reg_size == 1:
            self.bus.write_byte_data(self.i2c_adr, adr, val)
        elif self.reg_size == 2:
            val = self._swap_endiness(val)
            self.bus.write_word_data(self.i2c_adr, adr, val)
        else:
            raise NotImplementedError("Can't write more than 2 bytes currently")

    def get_adr(self, reg):
        return self.regs[reg]['address']

    def get_mask(self, reg):
        return self.regs[reg]['mask']

    def get_shift(self, reg):
        return ffs(self.get_mask(reg))

    def read(self, reg):
        # NOTE get the address here
        adr = self.get_adr(reg)
        shift = self.get_shift(reg)
        mask = self.get_mask(reg)
        res = self._read_address(adr)
        return (res & mask) >> shift

    def write(self, reg, val):
        # NOTE get the address here
        adr = self.get_adr(reg)
        shift = self.get_shift(reg)
        mask = self.get_mask(reg)
        tmp = self._read_address(adr)
        val_to_write = (val << shift) | (tmp & ~mask)
        self._write_address(adr, val_to_write)

    # NOTE everything below is ADS specific

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
