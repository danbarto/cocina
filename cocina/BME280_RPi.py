#!/usr/bin/env python3
# https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf

from smbus import SMBus
import os
import struct
from yaml import load, dump
from yaml import CLoader as Loader, CDumper as Dumper
from .RPi_I2C_Device import I2C_Device


class BME280(I2C_Device):
    def __init__(self,
                 channel=1,
                 address=0x76,
                 address_table='../address_table/BME280.yaml',
                 register_size=1,
                 debug=False,
                 ):
        super().__init__(channel, address, address_table, register_size, debug)
        self.t_ready = False
        self.h_ready = False
        self.p_ready = False
        self.set_default()

    def set_default(self):
        self.write("OSRS_T", 5)
        self.write("OSRS_H", 5)
        self.write("OSRS_P", 5)
        self.write("MODE", 1)

    def measure(self):
        self.write("MODE", 1)

    def read_temp_coeffs(self):
        for i in range(1,4):
            val = self.read(f"T{i}_LSB") | (self.read(f"T{i}_MSB") << 8)
            if self.regs[f"T{i}_LSB"]['type'] == 'h':  # take care of signed integers
                val = struct.unpack(">h", int.to_bytes(val, 2))[0]
            setattr(self, f"t{i}", val)
        #self.t1 = self.read("T1_LSB") | (self.read("T1_MSB") << 8)
        #self.t2 = self.read("T2_LSB") | (self.read("T2_MSB") << 8)
        #self.t3 = self.read("T3_LSB") | (self.read("T3_MSB") << 8)
        self.t_ready = True

    def read_hum_coeffs(self):
        self.h1 = self.read("H1")

        val = self.read("H2_LSB") | (self.read("H2_MSB") << 8)
        self.h2 = struct.unpack(">h", int.to_bytes(val, 2))[0]

        self.h3 = self.read("H3")

        val = self.read("H4_LSB") | (self.read("H4_MSB") << 4)
        self.h4 = struct.unpack(">h", int.to_bytes(val, 2))[0]

        val = self.read("H5_LSB") | (self.read("H5_MSB") << 4)
        self.h5 = struct.unpack(">h", int.to_bytes(val, 2))[0]

        self.h6 = self.read("H6")
        self.h_ready = True

    def read_pres_coeffs(self):
        for i in range(1,10):
            val = self.read(f"P{i}_LSB") | (self.read(f"P{i}_MSB") << 8)
            if self.regs[f"P{i}_LSB"]['type'] == 'h':
                val = struct.unpack(">h", int.to_bytes(val, 2))[0]
            setattr(self, f"p{i}", val)
        self.p_ready = True

    def read_temp_raw(self):
        self.t = self.read("TEMP_XLSB") | (self.read("TEMP_LSB") << 4) | (self.read("TEMP_MSB") << 12)

    def read_hum_raw(self):
        self.h = self.read("HUM_LSB") | (self.read("HUM_MSB") << 8)

    def read_pres_raw(self):
        self.p = self.read("PRESS_XLSB") | (self.read("PRESS_LSB") << 4) | (self.read("PRESS_MSB") << 12)

    def get_temp(self):
        if not self.t_ready:
            self.read_temp_coeffs()
        self.read_temp_raw()
# ((((adc_T>>3) – ((BME280_S32_t)dig_T1<<1))) * ((BME280_S32_t)dig_T2)) >> 11;
        var1 = (((self.t >> 3) - (self.t1<<1)) * self.t2) >> 11
# (((((adc_T>>4) – ((BME280_S32_t)dig_T1)) * ((adc_T>>4) – ((BME280_S32_t)dig_T1))) >> 12) * ((BME280_S32_t)dig_T3)) >> 14;
        var2 = (((((self.t >> 4) - self.t1) * ((self.t >> 4) - self.t1)) >> 12 ) * self.t3) >> 14
        self.t_fine = var1 + var2
        T = (self.t_fine * 5 + 128) >> 8
        return T/100.

    def get_hum(self):
        if not self.h_ready:
            self.read_hum_coeffs()
        self.read_hum_raw()
        self.get_temp()

        var = self.t_fine - 76800
        # ((((adc_H << 14) – (dig_H4 << 20) – (dig_H5 * v_x1_u32r)) + 16384) >> 15) * (((((((v_x1_u32r * dig_H6) >> 10) * (((v_x1_u32r * dig_H3) >> 11) + 32768)) >> 10) + 2097152) * dig_H2 + 8192) >> 14)
        var = ((((self.h << 14) - (self.h4 << 20) - (self.h5 * var)) + 16384) >> 15) * (((((((var * self.h6) >> 10) * ((( var * self.h3) >> 11) + 32768)) >> 10) + 2097152) * self.h2 + 8192) >> 14)  # wow what a mess
        # v_x1_u32r – (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) * dig_H1) >> 4)
        var = var - (((((var >> 15) * (var >> 15)) >> 7) * self.h1) >> 4)
        if var < 0: var = 0
        if var > 419430400: var = 419430400
        return (var>>12)/1024

    def get_pres(self):
        if not self.p_ready:
            self.read_pres_coeffs()
        self.read_pres_raw()
        self.get_temp()

        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.p6
        var2 = var2 + ((var1*self.p5) << 17)
        var2 = var2 + (self.p4 << 35)
        var1 = ((var1 * var1 * self.p3) >> 8) + ((var1 * self.p2) << 12)
        var1 = ((1 << 47) + var1) * self.p1 >> 33
        if var1 == 0: return 0
        P = 1048576 - self.p
        P = int((((P << 31) - var2) * 3125) / var1)
        var1 = (self.p9 * (P >> 13) * (P >> 13)) >> 25
        var2 = (self.p8 * P) >> 19
        P = ((P + var1 + var2) >> 8) + (self.p7 << 4)
        return P/25600  # result in mbar
