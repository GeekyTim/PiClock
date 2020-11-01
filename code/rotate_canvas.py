import threading
from time import sleep


class RotateCanvas(threading.Thread):

    def __init__(self, canvaslist, rotateinterval):
        """
        Swaps the canvases shown on a single canvas in turn

        :param canvaslist:
        :param rotateinterval:
        """
        self.__canvases = canvaslist
        self.__interval = rotateinterval
        self.__currentcanvas = 0

        self.__HasImageChanged = True

        super(RotateCanvas, self).__init__()

    def run(self):
        """
        Swaps the canvases listed in self.__canvases every self.__interval seconds
        """
        canvascount = len(self.__canvases)
        canvas = self.__currentcanvas
        while True:
            self.__currentcanvas = canvas
            self.__HasImageChanged = True
            canvas = (canvas + 1) % canvascount
            sleep(self.__interval)

    @property
    def haschanged(self):
        if self.__HasImageChanged:
            self.__HasImageChanged = False
            return True
        else:
            return False

    @property
    def get_canvas(self):
        """ Returns the canvas """
        return self.__canvases[self.__currentcanvas].get_canvas
