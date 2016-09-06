#!/usr/bin/python

# -----------------------------------------------------------------------------
# Import Libraries
# -----------------------------------------------------------------------------
import math
import StringIO
import time
from datetime import datetime, timedelta
import threading
from gpiozero import MotionSensor
from PIL import Image, ImageEnhance
from rgbmatrix import Adafruit_RGBmatrix
from requests import get
import json
import logging

# -----------------------------------------------------------------------------
# To check if we're in demo mode (i.e. not home network, IP 192.168.13.117)
import socket
import fcntl
import struct


def get_interface_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])


def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127."):
        interfaces = [
            "wlan0",
            "eth0",
            "eth1",
            "eth2",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
        ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass

    return ip


if (get_lan_ip() == "192.168.13.117"):
    demodata = []
    print "Got IP", demodata
else:
    with open('/home/pi/PiClock/demoforecast.json') as demodatafile:
        demodata = json.load(demodatafile)

# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Set up Logging defaults
# -----------------------------------------------------------------------------
logging.basicConfig(filename='clock.log', format='%(levelname)s:%(asctime)s:%(funcName)s:%(lineno)d: %(message)s',
                    level=logging.WARNING)

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
ImagePath = 'images/'

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

# The number of seconds between refreshign the weather from the forecast data
refreshweatherinterval = 900
# The number of seconds between changes of the smaller weather displays at the bottom
rotatesmallweatherinterval = 5

# ----------------------------------------------------------------------------------------------------------------------
# Definitions of each canvas
# The format of the 'def' dictioanry is:
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


# *****************************************************************************
# Classes
# *****************************************************************************

# #############################################################################
# Class: GetWeatherData
# Single thread that retrieves the weather from OpenWeatherMap.org and the
# defined frequency and stored in __weatherdatadict
# #############################################################################
class GetWeatherData:
    def __init__(self, cityid, units, frequency, errorfrequency, demodata):
        # logging.info('Creating CetWeatherData instance')
        self.__cityid = cityid
        self.__units = units
        self.__refreshfrequency = frequency
        self.__errorfrequency = errorfrequency
        self.__demodata = demodata

        self.__weatherdatadict = []

    # -------------------------------------------------------------------------
    # Method runs as a thread, retrieving the weather from OpenWeatherMap.org
    # -------------------------------------------------------------------------
    def get_weather_for_city_thread(self):
        while True:
            try:
                # logging.info('Getting Weather data')
                if (self.__demodata == []):
                    weatherdata = get(WeatherURLFormat.format(self.__cityid, OpenWeatherMapKey))
                    self.__weatherdatadict = weatherdata.json()
                    print "Real Weather"
                else:
                    self.__weatherdatadict = self.__demodata
                    print "Demo Data"

                sleeptime = self.__refreshfrequency
            except:
                # logging.warning('Error in get_weather_for_city_thread')
                sleeptime = self.__errorfrequency

            time.sleep(sleeptime)

    # -------------------------------------------------------------------------
    # read_forecast_for_date
    # Reads the weather forecast for the time weather_forecast_time from
    # __weatherdatadict
    # -------------------------------------------------------------------------
    def read_forecast_for_date(self, weather_forecast_time):
        try:
            # logging.info('Reading weather forecast')
            currentweather = self.__weatherdatadict
            for weatherdata in currentweather['list']:
                if weatherdata['dt_txt'] == weather_forecast_time:
                    return weatherdata
            return {}
        except:
            # logging.warning('Error read_forecast_for_date(%s)', weather_forecast_time)
            return {}

    # -------------------------------------------------------------------------
    # get_readable_forecast
    # Converts the weather for the defined time (weather_forecast_time) into a
    # readable (list) format
    # -------------------------------------------------------------------------
    def get_readable_forecast(self, weather_forecast_time):
        # logging.info('Putting the weather in readable format')
        weatherdata = {}
        weatherdict = self.read_forecast_for_date(weather_forecast_time)
        if weatherdict == {}:
            # logging.warning('The json was blank!')
            return {}
        try:
            # weatherdata['cloudiness'] = weatherdict['clouds']['all']
            # weatherdata['CurrentTemp'] = round(float(weatherdict['main']['temp']) - 273.0, 1)
            weatherdata['MaxTemp'] = self.kelvin_to_celcius(weatherdict['main']['temp_max'])
            weatherdata['MinTemp'] = self.kelvin_to_celcius(weatherdict['main']['temp_min'])
            weatherdata['humidity'] = int(weatherdict['main']['humidity'])

            # If [rain][3h] is in the forecast, set it, or set rainfall to 0mm
            if 'rain' in weatherdict:
                if '3h' in weatherdict['rain']:
                    weatherdata['rain'] = min(8.0, math.ceil(float(weatherdict['rain']['3h'] * 2)) / 2.0)
                else:
                    weatherdata['rain'] = 0.0
            else:
                weatherdata['rain'] = 0.0

            if 'snow' in weatherdict:
                if '3h' in weatherdict['snow']:
                    weatherdata['snow'] = min(16, int(math.ceil(float(weatherdict['snow']['3h']))))
                else:
                    weatherdata['snow'] = 0
            else:
                weatherdata['snow'] = -1

            weatherdata['description'] = weatherdict['weather'][0]['description']
            weatherdata['wind'] = float(weatherdict['wind']['speed'])
            weatherdata['beaufort'] = self.windspeed_to_beaufort(float(weatherdict['wind']['speed']))
            weatherdata['winddir'] = self.degrees_to_direction(float(weatherdict['wind']['deg']))
            weatherdata['icon'] = weatherdict['weather'][0]['icon']
            weatherdata['WeatherTime'] = time.strptime(weatherdict['dt_txt'], '%Y-%m-%d %H:%M:%S').tm_hour
            weatherdata['dt_txt'] = weatherdict['dt_txt']

            return weatherdata
        except:
            # logging.warning('Error get_readable_forecast')
            return {}

    # -------------------------------------------------------------------------
    # kelvin_to_celcius
    # Converts the temperature from Kelvins to celcius
    # -------------------------------------------------------------------------
    def kelvin_to_celcius(self, kelvin):
        return round(float(kelvin) - 273.15, 1)

    # -------------------------------------------------------------------------
    # windspeed_to_beaufort
    # Converts the wind speed from m/s to Beaufort scale
    # -------------------------------------------------------------------------
    def windspeed_to_beaufort(self, windspeedmps):
        beaufort = 0

        if windspeedmps <= 2.0:
            beaufort = 1
        elif windspeedmps <= 3.0:
            beaufort = 2
        elif windspeedmps <= 5.0:
            beaufort = 3
        elif windspeedmps <= 8.0:
            beaufort = 4
        elif windspeedmps <= 11.0:
            beaufort = 5
        elif windspeedmps <= 14.0:
            beaufort = 6
        elif windspeedmps <= 17.0:
            beaufort = 7
        elif windspeedmps <= 21.0:
            beaufort = 8
        elif windspeedmps <= 24.0:
            beaufort = 9
        elif windspeedmps <= 28.0:
            beaufort = 10
        elif windspeedmps <= 32.0:
            beaufort = 11
        elif windspeedmps > 32.0:
            beaufort = 12

        return beaufort

    # -------------------------------------------------------------------------
    # degrees_to_direction
    # Convert the wind direction from degrees to compass direction
    # -------------------------------------------------------------------------
    def degrees_to_direction(self, degrees):
        try:
            degrees = float(degrees)
        except ValueError:
            return None

        if degrees < 0 or degrees > 360:
            return None

        if degrees <= 11.25 or degrees >= 348.76:
            return "N"
        elif degrees <= 33.75:
            return "NNE"
        elif degrees <= 56.25:
            return "NE"
        elif degrees <= 78.75:
            return "ENE"
        elif degrees <= 101.25:
            return "E"
        elif degrees <= 123.75:
            return "ESE"
        elif degrees <= 146.25:
            return "SE"
        elif degrees <= 168.75:
            return "SSE"
        elif degrees <= 191.25:
            return "S"
        elif degrees <= 213.75:
            return "SSW"
        elif degrees <= 236.25:
            return "SW"
        elif degrees <= 258.75:
            return "WSW"
        elif degrees <= 281.25:
            return "W"
        elif degrees <= 303.75:
            return "WNW"
        elif degrees <= 326.25:
            return "NW"
        elif degrees <= 348.75:
            return "NNW"
        else:
            return None


# #############################################################################
# Class: Canvas
# An image canvas onto which images are drawn on and stored before being drawn
# on the LEDMatrix
# #############################################################################
class Canvas:
    def __init__(self, canvassize):
        # logging.info('Creating new Canvas instance')
        # Create a new canvas of size (x, y)
        self.Image = Image.new('RGB', canvassize)

    # -------------------------------------------------------------------------
    # extract_image_from_gallery
    # Extract an image from a 'gallery' image
    # galleryimage is a single image containing all the images
    # gallerypositions contains the locations of the images in galleryimage
    # -------------------------------------------------------------------------
    def extract_image_from_gallery(self, galleryimage, gallerypositions):
        # Now get the image from file (no error checking yet!)
        singleimagebox = (gallerypositions[0], gallerypositions[1],
                          gallerypositions[2] + 1, gallerypositions[3] + 1)
        singleimage = galleryimage.crop(singleimagebox)
        singleimage.load()

        return singleimage

    # -------------------------------------------------------------------------
    # draw_on_canvas
    # Draw an image on the canvas
    # imagedata is a tuple containing:
    #     (X position, Y position, ImageGalery, ImageGaleryPositions)
    # whichimage is the sub-image contained in the ImageGalery
    # -------------------------------------------------------------------------
    def draw_on_canvas(self, imagedata, whichimage):
        # The start/end in the image within imagedata
        imagexstart = imagedata[0]
        imageystart = imagedata[1]
        imagegallery = imagedata[2]
        imagegallerypositions = imagedata[3]

        imagexsize = imagegallerypositions[whichimage][2] - imagegallerypositions[whichimage][0] + 1
        imageysize = imagegallerypositions[whichimage][3] - imagegallerypositions[whichimage][1] + 1
        imagexend = imagexstart + imagexsize - 1
        imageyend = imageystart + imageysize - 1

        # If the image is off the canvas, don't draw any of it
        if imagexstart > self.Image.size[0] or imageystart > self.Image.size[1] or imagexend < 0 or imageyend < 0:
            return

        # Extract the sub-image from the ImageGallery (imagedata[2])
        croppedimage = self.extract_image_from_gallery(imagegallery, imagegallerypositions[whichimage])
        self.Image.paste(croppedimage, (imagexstart, imageystart))


# #############################################################################
# Class: LEDMatrix
# Creates an LED Matrix Canvas onto which the time and weather canvases can be
# pasted.
# The matrix is made from chained matricees, so this class converts between
# the Matrix canvas and the actual way required to be displayed correctly.
# #############################################################################
class LEDMatrix:
    def __init__(self, xsize, chainlength, ledxsize, ledysize):
        LEDMatrix.matrix = Adafruit_RGBmatrix(xsize, chainlength)
        LEDMatrix.matrix.Clear()

        self.__MatrixID = LEDMatrix

        self.__LEDXSize = ledxsize
        self.__LEDYSize = ledysize

        self.__LEDXMax = ledxsize - 1
        self.__LEDYMax = ledysize - 1

        self.__LEDRealX = ledxsize * 2
        self.__LEDYSplit = int((ledysize / 2) - 1)

        self.__DrawOnMatrix = True

        self.__MatrixCanvas = Canvas((self.__LEDXSize, self.__LEDYSize))
        self.__FadeMatrixCanvas = Canvas((self.__LEDXSize, self.__LEDYSize))

    # -------------------------------------------------------------------------
    # set_draw_on_matrix
    # Set whether to draw on the matrix of keep it blank, fading between the
    # states
    # -------------------------------------------------------------------------
    def set_draw_on_matrix(self, draw_on_matrix):
        if draw_on_matrix:
            self.fade_matrix_canvas(0, 10, 1)
            self.__DrawOnMatrix = True
        else:
            self.__DrawOnMatrix = False
            self.fade_matrix_canvas(10, 0, -1)

    # -------------------------------------------------------------------------
    # fade_matrix_canvas
    # Fade the Matrix canvas between states 'on' and 'off'
    # -------------------------------------------------------------------------
    def fade_matrix_canvas(self, start, end, step):
        fadeimage = ImageEnhance.Brightness(self.__MatrixCanvas.Image)
        for factor in range(start, (end + step), step):
            fadedimage = fadeimage.enhance(factor / 10.0)
            self.__FadeMatrixCanvas.Image.paste(fadedimage)
            LEDMatrix.paste_canvas_to_matrix(self, (0, 0), self.__FadeMatrixCanvas, True)
            time.sleep(0.1)

    # -------------------------------------------------------------------------
    # convertxy
    # Convert the x,y coordinates from 128x32 to 64x64
    # Chaining two 64x64 screens together produces a 128x32 screen:
    # -------------------
    # | 63x32  | 64x32  |
    # -------------------
    # But is arranged one on top of the other:
    # ----------
    # | 64x32  | ->
    # ----------   | Flips over second screen
    # | 64x32  | <-
    # ----------
    # Therefore we need to convert the 128x32 coordinates to make the second
    # screen appear below the first.
    # We will also take the opportunity to limit x and y to be below 63.
    # Negative x & y are allowed so that images can be drawn off the top and
    # left edges
    # -------------------------------------------------------------------------
    def convertxy(self, x, y):
        if y > self.__LEDYSize:
            y1 = y
            x1 = x
        elif 0 <= y < self.__LEDYSplit:
            y1 = y
            if x > self.__LEDXMax:
                x1 = self.__LEDRealX
            else:
                x1 = x
        elif self.__LEDYSplit < y <= self.__LEDYMax:
            y1 = self.__LEDYMax - y
            if x > self.__LEDXMax:
                x1 = self.__LEDRealX
            else:
                x1 = self.__LEDRealX - 1 - x
        else:
            y1 = y
            if x > self.__LEDXMax:
                x1 = self.__LEDRealX
            else:
                x1 = x

        return (x1, y1)

    # -------------------------------------------------------------------------
    # paste_to_matrix_canvas
    # Pastes another canvas (weather or time) to the Matrix canvas, and then
    # the Matrix Canvas to the LED Matrix itself
    # -------------------------------------------------------------------------
    def paste_to_matrix_canvas(self, canvasposition, canvasimage):
        canvasimagexstart = canvasposition[0]
        canvasimageystart = canvasposition[1]
        canvasimagexsize = canvasimage.Image.size[0]
        canvasimageysize = canvasimage.Image.size[1]
        canvasimagexend = canvasimagexstart + canvasimagexsize - 1
        canvasimageyend = canvasimageystart + canvasimageysize - 1

        # If the image is off the screen, don't draw any of it
        if canvasimagexstart > self.__LEDXMax or canvasimageystart > self.__LEDYMax \
                or canvasimagexend < 0 or canvasimageyend < 0:
            return

        # Create a crop box to stop the canvas exceeding off the Matrix Canvas area
        imagebox = (0, 0, min(self.__LEDXSize - canvasimagexstart, canvasimagexsize),
                    min(self.__LEDYSize - canvasimageystart, canvasimageysize))
        imagetopaste = canvasimage.Image.crop(imagebox)
        imagetopaste.load()

        # Paste the imagetopaste to the Matrix Canvas
        self.__MatrixCanvas.Image.paste(imagetopaste, box=(canvasimagexstart, canvasimageystart))

        # Display the Matrix Canvas on the LED Matrix
        self.paste_canvas_to_matrix((0, 0), self.__MatrixCanvas, False)

    # -------------------------------------------------------------------------
    # paste_canvas_to_matrix
    # Split the image in two before pasting to the LED matrix
    # This is so that it appears correctly on the 64x64 matrix, which is
    # actually a 128x32 matrix
    # Parameters:
    # positioninmatrix = (x,y) - Tuple of the image top left position
    # canvasimage = The image to paste to the matrix
    # -------------------------------------------------------------------------
    def paste_canvas_to_matrix(self, positioninmatrix, canvasimage, drawoverride):
        if self.__DrawOnMatrix or drawoverride:
            ledimagexstart = positioninmatrix[0]
            ledimageystart = positioninmatrix[1]
            ledimagexsize = canvasimage.Image.size[0]
            ledimageysize = canvasimage.Image.size[1]
            ledimagexend = ledimagexstart + ledimagexsize - 1
            ledimageyend = ledimageystart + ledimageysize - 1

            # If the image is off the screen, don't draw any of it
            if ledimagexstart > self.__LEDXMax or ledimageystart > self.__LEDYMax or ledimagexend < 0 or ledimageyend < 0:
                return

            # Draw the image in the top part of the screen, if there is any
            if ledimageystart <= self.__LEDYSplit:
                # Crop it to the top half of the screen
                topimagebox = (0, 0, min(self.__LEDXSize - ledimagexstart, ledimagexsize),
                               min(self.__LEDYSplit + 1 - ledimageystart, ledimageysize))
                topimage = canvasimage.Image.crop(topimagebox)
                topimage.load()

                # Convert iX, iY into LED coordinates
                ledimagexy = self.convertxy(ledimagexstart, ledimageystart)
                # Draw the top image
                LEDMatrix.matrix.SetImage(topimage.im.id, ledimagexy[0], ledimagexy[1])

            # Draw the image in the bot6tom part of the screen, if there is any
            if ledimageyend > self.__LEDYSplit:
                # Crop it to the bottom half of the screen
                bottomimagestarty = ledimageyend - self.__LEDYSplit
                bottomimagebox = (0, min(self.__LEDYSplit + 1 - ledimageystart, ledimageysize), ledimagexsize,
                                  ledimageysize)
                bottomimage = canvasimage.Image.crop(bottomimagebox)
                bottomimage.load()
                bottomimage = bottomimage.rotate(180)
                bottomimage.load()

                # Convert the position of the bottom image to LED coordinates
                ledimagexy = self.convertxy(ledimagexend, ledimageyend)

                # Draw the bottom image
                LEDMatrix.matrix.SetImage(bottomimage.im.id, ledimagexy[0], ledimagexy[1])

    # -------------------------------------------------------------------------
    # rotatecanvases
    # Swaps the canvases listed in canvaslist every rotateinterval seconds
    # -------------------------------------------------------------------------
    def rotatecanvases(self, canvaslist, rotateinterval):
        canvascount = len(canvaslist)
        canvas = 0
        while True:
            self.paste_to_matrix_canvas(canvaslist[canvas].get_canvas_matrix_position(),
                                        canvaslist[canvas].get_weather_canvas())
            canvas = (canvas + 1) % canvascount
            time.sleep(rotateinterval)


# #############################################################################
# Class: Clock
# Draws the date and/or time on a canvases, and then those canvases to the
# Matrix (matrixobject).
# positioninmatrix is the position of the clock canvas in the matrix canvas
# clockdefinition is the definition of what should be in the clock (Time, DoW,
# Month or Day(date))
# clock1224 = 12 for 12 hour clock, or 24 for 24 hour clock
# #############################################################################
class Clock:
    def __init__(self, matrixobject, positioninmatrix, clockdefinition, clock1224):
        logging.info('Creating new Clock instance')
        self.__Matrix = matrixobject
        self.__MatrixPosition = positioninmatrix
        self.__ClockDefinition = clockdefinition
        self.__Clock24h = clock1224

        self.__ClockCanvas = Canvas(clockdefinition['Size'])
        self.__ImageChanged = True

        self.__CurrentHour = -1
        self.__CurrentMinute = -1
        self.__CurrentSecond = -1
        self.__CurrentDay = -1
        self.__CurrentMonth = -1
        self.__CurrentDoW = -1

    # -------------------------------------------------------------------------
    # update_time_canvas
    # Update the time every second. The time can be 12h or 24h
    # -------------------------------------------------------------------------
    def update_time_canvas(self):
        while True:
            delay = 1.0
            if 'Time' in self.__ClockDefinition:
                if self.__ClockDefinition['Time'] != {}:
                    self.draw_time()
                    delay = 1.0 - float(time.time() % 1)
            time.sleep(delay)

    # -------------------------------------------------------------------------
    # update_date_canvas
    # Updates the date every day
    # -------------------------------------------------------------------------
    def update_date_canvas(self):
        while True:
            todaysdate = datetime.today()
            datedow = todaysdate.weekday()
            datemonth = todaysdate.month
            dateday = todaysdate.day

            if 'DoW' in self.__ClockDefinition:
                if self.__ClockDefinition['DoW'] != {}:
                    if self.__CurrentDoW != datedow:
                        self.__CurrentDoW = datedow
                        self.__ImageChanged = True
                        self.__ClockCanvas.draw_on_canvas(self.__ClockDefinition['DoW'], self.__CurrentDoW)

            if 'Day' in self.__ClockDefinition:
                if self.__ClockDefinition['Day'] != {}:
                    if self.__CurrentDay != dateday:
                        self.__CurrentDay = dateday
                        self.__ImageChanged = True
                        self.draw_day()

            if 'Month' in self.__ClockDefinition:
                if self.__ClockDefinition['Month'] != {}:
                    if self.__CurrentMonth != datemonth:
                        self.__CurrentMonth = datemonth
                        self.__ImageChanged = True
                        self.__ClockCanvas.draw_on_canvas(self.__ClockDefinition['Month'], self.__CurrentMonth)

            if self.__ClockDefinition['AutoDraw']:
                self.draw_on_matrix_canvas()

            # Calculate the number of seconds until midnight and wait for then
            secondstomidnight = (datetime.now().replace(hour=0, minute=0, second=0,
                                                        microsecond=0) + timedelta(days=1)) - datetime.now()
            time.sleep(secondstomidnight.total_seconds())

    # ----------------------------------------------------------------------------------
    # draw_clock_digit
    # Draw an individual clock digit at the pre-defined position (x, y) tuple
    # ----------------------------------------------------------------------------------
    def draw_clock_digit(self, position, digit):
        self.__ClockCanvas.draw_on_canvas(
            (position[0], position[1], self.__ClockDefinition['Time'][2], self.__ClockDefinition['Time'][3]),
            digit)

    # -------------------------------------------------------------------------
    # add_image_width
    # Increase x by a defined width
    # -------------------------------------------------------------------------
    def add_image_width(self, x, imagedef):
        return x + imagedef[2] - imagedef[0] + 1

    # ----------------------------------------------------------------------------------
    # draw_day
    # Update the day (date), consisting of a one or two digit number
    # ----------------------------------------------------------------------------------
    def draw_day(self):
        x = self.__ClockDefinition['Day'][0]
        y = self.__ClockDefinition['Day'][1]
        image = self.__ClockDefinition['Day'][2]
        imagedefinition = self.__ClockDefinition['Day'][3]

        # 10's digit
        if self.__CurrentDay >= 10.0:
            tensdigit = str(abs(int(self.__CurrentDay)))[0]
            self.__ClockCanvas.draw_on_canvas((x, y, image, imagedefinition), tensdigit)
            x = self.add_image_width(x, imagedefinition[tensdigit])
        else:
            tensdigit = 0
            self.__ClockCanvas.draw_on_canvas((x, y, image, imagedefinition), 'sp')
            x = self.add_image_width(x, imagedefinition['sp'])

        # Units digit
        unitdigit = str(abs(int(self.__CurrentDay)) - (int(tensdigit) * 10))
        self.__ClockCanvas.draw_on_canvas((x, y, image, imagedefinition), unitdigit)

    # ----------------------------------------------------------------------------------
    # draw_time
    # Update the time display, hh:mm a/p
    # ----------------------------------------------------------------------------------
    def draw_time(self):
        x = self.__ClockDefinition['Time'][0]
        y = self.__ClockDefinition['Time'][1]
        image = self.__ClockDefinition['Time'][2]
        imagedefinition = self.__ClockDefinition['Time'][3]

        self.__ImageChanged = False

        # The font is assumed to be non-proportional for all but the : and am/pm
        # Calculate the positions of the various items
        xhourtens = x
        xhourunits = self.add_image_width(xhourtens, imagedefinition[1])
        xcolon = self.add_image_width(xhourunits, imagedefinition[1])
        xminutetens = self.add_image_width(xcolon, imagedefinition[':'])
        xminuteunits = self.add_image_width(xminutetens, imagedefinition[1])
        xampm = self.add_image_width(xminuteunits, imagedefinition[1])

        # Get the current hour
        currenttime = time.localtime()

        # Only update the hour if it has changed
        if currenttime.tm_hour != self.__CurrentHour:
            self.__ImageChanged = True
            self.__CurrentHour = currenttime.tm_hour
            if self.__Clock24h == 12:
                # Change to 12 hour clock
                if currenttime.tm_hour > 12:
                    hour = self.__CurrentHour - 12
                    ampm = 1
                else:
                    hour = self.__CurrentHour
                    ampm = 0
            else:
                # 24 hour
                hour = self.__CurrentHour
                ampm = -1

            # Draw the hours - first digit
            if hour >= 20:
                firstdigit = 2
                seconddigit = hour - 20
            elif hour >= 10:
                firstdigit = 1
                seconddigit = hour - 10
            else:
                firstdigit = ' '
                seconddigit = hour

            # Draw the first digit
            self.draw_clock_digit((xhourtens, y), firstdigit)
            # Draw the second digit
            self.draw_clock_digit((xhourunits, y), seconddigit)

            # Draw AM/PM
            if ampm == 0:
                self.draw_clock_digit((xampm, y), 'am')
            elif ampm == 1:
                self.draw_clock_digit((xampm, y), 'pm')

        # Draw the : flashing each second
        if currenttime.tm_sec != self.__CurrentSecond:
            self.__ImageChanged = True
            self.__CurrentSecond = currenttime.tm_sec
            if self.__CurrentSecond / 2.0 == int(self.__CurrentSecond / 2):
                self.draw_clock_digit((xcolon, y), ':')
            else:
                self.draw_clock_digit((xcolon, y), ': ')

        # Only update the minutes if they have changed
        if currenttime.tm_min != self.__CurrentMinute:
            self.__ImageChanged = True
            self.__CurrentMinute = currenttime.tm_min

            minute = self.__CurrentMinute
            if self.__CurrentMinute < 10:
                minute_firstdigit = 0
                minute_seconddigit = self.__CurrentMinute
            else:
                minute_firstdigit = int(str(self.__CurrentMinute)[0])
                minute_seconddigit = int(str(self.__CurrentMinute)[1])

            self.draw_clock_digit((xminutetens, y), minute_firstdigit)
            self.draw_clock_digit((xminuteunits, y), minute_seconddigit)

        self.draw_on_matrix_canvas()

    # ----------------------------------------------------------------------------------
    # draw_on_matrix_canvas
    # If the canvas has changed, draw it on the
    # ----------------------------------------------------------------------------------
    def draw_on_matrix_canvas(self):
        # Only draw on matrix canvas if AutoDraw is set to True, and the image has changed
        if self.__ClockDefinition['AutoDraw']:
            if self.__ImageChanged:
                self.__Matrix.paste_to_matrix_canvas(self.__MatrixPosition, self.__ClockCanvas)
                self.__ImageChanged = False


# #############################################################################
# The Weather class
# Updates the weather conditions from the Weather file, and updates the screen 
# when necessary.
# Only updates every UpdateInterval (seconds), or 10 minutes if there is an 
# error
# #############################################################################
class Weather:
    def __init__(self, matrixobject, positioninmatrix, weatherdefinition, hours_from_now, update_interval):
        logging.info('Creating new Weather instnace')
        self.__Matrix = matrixobject
        self.__MatrixPosition = positioninmatrix
        self.__WeatherDefinition = weatherdefinition
        self.__HoursFromNow = hours_from_now
        self.__UpdateInterval = update_interval

        self.__WeatherCanvas = Canvas(weatherdefinition['Size'])
        self.__ImageChanged = True

        self.__WeatherForecast = {}
        self.__CurrentWeatherIcon = ''
        self.__CurrentWeatherWind = -1
        self.__CurrentWeatherRain = -1.0
        self.__CurrentWeatherSnow = -1.0
        self.__CurrentWeatherMaxTemp = 999.0
        self.__CurrentWeatherMinTemp = -999.0
        self.__CurrentWeatherTime = -1
        self.__WeatherReadError = False
        self.__LastUpdateTime = 0
        self.__WindSpeedIcon = -1
        self.__RainSnowIcon = ''

    # -------------------------------------------------------------------------
    # get_canvas_matrix_position
    # Returns the position of the weather canvas on the matrix canvas
    # -------------------------------------------------------------------------
    def get_canvas_matrix_position(self):
        return self.__MatrixPosition

    # -------------------------------------------------------------------------
    # get_weather_canvas
    # Returns the weather canvas
    # -------------------------------------------------------------------------
    def get_weather_canvas(self):
        return self.__WeatherCanvas

    # -------------------------------------------------------------------------
    # update_weather_canvas_thread
    # The weather canvas threads
    # -------------------------------------------------------------------------
    def update_weather_canvas_thread(self):
        while True:
            # Calculate the date of the forecast (only every 3 hours)
            # Adding an offset.
            date = self.get_offset_date(self.__HoursFromNow)

            # Read the weather from TheWeather thread
            self.__WeatherForecast = TheWeather.get_readable_forecast(date)
            # If there was a read error (happens when the time is too close to the
            # next forecast, read the one 3 hours ahead instead
            if self.__WeatherForecast == {}:
                date = self.get_offset_date(self.__HoursFromNow + 3)
                self.__WeatherForecast = TheWeather.get_readable_forecast(date)

            # Draw the weather forcast canvas
            self.draw_weather_canvas()

            # Don't update unless the time is greater than updateinterval (s) or 10
            # minutes (if there has been an error)
            if self.__WeatherReadError:
                delay = 600
                self.__WeatherReadError = False
            else:
                delay = self.__UpdateInterval

            # Draw the weather canvas on the matrix canvas
            self.draw_on_matrix_canvas()

            time.sleep(delay)

    # -------------------------------------------------------------------------
    # draw_weather_canvas
    # Draw the new Weather canvas according to the definition
    # -------------------------------------------------------------------------
    def draw_weather_canvas(self):
        # Go through each item, updating any images if required
        current_weather = self.__WeatherForecast
        if current_weather == {}:
            logging.warning('The weather was not updated correctly')
            self.__ImageChanged = False
            self.__WeatherReadError += 1
        else:
            self.__ImageChanged = False
            # Weather Icon
            if self.__WeatherDefinition['WeatherIcon'] != ():
                if self.__CurrentWeatherIcon != current_weather['icon']:
                    self.__CurrentWeatherIcon = current_weather['icon']
                    self.draw_weather_icon()
                    self.__ImageChanged = True

            # Max Temperature
            if self.__WeatherDefinition['MaxTemp'] != ():
                if self.__CurrentWeatherMaxTemp != current_weather['MaxTemp']:
                    self.__CurrentWeatherMaxTemp = current_weather['MaxTemp']
                    self.draw_temperature('MaxTemp', self.__CurrentWeatherMaxTemp, 'C')
                    self.__ImageChanged = True

            # Min Temperature
            if self.__WeatherDefinition['MinTemp'] != ():
                if self.__CurrentWeatherMinTemp != current_weather['MinTemp']:
                    self.__CurrentWeatherMinTemp = current_weather['MinTemp']
                    self.draw_temperature('MinTemp', self.__CurrentWeatherMinTemp, 'C')
                    self.__ImageChanged = True

            # Wind speed Icon
            if self.__WeatherDefinition['WindSpeedIcon'] != ():
                if self.__WindSpeedIcon != True:
                    self.draw_windspeed_icon()
                    self.__ImageChanged = True
                    self.__WindSpeedIcon = True

            # Wind Speed
            if self.__WeatherDefinition['WindSpeed'] != ():
                windspeedtobeaufort = current_weather['beaufort']
                if self.__CurrentWeatherWind != windspeedtobeaufort:
                    self.__CurrentWeatherWind = windspeedtobeaufort
                    self.draw_windspeed()
                    self.__ImageChanged = True

            # Rain or snow Icon?
            # If there is snow, replace the rain icon with snow icon
            if self.__WeatherDefinition['RainSnowIcon'] != ():
                # We have snow!
                if current_weather['snow'] > 0:
                    self.__CurrentWeatherRain = -1.0
                    if self.__RainSnowIcon != 'snow':
                        self.draw_rainsnow_icon('SnowIcon')
                        self.__ImageChanged = True
                        self.__RainSnowIcon = 'snow'

                    if self.__CurrentWeatherSnow != current_weather['snow']:
                        self.__CurrentWeatherSnow = current_weather['snow']
                        self.draw_snowfall()
                    self.__ImageChanged = True

                # Booo! Rain
                else:
                    self.__CurrentWeatherSnow = -1.0
                    if self.__RainSnowIcon != 'rain':
                        self.draw_rainsnow_icon('RainIcon')
                        self.__ImageChanged = True
                        self.__RainSnowIcon = 'rain'

                    if self.__CurrentWeatherRain != current_weather['rain']:
                        self.__CurrentWeatherRain = current_weather['rain']
                        self.draw_rainfall()
                        self.__ImageChanged = True

            # Weather Time Indicator (indicator of the 3 hours the forcast covers)
            if self.__WeatherDefinition['WeatherTime'] != ():
                if self.__CurrentWeatherTime != current_weather['WeatherTime']:
                    self.__CurrentWeatherTime = current_weather['WeatherTime']
                    self.draw_weather_time()
                    self.__ImageChanged = True

    # -------------------------------------------------------------------------
    # draw_rainsnow_icon
    # -------------------------------------------------------------------------
    def draw_rainsnow_icon(self, whichicon):
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['RainSnowIcon'], whichicon)

    # -------------------------------------------------------------------------
    # draw_windspeed_icon
    # -------------------------------------------------------------------------
    def draw_windspeed_icon(self):
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['WindSpeedIcon'], 'Icon')

    # -------------------------------------------------------------------------
    # draw_windspeed
    # -------------------------------------------------------------------------
    def draw_windspeed(self):
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['WindSpeed'], 'blank')
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['WindSpeed'], self.__CurrentWeatherWind)

    # -------------------------------------------------------------------------
    # draw_rainfall
    # -------------------------------------------------------------------------
    def draw_rainfall(self):
        whattodraw = 'rain' + str(self.__CurrentWeatherRain)
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['RainSnow'], whattodraw)

    # -------------------------------------------------------------------------
    # draw_snowfall
    # -------------------------------------------------------------------------
    def draw_snowfall(self):
        whattodraw = 'snow' + str(self.__CurrentWeatherSnow)
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['RainSnow'], whattodraw)

    # -------------------------------------------------------------------------
    # draw_weather_icon
    # -------------------------------------------------------------------------
    def draw_weather_icon(self):
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['WeatherIcon'], self.__CurrentWeatherIcon)

    # -------------------------------------------------------------------------
    # Draw the Weather Time indicator
    # -------------------------------------------------------------------------
    def draw_weather_time(self):
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['WeatherTime'], self.__CurrentWeatherTime)

    # -------------------------------------------------------------------------
    # draw_on_matrix_canvas
    # Draw the Weather canvas onto the LED Matrix canvas if it has changed
    # and only if 'Autodraw' is true
    # -------------------------------------------------------------------------
    def draw_on_matrix_canvas(self):
        if self.__WeatherDefinition['AutoDraw']:
            if self.__ImageChanged:
                self.__Matrix.paste_to_matrix_canvas(self.__MatrixPosition, self.__WeatherCanvas)
                self.__ImageChanged = False

    # -------------------------------------------------------------------------
    #
    # -------------------------------------------------------------------------
    def add_image_width(self, x, imagedef):
        return x + imagedef[2] - imagedef[0] + 1

    # -------------------------------------------------------------------------
    # Draw the Temperature
    # Draws the temperature in the form of
    # Max/Min icon, temperature, Unit
    # -------------------------------------------------------------------------
    def draw_temperature(self, MaxMin, Temperature, TempUnit):
        x = self.__WeatherDefinition[MaxMin][0]
        y = self.__WeatherDefinition[MaxMin][1]
        image = self.__WeatherDefinition[MaxMin][2]
        imagedefinition = self.__WeatherDefinition[MaxMin][3]

        # The Max/Min arrow
        if MaxMin == 'MaxTemp':
            self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), 'max')
            x = Weather.add_image_width(self, x, imagedefinition['max'])
        else:
            self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), 'min')
            x = Weather.add_image_width(self, x, imagedefinition['min'])

        # Temperature is below 0
        if Temperature < 0:
            self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), '-')
            x = Weather.add_image_width(self, x, imagedefinition['-'])
        else:
            self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), 'ssp')
            x = Weather.add_image_width(self, x, imagedefinition['ssp'])

        # 10's digit
        if Temperature >= 10.0:
            tensdigit = str(abs(int(Temperature)))[0]
            self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), tensdigit)
            x = Weather.add_image_width(self, x, imagedefinition[tensdigit])
        else:
            tensdigit = 0
            self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), 'sp')
            x = Weather.add_image_width(self, x, imagedefinition['sp'])

        # Units digit
        unitdigit = str(abs(int(Temperature)) - int(tensdigit) * 10)
        self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), unitdigit)
        x = Weather.add_image_width(self, x, imagedefinition[unitdigit])

        # Decimal point
        self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), '.')
        x = Weather.add_image_width(self, x, imagedefinition['.'])

        # Decimal
        Dec = str(int(abs(Temperature) * 10 % 10))
        self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), Dec)
        x = Weather.add_image_width(self, x, imagedefinition[Dec])

        # Temperature unit
        self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), TempUnit)

    # -------------------------------------------------------------------------
    # get_offset_date
    # Calculate the date for the forecast (offset hours from now)
    # -------------------------------------------------------------------------
    def get_offset_date(self, offset):
        forecastdate = datetime.now() + timedelta(hours=offset)
        forecasthour = int(forecastdate.strftime('%H'))
        forecastseachhour = forecasthour - forecasthour % 3
        return forecastdate.strftime('%Y') + '-' + forecastdate.strftime('%m') + '-' + \
               forecastdate.strftime('%d') + ' ' + '{:02}'.format(forecastseachhour) + ':00:00'


