#!/usr/bin/env python3

import siglent_psu_api.siglent_psu_api as siglent
from cocina.colors import green, red, yellow, dummy

hline = "| " + "-"*20 + " |"

class PowerSupply:
    def __init__(self, name, ip):
        self.name = name
        self.s = siglent.SIGLENT_PSU(ip)
        self.channels = {
            'ch1': siglent.CHANNEL.CH1,
            'ch2': siglent.CHANNEL.CH2,
        }

    def monitor(self):

        status = self.s.system()

        res = {}
        for channel in self.channels:
            res[channel] = {}
            res[channel]['Voltage'] = self.s.measure(ch = self.channels[channel], parameter = siglent.PARAMETER.VOLTAGE)
            res[channel]['Current'] = self.s.measure(ch = self.channels[channel], parameter = siglent.PARAMETER.CURRENT)


        for channel in self.channels:
            print ()
            if status[channel].value == 1: colored = green
            elif status[channel].value == 0: colored = red
            print(colored(hline))
            print(colored( "| {:10}{:10} |".format("Channel", channel) ))
            print(colored( "| {:10}{:10} |".format("Voltage", res[channel]["Voltage"]) ))
            print(colored( "| {:10}{:10} |".format("Current", res[channel]["Current"]) ))
            print(colored(hline))
        #r = self.s.measure(ch = siglent.CHANNEL.CH1, parameter = siglent.PARAMETER.VOLTAGE)
        #print(r)
