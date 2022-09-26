# cocina
Tools for an automated lab

Setup:

``` shell
git clone --recursive git@github.com:danbarto/cocina.git
```

`source setup.sh` sets all the necessary paths.

## BU setup

Two Sigilent SPD3303X-E connected to the same switch, subnet 192.168.X.X

Configured IP to 192.168.2.1 for RB supplies, 192.168.2.2 for emulators, subnet mask 255.255.0.0

`lab.py` instantiates the power supplies and prints current status.

## Basic monitoring

`ps1.monitor()` shows the current status of PS1 (RB supply).

`ps1.cycle('ch2')` power cycles channel 2 (combination of `power_down('ch2')` and `power_up('ch2')`)


## Setting parameters

No high level functionality for setting output voltage / current limit is implemented yet.
