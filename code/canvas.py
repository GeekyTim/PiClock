from PIL import Image


class Canvas:
    """
    An image canvas onto which images are drawn on and stored before being drawn on the LEDDisplay
    """

    def __init__(self, x, y):
        """ Create a new canvas of size (x, y) """
        self.__canvassize_x, self.__canvassize_y = x, y
        self.__Image = Image.new('RGB', (x, y))

    @staticmethod
    def __extract_image_from_gallery(galleryimage, gallerypositions):
        """
        Extract an image from a 'gallery' image

        :param galleryimage: A single image containing all the images
        :param gallerypositions: contains the locations of the images in galleryimage
        :return: A single image
        """
        # Now get the image from file (no error checking yet!)
        singleimage = galleryimage.crop(
            (gallerypositions[0], gallerypositions[1], gallerypositions[2] + 1, gallerypositions[3] + 1))
        singleimage.load()

        return singleimage

    @property
    def get_canvassize_x(self):
        return self.__canvassize_x

    @property
    def get_canvassize_y(self):
        return self.__canvassize_y

    def draw_on_canvas(self, imagedata, whichimage):
        """
        Draws an image on the canvas

        :param imagedata: A tuple containing: (X position, Y position, ImageGalery, ImageGaleryPositions)
        :param whichimage: The sub-image contained in the ImageGalery
        :return:
        """
        imagestart_x = imagedata[0]
        imagestart_y = imagedata[1]
        imagegallery = imagedata[2]
        imagegallerypositions = imagedata[3]

        imagexsize = imagegallerypositions[whichimage][2] - imagegallerypositions[whichimage][0] + 1
        imageysize = imagegallerypositions[whichimage][3] - imagegallerypositions[whichimage][1] + 1
        imagexend = imagestart_x + imagexsize - 1
        imageyend = imagestart_y + imageysize - 1

        # If the image is on the canvas, draw it
        if (imagestart_x <= self.__canvassize_x and imagestart_y <= self.__canvassize_y) and (
                imagexend > 0 and imageyend > 0):
            croppedimage = self.__extract_image_from_gallery(imagegallery, imagegallerypositions[whichimage])
            self.__Image.paste(croppedimage, (imagestart_x, imagestart_y))

    def crop(self, imagebox):
        return self.__Image.crop(imagebox)

    def paste(self, imagetopaste, position):
        self.__Image.paste(imagetopaste, box=position)

    @property
    def Image(self):
        return self.__Image
