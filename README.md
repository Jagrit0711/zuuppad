# Zuup

Zuup is a cicropad is a 9 key macropad built around the Arduino Pro Micro.

## Features
- 9 MX-style mechanical switches in a 3x3 grid  
- xiao-rp2040-dip as the brains  
- circuite python firmware

## Photos

![Zuuppad Photo 1](https://raw.githubusercontent.com/Jagrit0711/zuuppad/main/photos/casetypec.png)

![Zuuppad Photo 2](https://raw.githubusercontent.com/Jagrit0711/zuuppad/main/photos/topview.png)

![Zuuppad Photo 3](https://raw.githubusercontent.com/Jagrit0711/zuuppad/main/photos/kicadpcb.png)

## CAD Model

in my case the switches and controller are fully visible because it looks cool like tht lol  
for usb c there with a pill shaped cutout. i didn't made top panel i have made the bezzle and i am going to manually cut and place a acrylic sheet so that internal components are always visible hence i didn't made a top panel and my pcb is elevated so it doesnt require a plate

## PCB

i made it on KiCad 10. i used 9 MX_PCB_1.00u switch footprints in a clean 3x3 grid. Diodes are DO-35 1N4148, one per key i also aded random usless cool stuff on the pcb too

## Firmware Overview

Uses circuite python firmware.  
9 keys act as fully remappable macros

## BOM

- 9x MX-style mechanical switches  
- 9x keycaps (1u)  
- 9x 1N4148 DO-35 diodes  
- 1x xiao-rp2040-dip  
- 3x M2x5mm screws  
- 1x 3D printed open-top tray  
- 1x PCB i made  

## fun stuff

i made a micropad yay!
