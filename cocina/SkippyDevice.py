#!/usr/bin/env python3
'''
Parent class for all SCPI devices
'''

import logging
import threading
import zmq
import socket

class SkippyDevice():
    def __init__(self, ip: str, port: int, name: str = ""):

        self.name       = name
        self.ip         = ip
        self.port       = port
        self.dev        = None

        self.logger     = logging.getLogger(__name__)
        self.lock       = threading.Lock()

        self.connect()

    def connect(self) -> bool:
        '''
        ZeroMQ based connection
        '''
        #self.dev = "mock"
        with self.lock:
            context = zmq.Context()
            self.dev = context.socket(zmq.REQ)
            self.dev.connect(f"tcp://{self.ip}:{self.port}")
            self.logger.info(f"Connected to SCPI Device {self.name} @ {self.ip}:{self.port}")
        if self.dev:
            return True
        else:
            return False

    def send(self, msg: str) -> str:
        if not self.dev:
            self.connect()
        self.dev.send_string(msg)
        res = self.dev.recv().decode("utf-8")
        return res

    def close(self):
        with self.lock:
            self.dev.close()
            self.dev = None
            self.logger.info(f"Connection to SCPI Device {self.name} @ {self.ip}:{self.port} closed.")
