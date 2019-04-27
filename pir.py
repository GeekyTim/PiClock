from gpiozero import MotionSensor
import time
import logging

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

        logging.info('set up sensor')
        self.__PIR = MotionSensor(self.__pin)
        logging.info('starting motion')

    # -------------------------------------------------------------------------
    # wait_for_no_movement
    # Waits to see if there is movement within self.__delay seconds
    # If there is none, fades the matrix to black and stops it from being
    # updated.
    # Once movement is seen, fades the screen back on.
    # -------------------------------------------------------------------------
    def wait_for_no_movement(self):
        logging.info('motionsensor')
        t = time.time()
        while True:
            nomovement = self.__PIR.wait_for_no_motion(10)
            if nomovement:
                logging.info('No movement')
                if (time.time() - t) >= self.__delay:
                    logging.info('Turning off screen')
                    self.__Matrix.set_draw_on_matrix(False)
                    if self.__PIR.wait_for_motion():
                        t = time.time()
                        logging.info('Turning on screen')
                        self.__Matrix.set_draw_on_matrix(True)
                else:
                    if self.__PIR.wait_for_motion(10):
                        logging.info('Motion detected')
                        t = time.time()
            else:
                logging.info('Motion detected')
                t = time.time()
