#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
from cocina.PowerSupply import PowerSupply

class MyTestCase(unittest.TestCase):

    @patch("cocina.TimeController.SkippyDevice.send")
    def test_all(self, mock_send):
        # Define a return value for the send method
        mock_send.return_value = "16"

        # initialize a tc
        ps = PowerSupply("123.123.123.123", 5050, "test")
        self.assertTrue(ps.dev)

        # other methods
        ps.power_up('ch1')
        res = ps.measure()
        self.assertEqual(res, 16.)

        ps.monitor()
        ps.cycle(channel='ch2')
        ps.power_down('ch1')

        # close tc connection
        ps.close()
        self.assertFalse(ps.dev)
