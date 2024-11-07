#!/usr/bin/env python3
# Designed and tested for SDG 6000 series
# User manual: https://siglentna.com/wp-content/uploads/dlm_uploads/2024/08/SDG6000X_UserManual_UM0206X-E01C.pdf
# Programming guide: https://siglentna.com/wp-content/uploads/dlm_uploads/2024/06/SDG_Programming-Guide_PG02-E05C.pdf
#
import socket
import time

from .colors import green, red, yellow, dummy

topline = "┏━" + "━"*20 + "━┓"
botline = "┗━" + "━"*20 + "━┛"

class WaveFormGenerator:
    def __init__(self,
                 name,
                 ip,
                 port=5025,
                 timeout=1,
                 ):

        self.name   = name
        self.ip     = ip
        self.port   = port
        self.channels = ['CH1', 'CH2']
        self.timeout = timeout
        self.connect()
        self.id()
        self.status()

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(self.timeout)
        self.s.connect((self.ip, self.port))

    def send(self, cmd, timeout=2, read=False):
        starttime = time.time()
        while True:
            try:
                self.s.sendall(cmd.encode('utf-8'))
                if read:
                    reply = self.s.recv(4096).decode('utf-8').strip()
                    return reply
                else:
                    return True
            except socket.error:
                time.sleep(0.01)
                self.s.close()
                self.connect()
                if time.time() - starttime > timeout:
                    print ("Send command timed out")
                    break
        return False

    def id(self):
        # identical to "echo "*IDN?" | netcat -q 1 {IP} {PORT}"
        res = self.send('*IDN?', read=True).split(',')
        self.model = res[1]
        self.sn = res[2]
        self.firmware = res[3]
        self.hardware = res[4]

    def status(self):
        res = int(self.send('SYSTEM:STATUS?', read=True), 16)
        self.CH1 = (res >> 4) & 0x1
        self.CH2 = (res >> 5) & 0x1
        
    def reset(self):
        res = self.send('*RST', read=False)
        if res:
            print("Device has been reset")


