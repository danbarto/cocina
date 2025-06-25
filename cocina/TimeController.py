#!/usr/bin/env python3
'''
Simple class for IDQ Time Tagger
'''
from .ZeroMQDevice import ZeroMQDevice

def s_to_ps(time):
    return int(time*1e12)

class TimeController(ZeroMQDevice):

    def __init__(self,
                 name,
                 ip: str,
                 port: int,
                 timeout: int=1,
                 wait: float=0.01,
                 ):
        '''
        Initialize the TimeController

        Parameters:
            ip (str): IP Address of the device
            port (int): port that is used on the device
            name (str): arbitrary name of the device
        '''

        super().__init__(ip, port, name, timeout, wait)
        #self.id()
        self.dark = False

    def id(self) -> str:
        '''
        Get the ID from the device
        
        Parameters:
            None

        Return:
            str: the full ID string returned from the device
        '''
        cmd = "*IDN?"
        res = self.query(cmd)
        # do something with the returned ID here
        return res

    def dark_mode(self, on: bool = True):
        '''
        Turn on/off the LEDs on the Time Controller Device
        Parameter:
            on (bool): turn the dark mode on (LEDs off)
        '''
        on_str = "OFF" if on else "ON"
        cmd = f"DEVICE:LEDS {on_str}"
        res = self.query(cmd)
        self.dark = on
        return res

    def config_clock(self, ch: int, period: int, count: int=-1, pw: int=0):
        '''
        Configure a clock in a gnerator block

        Parameters:
            ch (int): channel number
            period (int): period of the clock in [ps]
            count (int): number of pulses to send, -1 for infinite / continuous running
            pw (int): pulse width of the clock pulse in [ps]

        '''
        if pw == 0:
            pw = period/2
        if count < 0:
            count = "INF"
        cmd = f"GEN{ch}:enable ON;PNUM {count};PPER {period};PWID {pw}"
        setattr(self, f"GEN{ch}", 1)
        self.query(cmd)

    def config_generator(self,
                         ch: int,
                         period: int,
                         count: int,
                         pw: int,
                         delay: int = 0,
                         link: int = -1,
                         mode: str = "AUTO",
                         ):
        '''
        Create a generator block that produces an output pulse

        Parameters:
            ch (int): Channel number
            period (int): period (separation between pulses) in ps
            count (int): number of pulses
            pw (int): pulse width in ps
            delay (int): delay in ps
            link (int): other generator block to link to
            mode (str): mode AUTO or MANU
        '''
        if link<0:
            link = "NONE"
        else:
            link = f"GEN{link}"
        cmd = f"GEN{ch}:ENAB ON;PNUM {count};PPER {period};PWID {pw};TRIG:DELAY {delay};LINK {link};ARM:MODE {mode}"
        res = self.query(cmd)
        return res

    def config_combiner(self,
                        ch: int,
                        delay: int = 0,
                        link: int = -1,
                        ):
        '''
        Create a timestamp combiner (TSCO) block

        Parameters:
            ch (int): Channel number
            delay (int): delay in ps
            link (int): other generator block to link to
        '''
        if link<0:
            link = "NONE"
        else:
            link = f"GEN{link}"
        cmds = [
            f"TSCO{ch}:WIND:ENAB OFF;BEGI:DELA 0;EDGE RISI;LINK NONE;",
            f"TSCO{ch}:WIND:END:DELA 0;EDGE FALL;LINK NONE;",
            f"TSCO{ch}:FIR:LINK {link};",
            f"TSCO{ch}:SEC:LINK NONE;",
            f"TSCO{ch}:OPIN ONLYFIR;OPOU ONLYFIR;COUN:INTE 1000;MODE CYCL",
        ]
        cmd = ":".join(cmds)
        res = self.query(cmd)
        return res

    def config_output(self,
                      ch: int,
                      enab: bool=True,
                      delay: int = 0,
                      link: int = -1,
                      mode: str = "TTL",
                      ):
        enab_str = "ON" if enab else "OFF"
        if link<0:
            link = "NONE"
        else:
            link = f"TSC{link}"
        cmd = f"OUTP{ch}:ENAB {enab_str};LINK {link};MODE {mode};PULSE OFF;DELAY {delay}"
        res = self.query(cmd)
        return res

    def arm_trigger(self, ch:int):
        '''
        Arm the triger
        '''
        _ = self.query(f"GEN{ch}:TRIG:ARM")

    def play(self, ch: int):
        '''
        Set a generator block into play mode

        Parameters:
            ch (int): Channel number
        '''

        self.query(f"GEN{ch}:PLAY")

    def stop(self, ch: int):
        '''
        Set a generator block into stop mode

        Parameters:
            ch (int): Channel number
        '''
        self.query(f"GEN{ch}:STOP")

    def link(self, ch1: int, ch2: int):
        '''
        Link two generator channels. Channel 2 (servant) will get triggered by Channel 1 (main).

        Parameters:
            ch1 (int): Channel 1 (main)
            ch2 (int): Channel 2 (servant)
        '''
        self.query(f"GEN{ch1}:TRIG:LINK GEN{ch2}")

    def delay(self, ch1: int, delay: int=0):
        '''
        Delay a generator channel with respect to its trigger
        
        Parameters:
            ch1 (int): Channel number
            delay (int): Delay in [ps] wrt the trigger
        '''
        self.query(f"GEN{ch1}:TRIG:DELAY {delay}")

    def config_input(self,
                     channel: int,
                     threshold: float=0.4,
                     int_time: int=1000,
                     ):
        '''
        Configure an input channel

        Parameters:
            channel (int): Channel number
            threshold (float): Discriminator threshold in V
            int_time (int): Integration time for counter in ms
        '''
        _ = self.query(f"INPU{channel}:ENAB")
        _ = self.query(f"INPU{channel}:THRESHOLD {threshold}")
        _ = self.query(f"INPU{channel}:COUN:INTE {int_time}")

    def get_counter(self, channel: int):
        '''
        Read the counter value of an input

        Parameters:
            channel (int): Channel number
        '''
        res = self.query(f"INPU{channel}:COUN?")
        return int(res)


