import math
import threading
from time import sleep, strptime

from canvas import Canvas


class Weather(threading.Thread):
    """
    Updates the weather conditions from the Weather file, and updates the screen when necessary.
    Only updates every UpdateInterval (seconds), or 10 minutes if there is an error
    """

    def __init__(self, weatherdefinition, hours_from_now, update_interval, getweatherobject):
        self.__WeatherDefinition = weatherdefinition
        self.__UpdateInterval = update_interval

        self.__WeatherCanvas = Canvas(weatherdefinition['Size'][0], weatherdefinition['Size'][1])
        self.__HasImageChanged = True

        self.__GetWeatherObject = getweatherobject
        self.__WeatherData = []
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
        self.__HoursFromNow = hours_from_now

        super(Weather, self).__init__()

    def run(self):
        while True:
            # Read the weather from TheWeather thread

            weather = self.__GetWeatherObject.get_weatherforecast(self.__HoursFromNow)
            delay = 300

            # If there was a read error (happens when the time is too close to the
            # next forecast, read the one 3 hours ahead instead
            if weather is None:
                weather = self.__GetWeatherObject.get_weatherforecast(self.__HoursFromNow + 3)

            if weather is not None:
                self.__WeatherForecast = self.__get_readable_forecast(weather)

                # Draw the weather forecast canvas
                self.__draw_weather_canvas()

                # Don't update for the update interval or 5 minutes if there has been an error
                delay = self.__UpdateInterval
            else:
                print("Error in weather")

            sleep(delay)

    @property
    def haschanged(self):
        if self.__HasImageChanged:
            self.__HasImageChanged = False
            return True
        else:
            return False

    @property
    def get_canvas(self):
        """ Returns the canvas """
        return self.__WeatherCanvas

    def __draw_weather_canvas(self):
        """ Draw the new Weather canvas according to the definition """
        # Go through each item, updating any images if required
        current_weather = self.__WeatherForecast
        if current_weather == {}:
            self.__HasImageChanged = False
            self.__WeatherReadError = True
        else:
            self.__HasImageChanged = False

            # Weather Icon
            if self.__WeatherDefinition['WeatherIcon'] != ():
                if self.__CurrentWeatherIcon != current_weather['icon']:
                    self.__CurrentWeatherIcon = current_weather['icon']
                    self.__drawicon_weather()
                    self.__HasImageChanged = True

            # Max temperature
            if self.__WeatherDefinition['MaxTemp'] != ():
                if self.__CurrentWeatherMaxTemp != current_weather['MaxTemp']:
                    self.__CurrentWeatherMaxTemp = current_weather['MaxTemp']
                    self.__draw_temperature('MaxTemp', self.__CurrentWeatherMaxTemp, 'C')
                    self.__HasImageChanged = True

            # Min temperature
            if self.__WeatherDefinition['MinTemp'] != ():
                if self.__CurrentWeatherMinTemp != current_weather['MinTemp']:
                    self.__CurrentWeatherMinTemp = current_weather['MinTemp']
                    self.__draw_temperature('MinTemp', self.__CurrentWeatherMinTemp, 'C')
                    self.__HasImageChanged = True

            # Wind speed Icon
            if self.__WeatherDefinition['WindSpeedIcon'] != ():
                if not self.__WindSpeedIcon:
                    self.__drawicon_windspeed()
                    self.__HasImageChanged = True
                    self.__WindSpeedIcon = True

            # Wind Speed
            if self.__WeatherDefinition['WindSpeed'] != ():
                windspeedtobeaufort = current_weather['beaufort']
                if self.__CurrentWeatherWind != windspeedtobeaufort:
                    self.__CurrentWeatherWind = windspeedtobeaufort
                    self.__draw_windspeed()
                    self.__HasImageChanged = True

            # Rain or snow Icon?
            # If there is snow, replace the rain icon with snow icon
            if self.__WeatherDefinition['RainSnowIcon'] != ():
                # We have snow!
                if current_weather['snow'] > 0:
                    self.__CurrentWeatherRain = -1.0
                    if self.__RainSnowIcon != 'snow':
                        self.__drawicon_rainsnow('SnowIcon')
                        self.__HasImageChanged = True
                        self.__RainSnowIcon = 'snow'

                    if self.__CurrentWeatherSnow != current_weather['snow']:
                        self.__CurrentWeatherSnow = current_weather['snow']
                        self.__draw_snowfall()
                    self.__HasImageChanged = True

                # Booo! Rain
                else:
                    self.__CurrentWeatherSnow = -1.0
                    if self.__RainSnowIcon != 'rain':
                        self.__drawicon_rainsnow('RainIcon')
                        self.__HasImageChanged = True
                        self.__RainSnowIcon = 'rain'

                    if self.__CurrentWeatherRain != current_weather['rain']:
                        self.__CurrentWeatherRain = current_weather['rain']
                        self.__draw_rainfall()
                        self.__HasImageChanged = True

            # Weather Time Indicator (indicator of the 3 hours the forecast covers)
            if self.__WeatherDefinition['WeatherTime'] != ():
                if self.__CurrentWeatherTime != current_weather['WeatherTime']:
                    self.__CurrentWeatherTime = current_weather['WeatherTime']
                    self.__drawicon_weathertime()
                    self.__HasImageChanged = True

    def __drawicon_rainsnow(self, whichicon):
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['RainSnowIcon'], whichicon)

    def __drawicon_windspeed(self):
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['WindSpeedIcon'], 'Icon')

    def __drawicon_weather(self):
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['WeatherIcon'], self.__CurrentWeatherIcon)

    def __drawicon_weathertime(self):
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['WeatherTime'], self.__CurrentWeatherTime)

    def __draw_windspeed(self):
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['WindSpeed'], 'blank')
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['WindSpeed'], self.__CurrentWeatherWind)

    def __draw_rainfall(self):
        whattodraw = 'rain' + str(self.__CurrentWeatherRain)
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['RainSnow'], whattodraw)

    def __draw_snowfall(self):
        whattodraw = 'snow' + str(self.__CurrentWeatherSnow)
        self.__WeatherCanvas.draw_on_canvas(self.__WeatherDefinition['RainSnow'], whattodraw)

    def __draw_temperature(self, maxmin, temperature, unit):
        """
        Draws the temperature in the form of Max/Min icon, temperature, Unit

        :param maxmin:
        :param temperature:
        :param unit:
        :return:
        """
        x = self.__WeatherDefinition[maxmin][0]
        y = self.__WeatherDefinition[maxmin][1]
        image = self.__WeatherDefinition[maxmin][2]
        imagedefinition = self.__WeatherDefinition[maxmin][3]

        # The Max/Min arrow
        if maxmin == 'MaxTemp':
            self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), 'max')
            x = self.__add_image_width(x, imagedefinition['max'])
        else:
            self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), 'min')
            x = self.__add_image_width(x, imagedefinition['min'])

        # temperature is below 0
        if temperature < 0:
            self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), '-')
            x = self.__add_image_width(x, imagedefinition['-'])
        else:
            self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), 'ssp')
            x = self.__add_image_width(x, imagedefinition['ssp'])

        # 10's digit
        if temperature >= 10.0:
            tensdigit = str(abs(int(temperature)))[0]
            self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), tensdigit)
            x = self.__add_image_width(x, imagedefinition[tensdigit])
        else:
            tensdigit = 0
            self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), 'sp')
            x = self.__add_image_width(x, imagedefinition['sp'])

        # Units digit
        unitdigit = str(abs(int(temperature)) - int(tensdigit) * 10)
        self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), unitdigit)
        x = self.__add_image_width(x, imagedefinition[unitdigit])

        # Decimal point
        self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), '.')
        x = self.__add_image_width(x, imagedefinition['.'])

        # Decimal
        dec = str(int(abs(temperature) * 10 % 10))
        self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), dec)
        x = self.__add_image_width(x, imagedefinition[dec])

        # temperature unit
        self.__WeatherCanvas.draw_on_canvas((x, y, image, imagedefinition), unit)

    def __get_readable_forecast(self, weatherdict):
        """
        Converts the weather for the defined time (weather_forecast_time) into a readable (list) format

        :param weatherdict:
        """
        weatherdata = {}

        if weatherdict == {}:
            print('The json was blank!')
        else:
            try:
                weatherdata['MaxTemp'] = self.__kelvin_to_celsius(weatherdict['main']['temp_max'])
                weatherdata['MinTemp'] = self.__kelvin_to_celsius(weatherdict['main']['temp_min'])
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
                weatherdata['beaufort'] = self.__windspeed_to_beaufort(float(weatherdict['wind']['speed']))
                weatherdata['winddir'] = self.__degrees_to_direction(float(weatherdict['wind']['deg']))
                weatherdata['icon'] = weatherdict['weather'][0]['icon']
                weatherdata['WeatherTime'] = strptime(weatherdict['dt_txt'], '%Y-%m-%d %H:%M:%S').tm_hour
                weatherdata['dt_txt'] = weatherdict['dt_txt']
            except:
                print('Error __get_readable_forecast')
            finally:
                return weatherdata

    @staticmethod
    def __kelvin_to_celsius(kelvin):
        """
        Converts the temperature from Kelvins to Celsius

        :param kelvin:
        :return: The temperature in Celsius
        """
        return round(float(kelvin) - 273.15, 1)

    @staticmethod
    def __windspeed_to_beaufort(windspeedmps):
        """
        Converts the wind speed from m/s to Beaufort scale

        :param windspeedmps:
        :return:
        """
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

    @staticmethod
    def __degrees_to_direction(degrees):
        """
        Convert the wind direction from degrees to compass direction

        :param degrees: The wind direction, in degrees
        :return: Text version of the wind direction
        """

        winddirection = None

        degrees = float(degrees)
        if degrees <= 11.25 or degrees >= 348.76:
            winddirection = "N"
        elif degrees <= 33.75:
            winddirection = "NNE"
        elif degrees <= 56.25:
            winddirection = "NE"
        elif degrees <= 78.75:
            winddirection = "ENE"
        elif degrees <= 101.25:
            winddirection = "E"
        elif degrees <= 123.75:
            winddirection = "ESE"
        elif degrees <= 146.25:
            winddirection = "SE"
        elif degrees <= 168.75:
            winddirection = "SSE"
        elif degrees <= 191.25:
            winddirection = "S"
        elif degrees <= 213.75:
            winddirection = "SSW"
        elif degrees <= 236.25:
            winddirection = "SW"
        elif degrees <= 258.75:
            winddirection = "WSW"
        elif degrees <= 281.25:
            winddirection = "W"
        elif degrees <= 303.75:
            winddirection = "WNW"
        elif degrees <= 326.25:
            winddirection = "NW"
        elif degrees <= 348.75:
            winddirection = "NNW"

        return winddirection

    @staticmethod
    def __add_image_width(x, imagedef):
        return x + imagedef[2] - imagedef[0] + 1