# #############################################################################
# Class: PIR
# Detects whether there has been movement around the clock, and turns the
# matrix off if there has not been any
# #############################################################################
class PIR:
    def __init__(self, ledmatrix, pirpin, nomovementforseconds):
        self.__ledmatrix = ledmatrix
        self.__delay = nomovementforseconds
        self.__pin = pirpin
        self.__PIR = MotionSensor(self.__pin)

    # -------------------------------------------------------------------------
    # wait_for_no_movement
    # Waits to see if there is movement within self.__delay seconds
    # If there is none, fades the matrix to black and stops it from being
    # updated.
    # Once movement is seen, fades the screen back on.
    # -------------------------------------------------------------------------
    def wait_for_no_movement(self):
        t = time.time()
        while True:
            nomovement = self.__PIR.wait_for_no_motion(10)
            if nomovement:
                logging.info('No movement')
                if (time.time() - t) >= self.__delay:
                    logging.info('Turning off screen')
                    self.__ledmatrix.set_draw_on_matrix(False)
                    if self.__PIR.wait_for_motion():
                        t = time.time()
                        logging.info('Turning on screen')
                        self.__ledmatrix.set_draw_on_matrix(True)
                else:
                    if self.__PIR.wait_for_motion(10):
                        logging.info('Motion detected')
                        t = time.time()
            else:
                logging.info('Motion detected')
                t = time.time()


