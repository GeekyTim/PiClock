#!/usr/bin/python3

# -----------------------------------------------------------------------------
# Import Libraries
# -----------------------------------------------------------------------------
# -- Standard Libraries
import math
from io import StringIO
import time
from datetime import datetime, timedelta
import threading

from PIL import Image, ImageEnhance

import json
import logging
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# -- My own libraries
from clock import Clock
from ledmatrix import LEDMatrix
from pir_gpio import PIR
from getweatherdata import GetWeatherData
from weather import Weather

# -----------------------------------------------------------------------------
# To check if we're in demo mode (i.e. not home network, IP 192.168.13.117)
#import socket
#import fcntl
#import struct


#def get_interface_ip(ifname):
#    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])


#def get_lan_ip():
#    ip = socket.gethostbyname(socket.gethostname())
#    if ip.startswith("127."):
#        interfaces = [
#            "wlan0",
#            "eth0",
#            "eth1",
#            "eth2",
#            "wlan1",
#            "wifi0",
#            "ath0",
#            "ath1",
#            "ppp0",
#        ]
#        for ifname in interfaces:
#            try:
#                ip = get_interface_ip(ifname)
#                break
#            except IOError:
#                pass

#    return ip


#if (get_lan_ip() == "192.168.13.26"):
#    demodata = []
#    print("Got IP"), demodata
#else:
#    with open('/home/pi/PiClock/demoforecast.json') as demodatafile:
#        demodata = json.load(demodatafile)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Set up Logging defaults
# -----------------------------------------------------------------------------
logging.basicConfig(filename='clock.log', format='%(levelname)s:%(asctime)s:%(funcName)s:%(lineno)d: %(message)s', level=logging.INFO)
logging.info('Starting by defining variables and dictionaries')

# -----------------------------------------------------------------------------
# OpenWeatherMap details
# -----------------------------------------------------------------------------
CityLocation = 2639964  # Potton
WeatherUnits = 'imperial'
WeatherURLFormat = 'http://api.openweathermap.org/data/2.5/forecast?id={}&APPID={}'
OpenWeatherMapKey = '7df1a4b48bacd8bfd001012c1c7878f0'

# -----------------------------------------------------------------------------
# Images
# -----------------------------------------------------------------------------
ImagePath = '/home/pi/PiClock/images/'

# The 'position' dictionaries show the top left and bottom right positions of
# each image within the image

# Small font used for temperature
SmallFontImage = 'smallfont.png'
SmallFontImagePositions = {'1': (0, 0, 4, 7),
                           '2': (5, 0, 9, 7),
                           '3': (10, 0, 14, 7),
                           '4': (15, 0, 19, 7),
                           '5': (20, 0, 24, 7),
                           '6': (25, 0, 29, 7),
                           '7': (30, 0, 34, 7),
                           '8': (35, 0, 39, 7),
                           '9': (40, 0, 44, 7),
                           '0': (45, 0, 49, 7),
                           'max': (50, 0, 54, 7),
                           'min': (55, 0, 59, 7),
                           'C': (60, 0, 64, 7),
                           'F': (65, 0, 69, 7),
                           '.': (70, 0, 72, 7),
                           ':': (73, 0, 75, 7),
                           '-': (76, 0, 78, 7),
                           'sp': (80, 0, 84, 7),
                           'ssp': (80, 0, 82, 7)}

# Clock Font
# The clock needs to contain the following characters:
# 0123456789 :12 ap -
# There is a full space (same size as digits) between 9 and :
# and a small space between 2 and a which is the same width as the 1
ClockFontImage = 'clockfont.png'
ClockImage = Image.open(ImagePath + ClockFontImage)
ClockImagePositions = {0: (0, 0, 6, 15),
                       1: (8, 0, 14, 15),
                       2: (16, 0, 22, 15),
                       3: (24, 0, 30, 15),
                       4: (32, 0, 38, 15),
                       5: (40, 0, 46, 15),
                       6: (48, 0, 54, 15),
                       7: (56, 0, 62, 15),
                       8: (64, 0, 70, 15),
                       9: (72, 0, 78, 15),
                       ' ': (80, 0, 86, 15),
                       ':': (88, 0, 90, 15),
                       ': ': (92, 0, 94, 15),
                       'am': (95, 0, 99, 15),
                       'pm': (100, 0, 104, 15)}

