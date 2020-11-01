import threading
from time import time, sleep, localtime
from datetime import datetime

from canvas import Canvas


class Clock(threading.Thread):
    """ Draws the date and/or time on a canvases """

    def __init__(self, clockdefinition, clock1224):
        """
        :param clockdefinition: The definition of what should be in the clock (Time, DoW, Month or Day(date))
        :param clock1224: = 12 for 12 hour clock, or 24 for 24 hour clock
        """
        self.__ClockDefinition = clockdefinition
        self.__Clock24h = clock1224

        # Create a canvas for the Clock - this is what will be updated
        self.__ClockCanvas = Canvas(clockdefinition['Size'][0], clockdefinition['Size'][1])
        self.__HasImageChanged = True

        self.__CurrentHour = -1
        self.__CurrentMinute = -1
        self.__CurrentSecond = -1
        self.__CurrentDay = -1
        self.__CurrentMonth = -1
        self.__CurrentDoW = -1

        super(Clock, self).__init__()

    def run(self):
        """ Update the time every second. The time can be 12h or 24h """
        while True:
            delay = 300
            if 'Day' in self.__ClockDefinition and self.__CurrentDay != datetime.today():
                self.__draw_date()
            if 'Time' in self.__ClockDefinition:
                self.__draw_time()
                delay = 1.0 - float(time() % 1)
            sleep(delay)

    @property
    def haschanged(self):
        if self.__HasImageChanged:
            self.__HasImageChanged = False
            return True
        else:
            return False

    @property
    def get_canvas(self):
        return self.__ClockCanvas

    def __draw_date(self):
        """ Updates the date """
        todaysdate = datetime.today()

        if 'DoW' in self.__ClockDefinition:
            if self.__ClockDefinition['DoW'] != {}:
                datedow = todaysdate.weekday()
                if self.__CurrentDoW != datedow:
                    self.__CurrentDoW = datedow
                    self.__ClockCanvas.draw_on_canvas(self.__ClockDefinition['DoW'], self.__CurrentDoW)
                    self.__HasImageChanged = True

        if 'Day' in self.__ClockDefinition:
            if self.__ClockDefinition['Day'] != {}:
                dateday = todaysdate.day
                if self.__CurrentDay != dateday:
                    self.__CurrentDay = dateday
                    self.__draw_day()
                    self.__HasImageChanged = True

        if 'Month' in self.__ClockDefinition:
            if self.__ClockDefinition['Month'] != {}:
                datemonth = todaysdate.month
                if self.__CurrentMonth != datemonth:
                    self.__CurrentMonth = datemonth
                    self.__ClockCanvas.draw_on_canvas(self.__ClockDefinition['Month'], self.__CurrentMonth)
                    self.__HasImageChanged = True

    def __draw_clock_digit(self, position, digit):
        """
        Draw an individual clock digit at the pre-defined position (x, y) tuple

        :param position:
        :param digit:
        """
        self.__ClockCanvas.draw_on_canvas(
            (position[0], position[1], self.__ClockDefinition['Time'][2], self.__ClockDefinition['Time'][3]), digit)

    def __draw_day(self):
        """
        Update the day (date), consisting of a one or two digit number
        """
        x = self.__ClockDefinition['Day'][0]
        y = self.__ClockDefinition['Day'][1]
        image = self.__ClockDefinition['Day'][2]
        imagedefinition = self.__ClockDefinition['Day'][3]

        # 10's digit
        if self.__CurrentDay >= 10.0:
            tensdigit = str(abs(int(self.__CurrentDay)))[0]
            self.__ClockCanvas.draw_on_canvas((x, y, image, imagedefinition), tensdigit)
            x = self.__add_image_width(x, imagedefinition[tensdigit])
        else:
            tensdigit = 0
            self.__ClockCanvas.draw_on_canvas((x, y, image, imagedefinition), 'sp')
            x = self.__add_image_width(x, imagedefinition['sp'])

        # Units digit
        unitdigit = str(abs(int(self.__CurrentDay)) - (int(tensdigit) * 10))
        self.__ClockCanvas.draw_on_canvas((x, y, image, imagedefinition), unitdigit)

    def __draw_time(self):
        """
        Update the time display, hh:mm a/p
        """
        x = self.__ClockDefinition['Time'][0]
        y = self.__ClockDefinition['Time'][1]
        imagedefinition = self.__ClockDefinition['Time'][3]

        # The font is assumed to be non-proportional for all but the : and am/pm
        # Calculate the positions of the various items
        xhourtens = x
        xhourunits = self.__add_image_width(xhourtens, imagedefinition[1])
        xcolon = self.__add_image_width(xhourunits, imagedefinition[1])
        xminutetens = self.__add_image_width(xcolon, imagedefinition[':'])
        xminuteunits = self.__add_image_width(xminutetens, imagedefinition[1])
        xampm = self.__add_image_width(xminuteunits, imagedefinition[1])

        # Get the current hour
        currenttime = localtime()

        # Only update the hour if it has changed
        if currenttime.tm_hour != self.__CurrentHour:
            self.__CurrentHour = currenttime.tm_hour
            self.__HasImageChanged = True
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
            self.__draw_clock_digit((xhourtens, y), firstdigit)
            # Draw the second digit
            self.__draw_clock_digit((xhourunits, y), seconddigit)

            # Draw AM/PM
            if ampm == 0:
                self.__draw_clock_digit((xampm, y), 'am')
            elif ampm == 1:
                self.__draw_clock_digit((xampm, y), 'pm')

        # Draw the : flashing each second
        if currenttime.tm_sec != self.__CurrentSecond:
            self.__HasImageChanged = True
            self.__CurrentSecond = currenttime.tm_sec
            if self.__CurrentSecond / 2.0 == int(self.__CurrentSecond / 2):
                self.__draw_clock_digit((xcolon, y), ':')
            else:
                self.__draw_clock_digit((xcolon, y), ': ')

        # Only update the minutes if they have changed
        if currenttime.tm_min != self.__CurrentMinute:
            self.__HasImageChanged = True
            self.__CurrentMinute = currenttime.tm_min

            if self.__CurrentMinute < 10:
                minute_firstdigit = 0
                minute_seconddigit = self.__CurrentMinute
            else:
                minute_firstdigit = int(str(self.__CurrentMinute)[0])
                minute_seconddigit = int(str(self.__CurrentMinute)[1])

            self.__draw_clock_digit((xminutetens, y), minute_firstdigit)
            self.__draw_clock_digit((xminuteunits, y), minute_seconddigit)

    @staticmethod
    def __add_image_width(x, imagedef):
        """
        Increase x by a defined width

        :param x:
        :param imagedef:
        :return:
        """
        return x + imagedef[2] - imagedef[0] + 1