# -----------------------------------------------------------------------------
# Initialise the LEDMatrix class
# Rows and chain length are both required parameters:
# matrix = Adafruit_RGBmatrix(32, 4)  # for the 64 x 32 matrix by 2
# -----------------------------------------------------------------------------
MyLEDs = LEDMatrix(32, 4, 64, 64)
# MyLEDs.matrix.SetPWMBits(5)

# -----------------------------------------------------------------------------
# Initialise the Weather Forecast retrieval class
# -----------------------------------------------------------------------------
TheWeather = GetWeatherData(CityLocation, WeatherUnits, 60 * 90, 60 * 10, demodata)

# -----------------------------------------------------------------------------
# Define the Matrix Layout by initialising the Clock and Weather classes
# -----------------------------------------------------------------------------
Time = Clock(MyLEDs, (0, 0), TimeDef, 12)
Date = Clock(MyLEDs, (37, 0), DateDef, -1)

WeatherNow = Weather(MyLEDs, (0, 16), WeatherDef, 0, refreshweatherinterval)
WeatherPlus3 = Weather(MyLEDs, (0, 48), WeatherPlusDef, 3, refreshweatherinterval)
WeatherPlus6 = Weather(MyLEDs, (0, 48), WeatherPlusDef, 6, refreshweatherinterval)
WeatherPlus9 = Weather(MyLEDs, (0, 48), WeatherPlusDef, 9, refreshweatherinterval)

