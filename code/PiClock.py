#!/usr/bin/python3


from signal import pause
from time import sleep

import RPi.GPIO as GPIO
from clock import Clock
from config_canvases import *
from config_images import *
from config_leddisplay import *
from config_openweathermap import *
from getweatherdata import GetWeatherData
from leddisplay import LEDDisplay
from pir_gpio import PIR
from rotate_canvas import RotateCanvas
from weather import Weather

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# -----------------------------------------------------------------------------
# Delays and various others
# -----------------------------------------------------------------------------
# PIR Delays and values
# Turn the screen off after 'turnscreenoffdelay' seconds of no movement
turnscreenoffdelay = 300

# The pin the PIR output is connected to
pirpin = 25

# The number of seconds between refreshing the weather from the forecast data
refreshweatherinterval = 300

# The number of seconds between changes of the smaller weather displays at the bottom
rotatesmallweatherinterval = 5

# -----------------------------------------------------------------------------
# Initialise the PIR Detection class
# -----------------------------------------------------------------------------
MovementPIR = PIR(pirpin, turnscreenoffdelay)
MovementPIR.start()

# -----------------------------------------------------------------------------
# Initialise the Weather Forecast retrieval class
# -----------------------------------------------------------------------------
TheWeather = GetWeatherData(OpenWeatherMapKey, WeatherURLFormat, CityLocation, WeatherUnits,
                            SecondsBetweenWeatherRefresh, SecondsBetweemWeatherRefreshOnError)
TheWeather.start()
sleep(1)

while not TheWeather.haveforecasts:
    print("Waiting for weather")
    sleep(1)

# -----------------------------------------------------------------------------
# Define the Matrix Layout by initialising the Clock and Weather classes
# -----------------------------------------------------------------------------
Time = Clock(TimeCanvas, 12)
sleep(0.1)
Date = Clock(DateCanvas, -1)
sleep(0.1)

WeatherNow = Weather(WeatherCanvas, 0, refreshweatherinterval, TheWeather)
sleep(0.1)
WeatherPlus3 = Weather(WeatherPlusCanvas, 3, refreshweatherinterval, TheWeather)
sleep(0.1)
WeatherPlus6 = Weather(WeatherPlusCanvas, 6, refreshweatherinterval, TheWeather)
sleep(0.1)
WeatherPlus9 = Weather(WeatherPlusCanvas, 9, refreshweatherinterval, TheWeather)
sleep(0.1)
RotatedView = RotateCanvas((WeatherPlus3, WeatherPlus6, WeatherPlus9), rotatesmallweatherinterval)
sleep(0.1)

Time.start()
sleep(0.1)
Date.start()
sleep(0.1)
WeatherNow.start()
sleep(0.1)
WeatherPlus3.start()
sleep(0.1)
WeatherPlus6.start()
sleep(0.1)
WeatherPlus9.start()
sleep(0.1)
RotatedView.start()
sleep(0.1)

# -----------------------------------------------------------------------------
# Initialise the LEDDisplay
# -----------------------------------------------------------------------------
CanvasPositions["Time"][1] = Time
CanvasPositions["Date"][1] = Date
CanvasPositions["WeatherNow"][1] = WeatherNow
CanvasPositions["RotateWeather"][1] = RotatedView

MyLEDs = LEDDisplay(LEDFormat, CanvasPositions, MovementPIR)
MyLEDs.start()

# Forever!
pause()
