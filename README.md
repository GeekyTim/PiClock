# PiClock v2

The code for this project has been updated to work with the latest matrix drivers.

1 November 2020 - v2 code now that I have learnt a lot more about Python!

## Requirements
The PiClock is a weather display made with:
* A Raspberry Pi model 2 B
* Two AdaFruit 64x32 RGB displays (https://makersify.com/collections/leds/products/adafruit-64x32-rgb-led-matrix-3mm-pitch)
* One Adafruit RGB Matrix HAT + RTC (https://makersify.com/products/adafruit-rgb-matrix-hat-rtc-for-raspberry-pi-mini-kit?variant=1054962589)
* A 30A 5V power supply (Model AD0530-150W)
* A small (10mm) PIR
* A custom designed case (laser cut Perspex and 3D printed parts - files supplied)

Software Required:
* RGB Matrix library: https://github.com/hzeller/rpi-rgb-led-matrix


## Why?
Having organised about 18+ Raspberry Jams in the guise of CamJam (http://camjam.me), including two PiWars (http://piwars.org), two birthday parties on behalf of the Raspberry Pi Foundation and a number of Potton Pi and Pints, and having designed and written the worksheets for the three CamJam EduKits (http://camjam.me/EduKit), I decided it was time finally get round to my own project using the Raspberry Pi.  Having about 75 of them in the house, being used for my 3D printer server, Audio Amp (IQaudIO - http://www.iqaudio.co.uk/), a Plex media server, numerous robots (inc. Diddyborg Metal Edition - https://www.piborg.org/diddyborg/metaledition), Pimoroni Picade (https://shop.pimoroni.com/products/picade), and PiTop (https://www.pi-top.com/) and the ones beloging to CamJam, I needed to build something for myself!

This clock had been in planning for about a year, but with so much going on with CamJam and the Foundation, I just did not get time to do anything.  So I decided to take a break and finish this project.  The main reason was for me to learn Python in more depth that I used for the EduKits.  And Wow, has it been a good learning experience.

## What I have Learnt
This project has taught me the following Python concepts:
* Tuples
* Dictionaries
* Reading files from the Internet
* Converting JSON into Python lists
* Classes and Methods
* Coding and wine/beer doesn't always mix
* Nor does coding and watching Game of Thrones etc.
* Logging
* Threading
* Best Class and Method naming conventions
* Using external files to populate Python dictionaries

##What are the Files
This repository includes the following files:
* PiClock.py - the clock code
* RunClock.sh - A shell script I uses to start the clock
* StopClock.sh - Used to stop all clock threads
The 'images' directory contains images multiple images that I address individually using dictionaries (explained at a later date):
* clockfont.png - All the characters used in the time part of the clock.
* clocktimes8.png - The 3 hour period the weather is being displayed for (to be explained)
* datefont.png - The font used for the date numbers
* DoW.png - The Days of the Week
* months.png - The months of the year
* smallfont.png - A font used in the clock
The PiClock Case directory contaus the files I used for creating the case.
* *.svg for the Perspex case
* *.stl for the various 3d printed parts
