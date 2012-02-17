""" Validators """

from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation
from zope.interface import implements
import PIL
from cStringIO import StringIO

class ManagementPlanCodeValidator:
    """ Validator
    """
    implements(IValidator)

    def __init__(self,
                 name,
                 title='Management plan code',
                 description='Management plan code validator'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):
        """ check if management plan code is in right format """
        # check we have 3 digits separated by dots
        errmsg = "Validation failed, management plan code is not in " \
                 "the format #.#.# e.g. 1.5.2"
        digits = value[1].split('.')
        if len(digits) == 3:
            for dig in digits:
                try:
                    int(dig)
                except ValueError:
                    return (errmsg)
            return 1
        else:
            return (errmsg)

validation.register(
    ManagementPlanCodeValidator('management_plan_code_validator'))


class ImageMinSize:
    """ Image minimum size validator
    """
    implements(IValidator)

    def __init__( self, name, title='ImageSizeValidator',
                        description='Image size validator'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        """ check to see if the image is at least 1024px """
        try:
            image = PIL.Image.open(value)
        except AttributeError:
            img_stream = StringIO(value.data.data)
            image = PIL.Image.open(img_stream)
        if image.size[0] < 1024:
            return "Image needs to be at least 1024px in width"
        return 1

validation.register(ImageMinSize('imageMinSize'))