# Weather Icons
# The weather icons are as per the OpenWeatherMap icons on
# http://openweathermap.org/weather-conditions
# They are arranged in a 9x2 grid, daytime icons on the top, nighttime on the bottom
WeatherImage32Name = 'OWMweather.png'
WeatherImage32 = Image.open(ImagePath + WeatherImage32Name)
WeatherImage32Positions = {'01d': (0, 0, 31, 31),
                           '02d': (32, 0, 63, 31),
                           '03d': (64, 0, 95, 31),
                           '04d': (96, 0, 127, 31),
                           '09d': (128, 0, 159, 31),
                           '10d': (160, 0, 191, 31),
                           '11d': (192, 0, 223, 31),
                           '13d': (224, 0, 255, 31),
                           '50d': (256, 0, 287, 31),
                           '01n': (0, 32, 31, 63),
                           '02n': (32, 32, 63, 63),
                           '03n': (64, 32, 95, 63),
                           '04n': (96, 32, 127, 63),
                           '09n': (128, 32, 159, 63),
                           '10n': (160, 32, 191, 63),
                           '11n': (192, 32, 223, 63),
                           '13n': (224, 32, 255, 63),
                           '50n': (256, 32, 287, 63)}

# Small version (16x16) of the weather icons
WeatherImage16Name = 'OWMweather16.png'
WeatherImage16 = Image.open(ImagePath + WeatherImage16Name)
WeatherImage16Positions = {'01d': (0, 0, 15, 15),
                           '02d': (16, 0, 31, 15),
                           '03d': (32, 0, 47, 15),
                           '04d': (48, 0, 63, 15),
                           '09d': (64, 0, 79, 15),
                           '10d': (80, 0, 95, 15),
                           '11d': (96, 0, 111, 15),
                           '13d': (112, 0, 127, 15),
                           '50d': (128, 0, 143, 15),
                           '01n': (0, 16, 15, 31),
                           '02n': (16, 16, 31, 31),
                           '03n': (32, 16, 47, 31),
                           '04n': (48, 16, 63, 31),
                           '09n': (64, 16, 79, 31),
                           '10n': (80, 16, 95, 31),
                           '11n': (96, 16, 111, 31),
                           '13n': (112, 16, 127, 31),
                           '50n': (128, 16, 143, 31)}

# Rain and Snow warning images
# Rain is in 0.5mm divisions, snow is in 1mm
WeatherRainSnowImageName = 'weatherwarn.png'
WeatherRainSnowImage = Image.open(ImagePath + WeatherRainSnowImageName)
WeatherRainSnowPositions = {'RainIcon': (0, 0, 7, 7),
                            'rain0.0': (8, 24, 23, 31),
                            'rain0.5': (8, 0, 8, 7),
                            'rain1.0': (8, 0, 9, 7),
                            'rain1.5': (8, 0, 10, 7),
                            'rain2.0': (8, 0, 11, 7),
                            'rain2.5': (8, 0, 12, 7),
                            'rain3.0': (8, 0, 13, 7),
                            'rain3.5': (8, 0, 14, 7),
                            'rain4.0': (8, 0, 15, 7),
                            'rain4.5': (8, 0, 16, 7),
                            'rain5.0': (8, 0, 17, 7),
                            'rain5.5': (8, 0, 18, 7),
                            'rain6.0': (8, 0, 19, 7),
                            'rain6.5': (8, 0, 20, 7),
                            'rain7.0': (8, 0, 21, 7),
                            'rain7.5': (8, 0, 22, 7),
                            'rain8.0': (8, 0, 23, 7),
                            'SnowIcon': (0, 16, 7, 23),
                            'snow0': (8, 24, 23, 31),
                            'snow1': (8, 16, 8, 23),
                            'snow2': (8, 16, 9, 23),
                            'snow3': (8, 16, 10, 23),
                            'snow4': (8, 16, 11, 23),
                            'snow5': (8, 16, 12, 23),
                            'snow6': (8, 16, 13, 23),
                            'snow7': (8, 16, 14, 23),
                            'snow8': (8, 16, 15, 23),
                            'snow9': (8, 16, 16, 23),
                            'snow10': (8, 16, 17, 23),
                            'snow11': (8, 16, 18, 23),
                            'snow12': (8, 16, 19, 23),
                            'snow13': (8, 16, 20, 23),
                            'snow14': (8, 16, 21, 23),
                            'snow15': (8, 16, 22, 23),
                            'snow16': (8, 16, 23, 23),
                            'blank': (8, 24, 23, 31)}

