import time
import logging
import json
from requests import get
from datetime import datetime, timedelta
# #############################################################################
# Class: GetWeatherData
# Single thread that retrieves the weather from OpenWeatherMap.org and the
# defined frequency and stored in __weatherdatadict
# #############################################################################
class GetWeatherData:
    def __init__(self, mapkey, weatherFormat, cityid, units, frequency, errorfrequency):
        logging.info('Creating CetWeatherData instance')
        self.__mapkey = mapkey
        self.__weatherURLFormat = weatherFormat
        self.__cityid = cityid
        self.__units = units
        self.__refreshfrequency = frequency
        self.__errorfrequency = errorfrequency

        self.__weatherdatadict = []

    # -------------------------------------------------------------------------
    # Method runs as a thread, retrieving the weather from OpenWeatherMap.org
    # -------------------------------------------------------------------------
    def get_weather_for_city_thread(self):
        while True:
            try:
                logging.info('Getting Weather data')
                weatherdata = get(self.__weatherURLFormat.format(self.__cityid, self.__mapkey))
                self.__weatherdatadict = weatherdata.json()

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
            logging.info('Reading weather forecast')
            currentweather = self.__weatherdatadict
            for weatherdata in currentweather['list']:
                if weatherdata['dt_txt'] == weather_forecast_time:
                    return weatherdata
            return {}
        except:
            logging.warning('Error read_forecast_for_date(%s)', weather_forecast_time)
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

