#!/bin/bash

ps aux | grep -ie PiClock | awk '{print "sudo kill -9 " $2}' | sh -x
#ps aux | grep -ie RunClock | awk '{print "sudo kill -9 " $2}' | sh -x

sudo python3 ~/PiClock/PiClock.py