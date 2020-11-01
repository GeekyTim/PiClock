from PIL import Image

# -----------------------------------------------------------------------------
# Images
# -----------------------------------------------------------------------------
imagepath = '/home/pi/PiClock/images/'

# The 'position' dictionaries show the top left and bottom right positions of
# each image within the image

# Small font used for temperature
imagename_smallfont = 'smallfont.png'
image_smallfont = Image.open(imagepath + imagename_smallfont)
imagepositions_smallfont = {'1': (0, 0, 4, 7),
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
imagename_clockfont = 'clockfont.png'
image_clockfont = Image.open(imagepath + imagename_clockfont)
imagepositions_clockfont = {0: (0, 0, 6, 15),
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
imagename_weather32 = 'OWMweather.png'
image_weather32 = Image.open(imagepath + imagename_weather32)
imagepositions_weather32 = {'01d': (0, 0, 31, 31),
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
imagename_weather16 = 'OWMweather16.png'
image_weather16 = Image.open(imagepath + imagename_weather16)
imagepositions_weather16 = {'01d': (0, 0, 15, 15),
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
imagename_rainsnow = 'weatherwarn.png'
image_rainsnow = Image.open(imagepath + imagename_rainsnow)
imagepositions_rainsnow = {'RainIcon': (0, 0, 7, 7),
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
imagename_wind = 'weatherwarn.png'
image_wind = Image.open(imagepath + imagename_wind)
imagepositions_wind = {'Icon': (0, 8, 7, 15),
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
imagename_dow = 'DoW.png'
image_dow = Image.open(imagepath + imagename_dow)
imagepositions_dow = {0: (0, 8, 16, 15),
                      1: (0, 16, 16, 23),
                      2: (0, 24, 16, 31),
                      3: (0, 32, 16, 39),
                      4: (0, 40, 16, 47),
                      5: (0, 48, 16, 55),
                      6: (0, 0, 16, 7)}

# Month Names
# 1=January etc
imagename_month = 'months.png'
image_month = Image.open(imagepath + imagename_month)
imagepositions_month = {1: (0, 0, 27, 7),
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

# The forecast clock
# Shows which 3 hours the forecast covers
imagename_weatherclock = 'clocktimes8.png'
image_weatherclock = Image.open(imagepath + imagename_weatherclock)
imagepositions_weatherclock = {0: (0, 0, 7, 7),
                               3: (8, 0, 15, 7),
                               6: (16, 0, 23, 7),
                               9: (24, 0, 31, 7),
                               12: (0, 0, 7, 7),
                               15: (8, 0, 15, 7),
                               18: (16, 0, 23, 7),
                               21: (24, 0, 31, 7)}

# Date font Images
imagename_date = 'datefont.png'
image_date = Image.open(imagepath + imagename_date)
imagepositions_date = {'1': (0, 0, 4, 7),
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

# temperature font Images
imagename_temperature = imagename_smallfont
image_temperature = Image.open(imagepath + imagename_temperature)
imagepositions_temperature = imagepositions_smallfont
