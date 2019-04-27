import time
import logging
import RPi.GPIO as GPIO

# #############################################################################
# Class: PIR
# Detects whether there has been movement around the clock, and turns the
# matrix off if there has not been any
# #############################################################################
class PIR:
    def __init__(self, ledmatrix, pirpin, nomovementforseconds):
        logging.info('init motion')

        self.__Matrix = ledmatrix
        self.__delay = nomovementforseconds
        self.__pin = pirpin

        GPIO.setup(self.__pin, GPIO.IN)

    # -------------------------------------------------------------------------
    # pir_set_matrix
    # Sets up the matrix ID AFTER the PIT has been intialised
    # -------------------------------------------------------------------------
    def pir_set_matrix(self, ledmatrix):
        self.__Matrix = ledmatrix

    # -------------------------------------------------------------------------
    # wait_for_no_movement
    # Waits to see if there is movement within self.__delay seconds
    # If there is none, fades the matrix to black and stops it from being
    # updated.
    # Once movement is seen, fades the screen back on.
    # -------------------------------------------------------------------------
    def wait_for_no_movement(self):
        logging.info('Motion sensor')

        if (self.__Matrix == 0):
            logging.error("You must set up the matrix before using the PIR")
            return

        t = time.time()
        screenstate = True

        while True:
            while (GPIO.input(self.__pin) == 0):
                if ((time.time() - t) >= self.__delay and screenstate):
                    screenstate = False
                    self.__Matrix.set_draw_on_matrix(screenstate)
            time.sleep(0.1)

            if (not screenstate):
                screenstate = True
                self.__Matrix.set_draw_on_matrix(screenstate)

            # Wait for 100 milliseconds
            t = time.time()
            time.sleep(0.1)
