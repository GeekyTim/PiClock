#from gpiozero import MotionSensor
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
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.__Matrix = ledmatrix
        self.__delay = nomovementforseconds
        self.__pin = pirpin

        logging.info('set up sensor')
        #self.__PIR = MotionSensor(self.__pin)
        GPIO.setup(self.__pin, GPIO.IN)
        logging.info('starting motion')

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
        logging.info('motionsensor')

        if (self.__Matrix == 0):
            logging.error("You must set up the matrix before using the PIR")
            return

        # Loop until PIR output is 0
        while GPIO.input(self.__pin) == 1:
            currentstate = 0

        t = time.time()

        while True:
            # Read PIR state
            currentstate = GPIO.input(self.__pin)

            while (currentstate == 0):
                logging.info('No movement')
                if (time.time() - t) >= self.__delay:
                    logging.info('Turning off screen')
                    self.__Matrix.set_draw_on_matrix(False)

                    currentstate = GPIO.input(self.__pin)
                    while (currentstate == 0):
                        time.sleep(0.1)

                    t = time.time()
                    logging.info('Turning on screen')
                    self.__Matrix.set_draw_on_matrix(True)
                else:
                    currentstate = GPIO.input(self.__pin)
                    while (currentstate == 0):
                        time.sleep(0.1)

                    logging.info('Motion detected')
                    t = time.time()

                currentstate = GPIO.input(self.__pin)
            # Wait for 100 milliseconds
            time.sleep(0.1)

