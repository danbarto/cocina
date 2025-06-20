#!/usr/bin/env python3
'''
Parent class for all SCPI devices
that somehow don't work with socket
'''

import logging
import threading
import time
import zmq
import numpy as np

class ZeroMQDevice():
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

        self.lstr = f"{self.name} @ {self.ip}:{self.port}"

        self.connect()

    def connect(self) -> bool:
        '''
        Socket based connection

        Returns:
            bool: True for a successful connection
        '''
        with self.lock:
            context = zmq.Context()
            self.dev = context.socket(zmq.REQ)
            #self.dev.settimeout(self.timeout)
            self.dev.connect(f"tcp://{self.ip}:{self.port}")
            #context = zmq.Context()
            #self.dev = context.socket(zmq.REQ)
            #self.dev.connect(f"tcp://{self.ip}:{self.port}")
            self.logger.info(f"{self.lstr}: Connected to SCPI Device")

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
        with self.lock:
            if not self.dev:
                self.logger.debug(f"{self.lstr}: Reconnecting")
                self.connect()
            self.logger.debug(f"{self.lstr}: Sending message: {msg}")
            self.dev.send_string(f"{msg}")
            if self.wait>0:
                time.sleep(self.wait)

    def read(self) -> str:
        '''
        Read response from the device

        Returns:
            str: Response from the device
        '''
        with self.lock:
            if not self.dev:
                self.logger.debug(f"{self.lstr}: Reconnecting")
                self.connect()
            self.logger.debug(f"{self.lstr}: Reading message.")
            res = self.dev.recv().decode("utf-8").strip()
            self.logger.debug(f"{self.lstr}: Received message: {res}")
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

    def write(self, cmd, value, strict=True) -> bool:
        '''
        Function that treats messages without values as commands.
        This is the safe way to write to a device, making sure that transactions were successful.
        NOTE tested, but comparison is very strict.

        Parameters:
            cmd (str): The command to send (i.e., message without the value to write)
            value (any): The value to write
            strict (bool): If true, raise a ValueError if readback does not agree with value

        Returns:
            bool: True if write and readback agree, False otherwise.
        '''
        self.logger.debug(f"{self.lstr}: Writing {value} to {cmd}.")
        self.send(f"{cmd} {value}")
        res = self.query(f"{cmd}?")
        try:
            comp = np.isclose(float(res), float(value))
        except ValueError:
            # if return value is not a number, compare the strings
            comp = (res == str(value))
        if comp:
            self.logger.debug(f"{self.lstr}: Write successful.")
            return True
        else:
            self.logger.debug(f"{self.lstr}: Writing to {cmd} was not successful. Expected {value}, but got {res}.")
            if strict:
                raise ValueError(f"Writing to {cmd} was not successful. Expected {value}, but got {res}.")
            return False

    def close(self):
        '''
        Close the connection to the device
        '''
        with self.lock:
            self.logger.info(f"{self.lstr}: Closing Connection.")
            self.dev.close()
            self.dev = None
            self.logger.info(f"{self.lstr}: Connection to SCPI Device closed.")
