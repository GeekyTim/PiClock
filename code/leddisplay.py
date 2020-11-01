import threading
import time

from PIL import ImageEnhance
from canvas import Canvas
from rgbmatrix import RGBMatrix, RGBMatrixOptions


class LEDDisplay(threading.Thread):
    """
    Creates an LED Matrix Canvas onto which the time and weather canvases can be pasted.
    The matrix may be made from chained matrices, so this class converts between the Matrix canvas and the actual way
    required to be displayed correctly.
    """

    def __init__(self, screendefinition, componentdefinition, pir):
        """
        Initialises the LED Matrix then updates it periodically if necessary

        :param screendefinition:
        :param componentdefinition:
        :param pir:
        """
        options = RGBMatrixOptions()

        options.hardware_mapping = screendefinition['matrixDriver']
        options.rows = screendefinition['matrixRows']
        options.cols = screendefinition['matrixCols']
        options.chain_length = screendefinition['matrixCount']
        options.pixel_mapper_config = screendefinition['matrixMapper']

        options.row_address_type = 0
        options.multiplexing = 0
        options.pwm_bits = 11
        options.brightness = 100
        options.pwm_lsb_nanoseconds = 130
        options.led_rgb_sequence = "RGB"
        options.show_refresh_rate = 0

        self.__display = RGBMatrix(options=options)
        self.__display.Clear()
        self.__displaybuffer = self.__display.CreateFrameCanvas()

        self.__displaysize_x = self.__display.width
        self.__displaysize_y = self.__display.height

        self.__drawdisplay = True
        self.__displaycanvas = Canvas(self.__displaysize_x, self.__displaysize_y)

        self.__screencomponents = componentdefinition

        self.__pirobject = pir

        self.__redrawall = True

        super(LEDDisplay, self).__init__()

    def run(self):
        while True:
            if self.__pirobject.hasbeenmovement:
                displaycanvasupdated = False
                for canvas in self.__screencomponents:
                    if self.__screencomponents[canvas][1].haschanged or self.__redrawall:
                        subcanvasimage = self.__screencomponents[canvas][1].get_canvas
                        self.__paste_to_displaycanvas(self.__screencomponents[canvas][0], subcanvasimage)
                        displaycanvasupdated = True
                if displaycanvasupdated:
                    self.__updatedisplay()
                    self.__redrawall = False
            else:
                self.__fade_matrix_canvas(10, 0, -1)
                self.__redrawall = True

            time.sleep(0.5)

    def __fade_matrix_canvas(self, start, end, step):
        """
        Fade the Matrix canvas between states 'on' and 'off'

        :param start:
        :param end:
        :param step:
        """
        fadeimage = ImageEnhance.Brightness(self.__displaycanvas.Image)
        for factor in range(start, (end + step), step):
            fadedimage = fadeimage.enhance(factor / 10.0)
            self.__displaycanvas.paste(fadedimage, (0, 0))
            self.__updatedisplay()
            time.sleep(0.1)

    def __paste_to_displaycanvas(self, canvasposition, canvasimage):
        """
        Pastes another canvas (weather or time) to the Matrix canvas, and then the Matrix Canvas to the LED Matrix
        itself

        :param canvasposition:
        :param canvasimage:
        """
        canvasstart_x = canvasposition[0]
        canvasstart_y = canvasposition[1]
        canvassize_x = canvasimage.get_canvassize_x
        canvassize_y = canvasimage.get_canvassize_y
        canvasend_x = canvasstart_x + canvassize_x - 1
        canvasend_y = canvasstart_y + canvassize_y - 1

        # If the image is off the screen, don't draw any of it
        if canvasstart_x <= self.__displaysize_x - 1 and canvasstart_y <= self.__displaysize_y - 1 \
                and canvasend_x >= 0 and canvasend_y >= 0:
            # Create a crop box to stop the canvas exceeding off the Matrix Canvas area
            imagebox = (0, 0, min(self.__displaysize_x - canvasstart_x, canvassize_x),
                        min(self.__displaysize_y - canvasstart_y, canvassize_y))
            imagetopaste = canvasimage.crop(imagebox)
            imagetopaste.load()

            # Paste the imagetopaste to the Matrix Canvas
            self.__displaycanvas.paste(imagetopaste, (canvasstart_x, canvasstart_y))

    def __updatedisplay(self):
        self.__displaybuffer.SetImage(self.__displaycanvas.Image, 0, 0, unsafe=True)
        self.__display.SwapOnVSync(self.__displaybuffer)