# Wind warning images (Beaufort Scale)
WeatherWindImageName = 'weatherwarn.png'
WeatherWindImage = Image.open(ImagePath + WeatherWindImageName)
WeatherWindPositions = {'Icon': (0, 8, 7, 15),
                        'blank': (8, 24, 23, 31),
                        0: (8, 24, 23, 31),
                        1: (8, 8, 8, 15),
                        2: (8, 8, 9, 15),
                        3: (8, 8, 10, 15),
                        4: (8, 8, 11, 15),
                        5: (8, 8, 12, 15),
                        6: (8, 8, 13, 15),
                        7: (8, 8, 14, 15),
                        8: (8, 8, 15, 15),
                        9: (8, 8, 16, 15),
                        10: (8, 8, 17, 15),
                        11: (8, 8, 18, 15),
                        12: (8, 8, 19, 15)}

# Day Names
# 0=Monday, 1=Tuesday etc (standard Linux)
DoWImageName = 'DoW.png'
DoWImage = Image.open(ImagePath + DoWImageName)
DoWImagePositions = {0: (0, 8, 16, 15),
                     1: (0, 16, 16, 23),
                     2: (0, 24, 16, 31),
                     3: (0, 32, 16, 39),
                     4: (0, 40, 16, 47),
                     5: (0, 48, 16, 55),
                     6: (0, 0, 16, 7)}

# Month Names
# 1=January etc
MonthImageName = 'months.png'
MonthImage = Image.open(ImagePath + MonthImageName)
MonthImagePositions = {1: (0, 0, 27, 7),
                       2: (0, 8, 27, 15),
                       3: (0, 16, 27, 23),
                       4: (0, 24, 27, 31),
                       5: (0, 32, 27, 39),
                       6: (0, 40, 27, 47),
                       7: (0, 48, 27, 55),
                       8: (0, 56, 27, 63),
                       9: (0, 64, 27, 71),
                       10: (0, 72, 27, 79),
                       11: (0, 80, 27, 87),
                       12: (0, 88, 27, 95)}

# Date font Images
DateImageName = 'datefont.png'
DateImage = Image.open(ImagePath + DateImageName)
DateImagePositions = {'1': (0, 0, 4, 7),
                      '2': (5, 0, 9, 7),
                      '3': (10, 0, 14, 7),
                      '4': (15, 0, 19, 7),
                      '5': (20, 0, 24, 7),
                      '6': (25, 0, 29, 7),
                      '7': (30, 0, 34, 7),
                      '8': (35, 0, 39, 7),
                      '9': (40, 0, 44, 7),
                      '0': (45, 0, 49, 7),
                      'sp': (80, 0, 84, 7)}

# Temperature font Images
TemperatureImageName = SmallFontImage
TemperatureImage = Image.open(ImagePath + TemperatureImageName)
TemperatureImagePositions = SmallFontImagePositions

