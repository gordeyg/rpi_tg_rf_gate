# General
Python Telegram bot running on RPI which gives ability to open and close through internet RF controllable gate.
Has basic authentication (password protection), so you can change password to rewoke access from those who lost your trust.

Consists of:
* Breadboard
* Some wires
* npn transistor (KSP2222A in my case)
* Raspberry PI (any will fit, we only need one GPIO)
* Remote gate control unit (like this one: https://www.aliexpress.com/item/4000037305642.html. This one easilly works from 60 meters, have not tested further)
* HW button (optional - to enable manual control)

# Dependencies
* Python 2.7
* https://pypi.org/project/RPi.GPIO/
* https://github.com/python-telegram-bot/python-telegram-bot

# Assembly
Preparations:

Extract remote control PCB from case and remove (solder out or gently rip off without damaging PCB) button used for gate opening. Replace it with wires (I have managed to do that without soldering, but don't tell anyone). 
Remote control is marked as IC with two black wires coming from it on scheme.

Legend:
* Gray wire - ground.
* Red wire - GPIO pin. On scheme - GPIO 21, which is hardcoded in script.
* Blue wires - script controlabble circuit. As soon as script will enable GPIO - button on remote control will be triggered.
* Green wires (optional part). Manual control circuit. Replacement for button we have ripped off before in case you still want an ability to pree button physically.

![Wiring scheme](https://github.com/gordeyg/rpi_tg_rf_gate/blob/master/scheme.png "Wiring scheme")

# Usage
1) Replace defaults located in the beginning of script (master password, user password, GPIO port number if needed)
2) Execute script.
