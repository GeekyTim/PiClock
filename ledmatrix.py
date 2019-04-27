from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageEnhance
import logging
import time

from canvas import Canvas

# #############################################################################
# Class: LEDMatrix
# Creates an LED Matrix Canvas onto which the time and weather canvases can be
# pasted.
# The matrix is made from chained matrices, so this class converts between
# the Matrix canvas and the actual way required to be displayed correctly.
# #############################################################################
class LEDMatrix:
    def __init__(self, LEDFormat):
        logging.info('Initialising LEDMatrix')

        options = RGBMatrixOptions()

        options.hardware_mapping = LEDFormat['matrixDriver']
        options.rows = LEDFormat['matrixRows']
        options.cols = LEDFormat['matrixCols']
        options.chain_length = LEDFormat['matrixCount']
        options.pixel_mapper_config = LEDFormat['matrixMapper']

        options.row_address_type = 0
        options.multiplexing = 0
        options.pwm_bits = 11
        options.brightness = 100
        options.pwm_lsb_nanoseconds = 130
        options.led_rgb_sequence = "RGB"
        options.show_refresh_rate = 0

        self.__MatrixID = RGBMatrix(options = options)
        
        self.__MatrixID.Clear()

        xsize = self.__MatrixID.width
        ysize = self.__MatrixID.height

        self.__LEDXSize = xsize
        self.__LEDYSize = ysize

        self.__LEDXMax = xsize - 1
        self.__LEDYMax = ysize - 1

        self.__DrawOnMatrix = True

        self.__MatrixCanvas = Canvas((self.__LEDXSize, self.__LEDYSize))
        self.__FadeMatrixCanvas = Canvas((self.__LEDXSize, self.__LEDYSize))

        self.__MatrixBuffer = self.__MatrixID.CreateFrameCanvas()

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
            self.paste_canvas_to_matrix((0, 0), self.__FadeMatrixCanvas, True)
            time.sleep(0.1)

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
    # drawoverride = Whether to draw onto the matrix itself
    # -------------------------------------------------------------------------
    def paste_canvas_to_matrix(self, positioninmatrix, canvasimage, drawoverride):
        if self.__DrawOnMatrix or drawoverride:
            ledimagexstart = positioninmatrix[0]
            ledimageystart = positioninmatrix[1]
            ledimagexsize = canvasimage.Image.size[0]
            ledimageysize = canvasimage.Image.size[1]
            ledimagexend = ledimagexstart + ledimagexsize - 1
            ledimageyend = ledimageystart + ledimageysize - 1

            self.__MatrixBuffer.SetImage(canvasimage.Image, ledimagexstart, ledimageystart)
            self.__MatrixID.SwapOnVSync(self.__MatrixBuffer)

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
