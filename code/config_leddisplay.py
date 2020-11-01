# Configuration of the LED Matrix

# Rows and chain length are both required parameters:
# matrix = Adafruit_RGBmatrix(32, 4)  # for the 64 x 32 matrix by 2
# screendefinition is the real format of each matrix. It assumes all screens are equal size.
#   matrixWidth = Width of the matrix
#   matrixHeight = Height of the matrix
#   matrixCount = Number of screens
#   matrixFlip = Flip the even matrices (1=true)

LEDFormat = {"matrixRows": 32,
             "matrixCols": 64,
             "matrixCount": 2,
             "matrixMapper": "U-mapper;Rotate:180",
             "matrixDriver": "adafruit-hat-pwm"}

# A dictionary with the location of the canvases. The None will be filled in by the object names before use
CanvasPositions = {"Time": [(0, 0), None],
                   "Date": [(37, 0), None],
                   "WeatherNow": [(0, 16), None],
                   "RotateWeather": [(0, 48), None]}
