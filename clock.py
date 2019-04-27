import logging
from datetime import datetime, timedelta
import time

from canvas import Canvas

# #############################################################################
# Class: Clock
# Draws the date and/or time on a canvases, and then those canvases to the
# Matrix (matrixobject).
# positioninmatrix is the position of the clock canvas in the matrix canvas
# clockdefinition is the definition of what should be in the clock (Time, DoW,
# Month or Day(date))
# clock1224 = 12 for 12 hour clock, or 24 for 24 hour clock
# #############################################################################
class Clock:
    def __init__(self, matrixobject, positioninmatrix, clockdefinition, clock1224):
        logging.info('Creating new Clock instance')
        self.__Matrix = matrixobject
        self.__MatrixPosition = positioninmatrix
        self.__ClockDefinition = clockdefinition
        self.__Clock24h = clock1224

        self.__ClockCanvas = Canvas(clockdefinition['Size'])
        self.__ImageChanged = True

        self.__CurrentHour = -1
        self.__CurrentMinute = -1
        self.__CurrentSecond = -1
        self.__CurrentDay = -1
        self.__CurrentMonth = -1
        self.__CurrentDoW = -1

    # -------------------------------------------------------------------------
    # update_time_canvas
    # Update the time every second. The time can be 12h or 24h
    # -------------------------------------------------------------------------
    def update_time_canvas(self):
        while True:
            delay = 1.0
            if 'Time' in self.__ClockDefinition:
                if self.__ClockDefinition['Time'] != {}:
                    self.draw_time()
                    delay = 1.0 - float(time.time() % 1)
            time.sleep(delay)

    # -------------------------------------------------------------------------
    # update_date_canvas
    # Updates the date every day
    # -------------------------------------------------------------------------
    def update_date_canvas(self):
        while True:
            todaysdate = datetime.today()
            datedow = todaysdate.weekday()
            datemonth = todaysdate.month
            dateday = todaysdate.day

            if 'DoW' in self.__ClockDefinition:
                if self.__ClockDefinition['DoW'] != {}:
                    if self.__CurrentDoW != datedow:
                        self.__CurrentDoW = datedow
                        self.__ImageChanged = True
                        self.__ClockCanvas.draw_on_canvas(self.__ClockDefinition['DoW'], self.__CurrentDoW)

            if 'Day' in self.__ClockDefinition:
                if self.__ClockDefinition['Day'] != {}:
                    if self.__CurrentDay != dateday:
                        self.__CurrentDay = dateday
                        self.__ImageChanged = True
                        self.draw_day()

            if 'Month' in self.__ClockDefinition:
                if self.__ClockDefinition['Month'] != {}:
                    if self.__CurrentMonth != datemonth:
                        self.__CurrentMonth = datemonth
                        self.__ImageChanged = True
                        self.__ClockCanvas.draw_on_canvas(self.__ClockDefinition['Month'], self.__CurrentMonth)

            if self.__ClockDefinition['AutoDraw']:
                self.draw_on_matrix_canvas()

            # Calculate the number of seconds until midnight and wait for then
            secondstomidnight = (datetime.now().replace(hour=0, minute=0, second=0,
                                                        microsecond=0) + timedelta(days=1)) - datetime.now()
            time.sleep(secondstomidnight.total_seconds())

    # ----------------------------------------------------------------------------------
    # draw_clock_digit
    # Draw an individual clock digit at the pre-defined position (x, y) tuple
    # ----------------------------------------------------------------------------------
    def draw_clock_digit(self, position, digit):
        self.__ClockCanvas.draw_on_canvas(
            (position[0], position[1], self.__ClockDefinition['Time'][2], self.__ClockDefinition['Time'][3]),
            digit)

    # -------------------------------------------------------------------------
    # add_image_width
    # Increase x by a defined width
    # -------------------------------------------------------------------------
    def add_image_width(self, x, imagedef):
        return x + imagedef[2] - imagedef[0] + 1

    # ----------------------------------------------------------------------------------
    # draw_day
    # Update the day (date), consisting of a one or two digit number
    # ----------------------------------------------------------------------------------
    def draw_day(self):
        x = self.__ClockDefinition['Day'][0]
        y = self.__ClockDefinition['Day'][1]
        image = self.__ClockDefinition['Day'][2]
        imagedefinition = self.__ClockDefinition['Day'][3]

        # 10's digit
        if self.__CurrentDay >= 10.0:
            tensdigit = str(abs(int(self.__CurrentDay)))[0]
            self.__ClockCanvas.draw_on_canvas((x, y, image, imagedefinition), tensdigit)
            x = self.add_image_width(x, imagedefinition[tensdigit])
        else:
            tensdigit = 0
            self.__ClockCanvas.draw_on_canvas((x, y, image, imagedefinition), 'sp')
            x = self.add_image_width(x, imagedefinition['sp'])

        # Units digit
        unitdigit = str(abs(int(self.__CurrentDay)) - (int(tensdigit) * 10))
        self.__ClockCanvas.draw_on_canvas((x, y, image, imagedefinition), unitdigit)

    # ----------------------------------------------------------------------------------
    # draw_time
    # Update the time display, hh:mm a/p
    # ----------------------------------------------------------------------------------
    def draw_time(self):
        x = self.__ClockDefinition['Time'][0]
        y = self.__ClockDefinition['Time'][1]
        image = self.__ClockDefinition['Time'][2]
        imagedefinition = self.__ClockDefinition['Time'][3]

        self.__ImageChanged = False

        # The font is assumed to be non-proportional for all but the : and am/pm
        # Calculate the positions of the various items
        xhourtens = x
        xhourunits = self.add_image_width(xhourtens, imagedefinition[1])
        xcolon = self.add_image_width(xhourunits, imagedefinition[1])
        xminutetens = self.add_image_width(xcolon, imagedefinition[':'])
        xminuteunits = self.add_image_width(xminutetens, imagedefinition[1])
        xampm = self.add_image_width(xminuteunits, imagedefinition[1])

        # Get the current hour
        currenttime = time.localtime()

        # Only update the hour if it has changed
        if currenttime.tm_hour != self.__CurrentHour:
            self.__ImageChanged = True
            self.__CurrentHour = currenttime.tm_hour
            if self.__Clock24h == 12:
                # Change to 12 hour clock
                if currenttime.tm_hour > 12:
                    hour = self.__CurrentHour - 12
                    ampm = 1
                else:
                    hour = self.__CurrentHour
                    ampm = 0
            else:
                # 24 hour
                hour = self.__CurrentHour
                ampm = -1

            # Draw the hours - first digit
            if hour >= 20:
                firstdigit = 2
                seconddigit = hour - 20
            elif hour >= 10:
                firstdigit = 1
                seconddigit = hour - 10
            else:
                firstdigit = ' '
                seconddigit = hour

            # Draw the first digit
            self.draw_clock_digit((xhourtens, y), firstdigit)
            # Draw the second digit
            self.draw_clock_digit((xhourunits, y), seconddigit)

            # Draw AM/PM
            if ampm == 0:
                self.draw_clock_digit((xampm, y), 'am')
            elif ampm == 1:
                self.draw_clock_digit((xampm, y), 'pm')

        # Draw the : flashing each second
        if currenttime.tm_sec != self.__CurrentSecond:
            self.__ImageChanged = True
            self.__CurrentSecond = currenttime.tm_sec
            if self.__CurrentSecond / 2.0 == int(self.__CurrentSecond / 2):
                self.draw_clock_digit((xcolon, y), ':')
            else:
                self.draw_clock_digit((xcolon, y), ': ')

        # Only update the minutes if they have changed
        if currenttime.tm_min != self.__CurrentMinute:
            self.__ImageChanged = True
            self.__CurrentMinute = currenttime.tm_min

            minute = self.__CurrentMinute
            if self.__CurrentMinute < 10:
                minute_firstdigit = 0
                minute_seconddigit = self.__CurrentMinute
            else:
                minute_firstdigit = int(str(self.__CurrentMinute)[0])
                minute_seconddigit = int(str(self.__CurrentMinute)[1])

            self.draw_clock_digit((xminutetens, y), minute_firstdigit)
            self.draw_clock_digit((xminuteunits, y), minute_seconddigit)

        self.draw_on_matrix_canvas()

    # ----------------------------------------------------------------------------------
    # draw_on_matrix_canvas
    # If the canvas has changed, draw it on the
    # ----------------------------------------------------------------------------------
    def draw_on_matrix_canvas(self):
        # Only draw on matrix canvas if AutoDraw is set to True, and the image has changed
        if self.__ClockDefinition['AutoDraw']:
            if self.__ImageChanged:
                self.__Matrix.paste_to_matrix_canvas(self.__MatrixPosition, self.__ClockCanvas)
                self.__ImageChanged = False
