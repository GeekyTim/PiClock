#!/usr/bin/env python
import time
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions

options = RGBMatrixOptions()

options.hardware_mapping = "adafruit-hat-pwm"
options.rows = 32
options.cols = 64
options.chain_length = 2
options.row_address_type = 0
options.pwm_bits = 11
options.brightness = 100
options.pixel_mapper_config = "U-mapper;Rotate:180"
options.show_refresh_rate = 0

matrix = RGBMatrix(options = options)

image = Image.open("/home/pi/PiClock/pi.ppm").convert('RGB')
image.resize((matrix.width, matrix.height), Image.ANTIALIAS)

image2 = Image.open("/home/pi/PiClock/pi.ppm").convert('RGB')

imagebuffer = matrix.CreateFrameCanvas()
img_width, img_height = image.size

# let's scroll
xpos = 0
ypos = 0

imagebuffer.SetImage(image)

#matrix.SwapOnVSync(imagebuffer)
#matrix.SetImage(image, 32, 32)

#time.sleep(1)

while True:
    if (xpos > img_width):
        xpos = 1
    print(xpos)

    imagebuffer.SetImage(image, xpos, xpos)
    imagebuffer.SetImage(image, 63-xpos, 63-xpos)
    #double_buffer.SetImage(image, -xpos + img_width)
    #matrix.SetImage(image, xpos, xpos)

    matrix.SwapOnVSync(imagebuffer)

    time.sleep(0.5)
    xpos += 1
    matrix.Clear()