# -----------------------------------------------------------------------------
# Initialise the PIR Detection class
# -----------------------------------------------------------------------------
MovementPIR = PIR(MyLEDs, pirpin, turnscreenoffdelay)

# -----------------------------------------------------------------------------
# Define the threads
# -----------------------------------------------------------------------------
GetWeatherThread = threading.Thread(target=TheWeather.get_weather_for_city_thread, args=())
TimeThread = threading.Thread(target=Time.update_time_canvas, args=())
DateThread = threading.Thread(target=Date.update_date_canvas, args=())
WeatherThreadNow = threading.Thread(target=WeatherNow.update_weather_canvas_thread, args=())
WeatherThread3 = threading.Thread(target=WeatherPlus3.update_weather_canvas_thread, args=())
WeatherThread6 = threading.Thread(target=WeatherPlus6.update_weather_canvas_thread, args=())
WeatherThread9 = threading.Thread(target=WeatherPlus9.update_weather_canvas_thread, args=())

RotateWeather = threading.Thread(target=MyLEDs.rotatecanvases, args=(
    [WeatherPlus3, WeatherPlus6, WeatherPlus9], rotatesmallweatherinterval))

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

PIRThread.start()

logging.info('Let`s go loopy!')
# Forever!
while True:
    time.sleep(3600)
