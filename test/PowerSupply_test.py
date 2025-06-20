#!/usr/bin/env python3

import unittest
import cocina
from unittest.mock import patch, MagicMock
from cocina.PowerSupply import PowerSupply

class MyTestCase(unittest.TestCase):

    @patch("cocina.SourceMeter.SkippyDevice.connect", return_vale=True)
    @patch("cocina.SourceMeter.SkippyDevice.read", return_value="16")
    @patch("cocina.SourceMeter.SkippyDevice.send", return_value="16")
    def test_all(self, mock_send, mock_read, mock_connect):
        # Define a return value for the send method
        #mock_read.return_value = "16"
        #mock_connect.return_value = "16"
        #mock_send.return_value = "16"

        # initialize a tc
        ps = PowerSupply("123.123.123.123", 5050, "test")
        with patch.object(ps, 'dev', True):
            print(ps.dev)
            self.assertTrue(ps.dev)

        ps.id()
        ps.status()
        ps.set_voltage('ch1', 12)
        ps.set_current('ch1', 0.5)
        # other methods
        ps.power_up('ch1')
        res = ps.measure()
        self.assertEqual(res, 16.)

        with patch.object(ps, 'measure', return_value=12.34):
            ps.monitor()
        ps.cycle(channel='ch2')
        ps.power_down('ch1')

        # close tc connection
        with patch.object(ps, 'close', return_value=None):
            ps.close()
            self.assertFalse(ps.dev)

if __name__ == '__main__':
    unittest.main()
