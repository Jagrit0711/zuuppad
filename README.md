# Zuuppad
Zuuppad is a 9 key macropad built around the Raspberry Pi Pico.

## Photos

![Zuuppad Photo 1](https://raw.githubusercontent.com/Jagrit0711/zuuppad/main/photos/Screenshot%202026-03-14%20131008.png)

![Zuuppad Photo 2](https://raw.githubusercontent.com/Jagrit0711/zuuppad/main/photos/Screenshot%202026-03-14%20132604.png)

![Zuuppad Photo 3](https://raw.githubusercontent.com/Jagrit0711/zuuppad/main/photos/Screenshot_20260314-144837.png)

## Features
- 9 MX-style mechanical switches in a 3x3 grid
- Raspberry Pi Pico as the brains
- QMK firmware

## CAD Model
In my case the switches and controller are fully visible because it looks cool like that lol. For USB-C there's a pill shaped cutout.

## PCB
Made on KiCad 10. Used 9 MX_PCB_1.00u switch footprints in a clean 3x3 grid. Diodes are DO-35 1N4148, one per key. Also added some random cool stuff on the PCB too.

## Firmware Overview
Uses QMK firmware. 9 keys act as fully remappable macros.

## BOM
- 9x MX-style mechanical switches
- 9x keycaps (1u)
- 9x 1N4148 DO-35 diodes
- 1x Raspberry Pi Pico
- 3x M2x5mm screws
- 1x 3D printed open-top tray
- 1x custom PCB

## Fun Stuff
I made a macropad yay!