# The forecast clock
# Shows which 3 hours the forecast covers
WeatherClockImageName = 'clocktimes8.png'
WeatherClockImage = Image.open(ImagePath + WeatherClockImageName)
WeatherClockImagePositions = {0: (0, 0, 7, 7),
                              3: (8, 0, 15, 7),
                              6: (16, 0, 23, 7),
                              9: (24, 0, 31, 7),
                              12: (0, 0, 7, 7),
                              15: (8, 0, 15, 7),
                              18: (16, 0, 23, 7),
                              21: (24, 0, 31, 7)}

# -----------------------------------------------------------------------------
# Delays and various others
# -----------------------------------------------------------------------------
# PIR Delays and values
# Turn the screen off after 'turnscreenoffdelay' seconds of no movement
turnscreenoffdelay = 300
# The pin the PIR output is connected to
pirpin = 25

# The number of seconds between refreshing the weather from the forecast data
refreshweatherinterval = 900
# The number of seconds between changes of the smaller weather displays at the bottom
rotatesmallweatherinterval = 5

# ----------------------------------------------------------------------------------------------------------------------
# Definitions of each canvas
# The format of the 'def' dictionary is:
# 'element':(TopLeftX, TopLeftY, ImageGallery, ImageGalleryPositions)
# ----------------------------------------------------------------------------------------------------------------------
TimeDef = {'Size': (36, 16),
           'Time': (0, 0, ClockImage, ClockImagePositions),
           'AutoDraw': True}

DateDef = {'Size': (28, 16),
           'DoW': (0, 0, DoWImage, DoWImagePositions),
           'Day': (17, 0, DateImage, DateImagePositions),
           'Month': (0, 8, MonthImage, MonthImagePositions),
           'AutoDraw': True}

WeatherDef = {'Size': (64, 32),
              'WeatherIcon': (32, 0, WeatherImage32, WeatherImage32Positions),
              'MaxTemp': (0, 16, TemperatureImage, TemperatureImagePositions),
              'MinTemp': (0, 24, TemperatureImage, TemperatureImagePositions),
              'WindSpeedIcon': (8, 8, WeatherWindImage, WeatherWindPositions),
              'WindSpeed': (16, 8, WeatherWindImage, WeatherWindPositions),
              'RainSnowIcon': (8, 0, WeatherRainSnowImage, WeatherRainSnowPositions),
              'RainSnow': (16, 0, WeatherRainSnowImage, WeatherRainSnowPositions),
              'WeatherTime': (0, 4, WeatherClockImage, WeatherClockImagePositions),
              'AutoDraw': True}

WeatherPlusDef = {'Size': (64, 16),
                  'WeatherIcon': (48, 0, WeatherImage16, WeatherImage16Positions),
                  'MaxTemp': (16, 0, TemperatureImage, TemperatureImagePositions),
                  'MinTemp': (16, 8, TemperatureImage, TemperatureImagePositions),
                  'WindSpeedIcon': (),
                  'WindSpeed': (),
                  'RainSnowIcon': (8, 0, WeatherRainSnowImage, WeatherRainSnowPositions),
                  'RainSnow': (0, 8, WeatherRainSnowImage, WeatherRainSnowPositions),
                  'WeatherTime': (0, 0, WeatherClockImage, WeatherClockImagePositions),
                  'AutoDraw': False}

# -----------------------------------------------------------------------------
# Initialise the PIR Detection class
# -----------------------------------------------------------------------------
#print("initialising PIR")
logging.info('Initialising PIR')
MovementPIR = PIR(0, pirpin, turnscreenoffdelay)

# -----------------------------------------------------------------------------
# Initialise the LEDMatrix class
# Rows and chain length are both required parameters:
# matrix = Adafruit_RGBmatrix(32, 4)  # for the 64 x 32 matrix by 2
# LEDFormat is the real format of each matrix. It assumes all screens are equal size.
#   matrixWidth = Width of the matrix
#   matrixHeight = Height of the matrix
#   matrixCount = Number of screens
#   matrixFlip = Flip the even matrices (1=true)
# -----------------------------------------------------------------------------
LEDFormat = {'matrixRows':32,
             'matrixCols': 64,
             'matrixCount': 2,
             'matrixMapper': "U-mapper;Rotate:180",
             'matrixDriver': "adafruit-hat-pwm"}

