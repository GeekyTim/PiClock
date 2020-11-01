from config_images import *

# ----------------------------------------------------------------------------------------------------------------------
# Definitions of each canvas
# The format of the 'def' dictionary is:
# 'element':(TopLeftX, TopLeftY, ImageGallery, ImageGallery,)
# ----------------------------------------------------------------------------------------------------------------------
TimeCanvas = {'Size': (36, 16),
              'Time': (0, 0, image_clockfont, imagepositions_clockfont)}

DateCanvas = {'Size': (28, 16),
              'DoW': (0, 0, image_dow, imagepositions_dow),
              'Day': (17, 0, image_date, imagepositions_date),
              'Month': (0, 8, image_month, imagepositions_month)}

WeatherCanvas = {'Size': (64, 32),
                 'WeatherIcon': (32, 0, image_weather32, imagepositions_weather32),
                 'MaxTemp': (0, 16, image_temperature, imagepositions_temperature),
                 'MinTemp': (0, 24, image_temperature, imagepositions_temperature),
                 'WindSpeedIcon': (8, 8, image_wind, imagepositions_wind),
                 'WindSpeed': (16, 8, image_wind, imagepositions_wind,),
                 'RainSnowIcon': (8, 0, image_rainsnow, imagepositions_rainsnow,),
                 'RainSnow': (16, 0, image_rainsnow, imagepositions_rainsnow,),
                 'WeatherTime': (0, 4, image_weatherclock, imagepositions_weatherclock)}

WeatherPlusCanvas = {'Size': (64, 16),
                     'WeatherIcon': (48, 0, image_weather16, imagepositions_weather16,),
                     'MaxTemp': (16, 0, image_temperature, imagepositions_temperature),
                     'MinTemp': (16, 8, image_temperature, imagepositions_temperature),
                     'WindSpeedIcon': (),
                     'WindSpeed': (),
                     'RainSnowIcon': (8, 0, image_rainsnow, imagepositions_rainsnow,),
                     'RainSnow': (0, 8, image_rainsnow, imagepositions_rainsnow,),
                     'WeatherTime': (0, 0, image_weatherclock, imagepositions_weatherclock)}
