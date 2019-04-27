import time
import logging
import json
from requests import get

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
                weatherdatadict = weatherdata.json()

                self.__weatherdatadict = weatherdatadict
                sleeptime = self.__refreshfrequency

            except:
                logging.warning('Error in get_weather_for_city_thread')
                TheWeatherData.put(self.__weatherdatadict)
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

            weatherlist = self.__weatherdatadict['list']

            for weatherdata in weatherlist:
                if weatherdata['dt_txt'] == weather_forecast_time:
                    return weatherdata

            return {}
        except:
            logging.warning('Error read_forecast_for_date(%s)', weather_forecast_time)
            return {}