logging.info('Initialise Matrix')
MyLEDs = LEDMatrix(LEDFormat)

MatrixPositions = {'Time': (0,0),
                   'Date': (37,0),
                   'WeatherNow': (0,16),
                   'WeatherPlus3': (0, 48),
                   'WeatherPlus6': (0, 48),
                   'WeatherPlus9': (0, 48)}

MovementPIR.pir_set_matrix(MyLEDs)

# -----------------------------------------------------------------------------
# Initialise the Weather Forecast retrieval class
# -----------------------------------------------------------------------------
logging.info('Initialising TheWeather')
TheWeather = GetWeatherData(OpenWeatherMapKey, WeatherURLFormat, CityLocation, WeatherUnits, 3600, 60)

# -----------------------------------------------------------------------------
# Define the Matrix Layout by initialising the Clock and Weather classes
# -----------------------------------------------------------------------------
logging.info('Initialising Time/Date')
Time = Clock(MyLEDs, MatrixPositions['Time'], TimeDef, 12)
Date = Clock(MyLEDs, MatrixPositions['Date'], DateDef, -1)

logging.info('Initialising Weather Now')
WeatherNow = Weather(MyLEDs, MatrixPositions['WeatherNow'], WeatherDef, TheWeather, 0, refreshweatherinterval)
WeatherPlus3 = Weather(MyLEDs, MatrixPositions['WeatherPlus3'], WeatherPlusDef, TheWeather, 3, refreshweatherinterval)
WeatherPlus6 = Weather(MyLEDs, MatrixPositions['WeatherPlus6'], WeatherPlusDef, TheWeather, 6, refreshweatherinterval)
WeatherPlus9 = Weather(MyLEDs, MatrixPositions['WeatherPlus9'], WeatherPlusDef, TheWeather, 9, refreshweatherinterval)

# -----------------------------------------------------------------------------
# Define the threads
# -----------------------------------------------------------------------------
logging.info('Initialising Threads')

GetWeatherThread = threading.Thread(target=TheWeather.get_weather_for_city_thread, args=())
TimeThread = threading.Thread(target=Time.update_time_canvas, args=())
DateThread = threading.Thread(target=Date.update_date_canvas, args=())
WeatherThreadNow = threading.Thread(target=WeatherNow.update_weather_canvas_thread, args=())
WeatherThread3 = threading.Thread(target=WeatherPlus3.update_weather_canvas_thread, args=())
WeatherThread6 = threading.Thread(target=WeatherPlus6.update_weather_canvas_thread, args=())
WeatherThread9 = threading.Thread(target=WeatherPlus9.update_weather_canvas_thread, args=())

RotateWeather = threading.Thread(target=MyLEDs.rotatecanvases, args=([WeatherPlus3, WeatherPlus6, WeatherPlus9], rotatesmallweatherinterval))

PIRThread = threading.Thread(target=MovementPIR.wait_for_no_movement, args=())

# -----------------------------------------------------------------------------
# Start the threads, one at a time, with delays in between to allow them to run.
# -----------------------------------------------------------------------------
logging.info('Starting Threads')

GetWeatherThread.daemon = True
GetWeatherThread.start()

TimeThread.daemon = True
TimeThread.start()
DateThread.daemon = True
DateThread.start()

time.sleep(1)

WeatherThreadNow.daemon = True
WeatherThreadNow.start()
time.sleep(1)
WeatherThread3.daemon = True
WeatherThread3.start()
time.sleep(1)
WeatherThread6.daemon = True
WeatherThread6.start()
time.sleep(1)
WeatherThread9.daemon = True
WeatherThread9.start()
time.sleep(1)

RotateWeather.start()
PIRThread.daemon = True
PIRThread.start()

logging.info('Let`s go loopy!')
print('Let`s go loopy!')
# Forever!
while True:
    time.sleep(3600)