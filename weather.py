import logging
from canvas import Canvas
from datetime import datetime, timedelta
import time
from getweatherdata import GetWeatherData 

# #############################################################################
# The Weather class
# Updates the weather conditions from the Weather file, and updates the screen 
# when necessary.
# Only updates every UpdateInterval (seconds), or 10 minutes if there is an 
# error
# #############################################################################
class Weather:
    def __init__(self, matrixobject, positioninmatrix, weatherdefinition, forecast, hours_from_now, update_interval):
        logging.info('Creating new Weather instance')
        self.__Matrix = matrixobject
        self.__MatrixPosition = positioninmatrix
        self.__WeatherDefinition = weatherdefinition
        self.__HoursFromNow = hours_from_now
        self.__UpdateInterval = update_interval

        self.__WeatherCanvas = Canvas(weatherdefinition['Size'])
        self.__ImageChanged = True

        self.__forecast = forecast
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
            self.__WeatherForecast = self.__forecast.get_readable_forecast(date)
            # If there was a read error (happens when the time is too close to the
            # next forecast, read the one 3 hours ahead instead
            if self.__WeatherForecast == {}:
                date = self.get_offset_date(self.__HoursFromNow + 3)
                self.__WeatherForecast = self.__forecast.get_readable_forecast(date)

            # Draw the weather forecast canvas
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
