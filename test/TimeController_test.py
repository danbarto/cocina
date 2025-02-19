#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
from cocina.TimeController import TimeController

class TimeControllerTest(unittest.TestCase):

    @patch("cocina.TimeController.SkippyDevice.send")
    def test_all(self, mock_send):
        # Define a return value for the send method
        mock_send.return_value = "123"

        # initialize a tc
        tc = TimeController("123.123.123.123", 5050, "test")
        self.assertTrue(tc.dev)

        # obtain the ID
        res = tc.id()
        self.assertEqual(res, "123")

        # test other methods
        self.assertFalse(tc.dark)
        tc.dark_mode()
        self.assertTrue(tc.dark)
        tc.dark_mode(False)
        self.assertFalse(tc.dark)

        # 24ms period with a 8ms pulse
        tc.config_clock(
            ch = 1,
            period = int(24e9),
            count = -1,
            pw = int(8e9),
        )

        # single pulse of 4ms
        tc.config_clock(
            ch = 2,
            period = int(10e9),
            count = 1,
            pw = int(4e9),
        )
        self.assertEqual(tc.GEN1, 1)
        self.assertEqual(tc.GEN2, 1)

        # link single pulse to continuous clock, add delay of 1ms
        tc.link(2, 1)
        tc.delay(2, int(1e9))

        # start and stop
        tc.play(1)
        tc.stop(1)


        # close tc connection
        tc.close()
        self.assertFalse(tc.dev)
