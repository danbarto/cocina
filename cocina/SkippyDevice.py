#!/usr/bin/env python3
'''
Parent class for all SCPI devices
'''

import logging
import threading
import time
import socket

class SkippyDevice():
    def __init__(self, ip: str, port: int, name: str = "", timeout: int = 1, wait: int = 0):
        '''
        Initialize a SCPI device, with a default timeout for socket transactions.
        For some (slow?) devices a wait time between send and receive is necessary.

        Parameters:
            ip (str): IP Address of the device
            port (int): port to use for SCPI connection
            name (str): arbitrary name used for the python instance of the device
            timeout (int): timeout of socket transaction in seconds
            wait (int): wait time between after sending a message
        '''

        self.name       = name
        self.ip         = ip
        self.port       = port
        self.dev        = None
        self.timeout    = timeout
        self.wait       = wait

        self.logger     = logging.getLogger(__name__)
        self.lock       = threading.Lock()

        self.connect()

    def connect(self) -> bool:
        '''
        Socket based connection

        Returns:
            bool: True for a successful connection
        '''
        with self.lock:
            self.dev = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.dev.settimeout(self.timeout)
            self.dev.connect((self.ip, self.port))
            #context = zmq.Context()
            #self.dev = context.socket(zmq.REQ)
            #self.dev.connect(f"tcp://{self.ip}:{self.port}")
            self.logger.info(f"Connected to SCPI Device {self.name} @ {self.ip}:{self.port}")
        if self.dev:
            return True
        else:
            return False

    def send(self, msg: str):
        '''
        Send a message to the device

        Parameters:
            msg (str): The message to be sent to the device
        '''
        if not self.dev:
            self.connect()
        self.dev.sendall(f"{msg}\n".encode('utf-8'))
        if self.wait>0:
            time.sleep(self.wait)

    def read(self) -> str:
        '''
        Read response from the device

        Returns:
            str: Response from the device
        '''
        if not self.dev:
            self.connect()
        res = self.dev.recv(4096).decode("utf-8").strip()
        return res

    def query(self, msg:str) -> str:
        '''
        Submit a query to the device

        Parameters:
            msg (str): The message to be sent to the device

        Returns:
            str: Response from the device
        '''
        self.send(msg)
        return self.read()
    
    def close(self):
        '''
        Close the connection to the device
        '''
        with self.lock:
            self.dev.close()
            self.dev = None
            self.logger.info(f"Connection to SCPI Device {self.name} @ {self.ip}:{self.port} closed.")
