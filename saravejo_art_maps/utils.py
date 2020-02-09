# To add text and a border to the map
from PIL import Image, ImageOps, ImageColor, ImageFont, ImageDraw

###############################################################################
#                    8. Helper Functions: Add Border to the Map               #
###############################################################################
# Get color
def _color(color, mode):
    color = ImageColor.getcolor(color, mode)
    return color

# Expand image
def expand(image, fill = '#e0474c', bottom = 50, left = None, right = None, top = None):
    """
    Expands image

    Parameters
    ----------

    image: The image to expand.
    bottom, left, right, top: Border width, in pixels.
    param fill: Pixel fill value (a color value).  Default is 0 (black).

    return: An image.
    """


    if left == None:
        left = 0
    if right == None:
        right = 0
    if top == None:
        top = 0

    width = left + image.size[0] + right
    height = top + image.size[1] + bottom
    out = Image.new(image.mode, (width, height), _color(fill, image.mode))
    out.paste(image, (left, top))
    return out

# Add border
def add_border(input_image, output_image, fill = '#e0474c', bottom = 50, left = None, right = None, top = None):
    """ Adds border to image and saves it.
    Parameters
    ----------


    input_image: str,
        String object for the image you want to load. This is the name of the file you want to read.

    output_image: str,
        String object for the output image name. This is the name of the file you want to export.

    fill: str,
        Hex code for border color. Default is set to reddish.

    bottom, left, right, top: int,
        Integer object specifying the border with in pixels.

    """


    if left == None:
        left = 0
    if right == None:
        right = 0
    if top == None:
        top = 0

    img = Image.open(input_image)
    bimg = expand(img, bottom = bottom, left = left, right = right, top = top, fill= fill)
    bimg.save(output_image)
