# SMIBHID

## Overview
SMIBHID is the So Make It Bot Human Interface Device and definitely not a mispronunciation of any insults from a popular 90s documentary detailing the activites of the Jupiter Mining Core.

This device run on a Raspberry Pi Pico W and provides physical input and output to humans for the SMIB project; Buttons, LEDs, that sort of thing.

Space_open and Space_closed LEDs show current state (based on last successful state change form this device) and boots with both off.

Press the space_open or space_closed buttons to call the smib server endpoint appropriately. The target state LED will flash to show it's attempting to communicate and confirm successful state update to provide feedback to the user. One of the timeouts I can't work around yet is quite lengthy so expect ~30 seconds of flashing if SMIBHID can't connect to the API webserver. In normal operation the light will simply update immediately.

## Features
- Space open and closed buttons with LED feedback that calls the SMIB space_open endpoint
- LED flashes while trying to set state so you know it's trying to do something

## Circuit diagram
### Pico W Connections
![Circuit diagram](images/SMIBHID%20circuit%20diagram.drawio.png)

### Pico W pinout
![Pico W pinout](images/pico_w_pinout.png)

### Example breadboard build
![Breadboard photo](images/breadboard.jpg)

## Deployment
Copy the files from the smibhib folder into the root of a Pico W running Micropython and update values in config.py as necessary
### Configuration
- Ensure the pins for the space open/closed LEDs and buttons are correctly specified for your wiring
- Populate Wifi SSID and password
- Configure the webserver hostname/IP and port as per your smib.webserver configuration

## Developers
SMIB uses a class abstracted approach running an async loop using the builtin uasyncio, a static copy of the uaiohttpclient for making async requests and my custom logging module.

### Logging
Set the loglevel argument for the HID object in \_\_main\_\_.py for global log level output where: 0 = Disabled, 1 = Critical, 2 = Error, 3 = Warning, 4 = Info

### Adding functionality
Refer to existing space state buttons, lights and watchers as an example for how to implement:
- Create or use an existing (such as button) appropriate module and class with coroutine to watch for input or other appropriate event
- In the HID class
  - instantiate the object instance, passing an asyncio event to the watcher and add the watcher coroutine to the loop
  - Configure another coroutine to watch for the event and take appropriate action on event firing