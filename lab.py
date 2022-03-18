#!/usr/bin/env python3

from cocina.PowerSupply import PowerSupply


if __name__ == '__main__':

    ps1 = PowerSupply("Readout", "192.168.2.1")
    ps2 = PowerSupply("Emulator", "192.168.2.2")

    ps1.monitor()
    ps2.monitor()
