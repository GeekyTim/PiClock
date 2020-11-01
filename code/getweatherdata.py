import threading
from datetime import datetime, timedelta
from time import sleep

from requests import get


class GetWeatherData(threading.Thread):
    def __init__(self, mapkey, weatherformat, cityid, units, frequency, errorfrequency):
        """
        Retrieves the weather from OpenWeatherMap.org at the defined frequency and stored in __wetherdatadict

        :param mapkey: The OpenWeatherMap key
        :param weatherformat:
        :param cityid:
        :param units:
        :param frequency:
        :param errorfrequency:
        """
        self.__mapkey = mapkey
        self.__weatherURLFormat = weatherformat
        self.__cityid = cityid
        self.__units = units
        self.__refreshfrequency = frequency
        self.__errorfrequency = errorfrequency

        self.__wetherdatadict = []

        super(GetWeatherData, self).__init__()

    def run(self):
        """ Method runs as a thread, retrieving the weather from OpenWeatherMap.org """
        while True:
            sleeptime = self.__refreshfrequency
            try:
                weatherdata = get(self.__weatherURLFormat.format(self.__cityid, self.__mapkey),
                                  headers={'Connection': 'close'})
                if weatherdata.status_code == 200:
                    self.__wetherdatadict = weatherdata.json()
            except:
                sleeptime = self.__errorfrequency
            finally:
                sleep(sleeptime)

    def get_weatherforecast(self, offsethours):
        """
        Reads the weather forecast for the time weather_forecast_time from __weatherdatadict
        """
        weather = None
        weatherlist = self.__wetherdatadict['list']
        offsettime = self.__get_offset_date(offsethours)

        foundweather = next((sub for sub in weatherlist if sub['dt_txt'] == offsettime), None)
        if foundweather is not None:
            weather = foundweather

        return weather

    @property
    def haveforecasts(self):
        return self.__wetherdatadict != []

    @staticmethod
    def __get_offset_date(offset):
        """
        Calculate the date for the forecast (offset hours from now)

        :param offset:
        :return:
        """
        forecastdate = datetime.now() + timedelta(hours=offset)
        forecasthour = int(forecastdate.strftime('%H'))
        forecastseachhour = forecasthour - forecasthour % 3
        returndate = forecastdate.strftime('%Y') + '-' + forecastdate.strftime('%m') + '-' + forecastdate.strftime(
            '%d') + ' ' + '{:02}'.format(forecastseachhour) + ':00:00'
        return returndate
