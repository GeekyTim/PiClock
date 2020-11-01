import threading
from time import time, sleep

import RPi.GPIO as GPIO


class PIR(threading.Thread):
    """
    Detects whether there has been movement around the clock, and turns the matrix off if there has not been any
    """

    def __init__(self, pirpin, nomovementforseconds):
        self.__pin = pirpin
        self.__delay = nomovementforseconds

        GPIO.setup(self.__pin, GPIO.IN)

        self.__hasbeenmovement = True

        super(PIR, self).__init__()

    def run(self):
        """
        Waits to see if there is movement within self.__delay seconds
        If there is none, fades the matrix to black and stops it from being updated.
        Once movement is seen, fades the screen back on.
        """
        t = time()

        while True:
            while GPIO.input(self.__pin) == 0:
                if (time() - t) >= self.__delay:
                    self.__hasbeenmovement = False
                sleep(0.1)

            self.__hasbeenmovement = True
            t = time()
            sleep(0.1)

    @property
    def hasbeenmovement(self):
        return self.__hasbeenmovement
