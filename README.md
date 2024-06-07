# cocina
Tools for an automated lab

Install:

``` shell
pip install git+https://github.com/danbarto/cocina.git
```

## BU setup

Several Sigilent SPD3303X-E connected to the same switch, subnet 192.168.X.X, with subnet mask 255.255.0.0

`lab.py` shows an example for how to instantiate the power supplies and print current status.

## Basic monitoring

Load the package and instantiate a Power Supply with a name and IP address.

``` python
from cocina import PowerSupply
psu = PowerSupply("My favorite PSU", "192.168.2.1")
```

A nice print out of the current state of the power supply can be obtained using
``` python
 psu.monitor()
```

Measuring the volgate (in Volt), current (in Ampere) or power (in Watt) on one of the channels using `measure()`, example:

``` python
psu.measure('ch2', 'power')
```


`psu.cycle('ch2')` power cycles channel 2 (combination of `psu.power_down('ch2')` and `psu.power_up('ch2')`)


## Setting parameters

No high level functionality for setting output voltage / current limit is implemented yet.

## Troubleshooting

If UTF encoding is not working properly please set `export PYTHONIOENCODING=utf8`.