if __name__ == '__main__':

    tc = TimeController("TC", "192.168.10.42", 5555)

    '''
    Generate 3 GEN blocks, GEN3 serves as reference, GEN1 and 2 are linked to GEN3
    GEN1:ENAB ON;PNUM 1;PWID 1000000000000;PPER 1500000000000;TRIG:DELA 0;LINK GEN3;ARM:MODE AUTO
    GEN2:ENAB ON;PNUM 1;PWID 4000000000;PPER 1500000000000;TRIG:DELA 1000000000;LINK GEN3;ARM:MODE AUTO
    GEN3:ENAB ON;PNUM 1;PWID 4000;PPER 2000000000;TRIG:DELA 0;LINK NONE;ARM:MODE MANU
    '''

    # configure reference pulse
    tc.config_generator(ch=3, period=int(2e9), count=1, pw=4000, mode="MANU")
    # configure enable pulses
    tc.config_generator(ch=1, period=s_to_ps(15), count=1, pw=s_to_ps(10), mode="AUTO", link=3)
    tc.config_generator(ch=2, period=s_to_ps(15), count=1, pw=s_to_ps(0.006), delay=s_to_ps(0.001), mode="AUTO", link=3)

    '''
    TSCO9:WIND:ENAB OFF;BEGI:DELA 0;EDGE RISI;LINK NONE;
    TSCO9:WIND:END:DELA 0;EDGE FALL;LINK NONE;
    TSCO9:FIR:LINK GEN1;
    TSCO9:SEC:LINK NONE;
    TSCO9:OPIN ONLYFIR;OPOU ONLYFIR;COUN:INTE 1000;MODE CYCL

    TSCO10:WIND:ENAB OFF;BEGI:DELA 0;EDGE RISI;LINK NONE;
    TSCO10:WIND:END:DELA 0;EDGE FALL;LINK NONE;
    TSCO10:FIR:LINK GEN2;
    TSCO10:SEC:LINK NONE;
    TSCO10:OPIN ONLYFIR;OPOU ONLYFIR;COUN:INTE 1000;MODE CYCL
    '''

    tc.config_combiner(ch=9, link=1)
    tc.config_combiner(ch=10, link=2)

    '''
    OUTP1:ENAB ON;LINK TSCO9;MODE TTL;PULS OFF;DELA 0;PULS:WIDT 1000
    OUTP2:ENAB ON;LINK TSCO10;MODE TTL;PULS OFF;DELA 0;PULS:WIDT 1000
    OUTP3:ENAB ON;LINK TSCO9;MODE TTL;PULS OFF;DELA 0;PULS:WIDT 1000
    OUTP4:ENAB ON;LINK TSCO10;MODE TTL;PULS OFF;DELA 0;PULS:WIDT 1000
    '''

    tc.config_output(ch=1, link=9)
    tc.config_output(ch=2, link=10)
    #tc.config_output(ch=3, link=9)
    #tc.config_output(ch=4, link=10)  # make copies of the signal

    tc.arm_trigger(ch=3)
    tc.play(ch=3)

    # to disable
    tc.stop(1)
