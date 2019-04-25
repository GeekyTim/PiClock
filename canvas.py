from PIL import Image, ImageEnhance

# #############################################################################
# Class: Canvas
# An image canvas onto which images are drawn on and stored before being drawn
# on the LEDMatrix
# #############################################################################
class Canvas:
    def __init__(self, canvassize):
        # logging.info('Creating new Canvas instance')
        # Create a new canvas of size (x, y)
        self.Image = Image.new('RGB', canvassize)

    # -------------------------------------------------------------------------
    # extract_image_from_gallery
    # Extract an image from a 'gallery' image
    # galleryimage is a single image containing all the images
    # gallerypositions contains the locations of the images in galleryimage
    # -------------------------------------------------------------------------
    def extract_image_from_gallery(self, galleryimage, gallerypositions):
        # Now get the image from file (no error checking yet!)
        singleimagebox = (gallerypositions[0], gallerypositions[1],
                          gallerypositions[2] + 1, gallerypositions[3] + 1)
        singleimage = galleryimage.crop(singleimagebox)
        singleimage.load()

        return singleimage

    # -------------------------------------------------------------------------
    # draw_on_canvas
    # Draw an image on the canvas
    # imagedata is a tuple containing:
    #     (X position, Y position, ImageGalery, ImageGaleryPositions)
    # whichimage is the sub-image contained in the ImageGalery
    # -------------------------------------------------------------------------
    def draw_on_canvas(self, imagedata, whichimage):
        # The start/end in the image within imagedata
        imagexstart = imagedata[0]
        imageystart = imagedata[1]
        imagegallery = imagedata[2]
        imagegallerypositions = imagedata[3]

        imagexsize = imagegallerypositions[whichimage][2] - imagegallerypositions[whichimage][0] + 1
        imageysize = imagegallerypositions[whichimage][3] - imagegallerypositions[whichimage][1] + 1
        imagexend = imagexstart + imagexsize - 1
        imageyend = imageystart + imageysize - 1

        # If the image is off the canvas, don't draw any of it
        if imagexstart > self.Image.size[0] or imageystart > self.Image.size[1] or imagexend < 0 or imageyend < 0:
            return

        # Extract the sub-image from the ImageGallery (imagedata[2])
        croppedimage = self.extract_image_from_gallery(imagegallery, imagegallerypositions[whichimage])
        self.Image.paste(croppedimage, (imagexstart, imageystart))
