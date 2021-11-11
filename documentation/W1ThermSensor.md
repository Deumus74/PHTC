# W1ThermSensor

## Introduction
This project used Python module from https://github.com/timofurrer/w1thermsensor to speak with thermsensors.

I'm used waterproof 1-Wire DS18B20 sensors.

## Setup
(Excerpt from documentation on https://github.com/timofurrer/w1thermsensor)
On the Raspberry Pi, you will need to add `dtoverlay=w1-gpio"` (for regular connection) or `dtoverlay=w1-gpio,pullup="y"` (for parasitic connection) to your /boot/config.txt. The default data pin is GPIO4 (RaspPi connector pin 7), but that can be changed from 4 to `x` with `dtoverlay=w1-gpio,gpiopin=x`.

After that, don't forget to reboot.

### Hardware-connection


    Raspi VCC (3V3) Pin 1 -----------------------------   VCC    DS18B20
                                                   |
                                                   |
                                                   R1 = 4k7 ...10k
                                                   |
                                                   |
    Raspi GPIO 4    Pin 7 -----------------------------   Data   DS18B20


    Raspi GND       Pin 6 -----------------------------   GND    DS18B20

