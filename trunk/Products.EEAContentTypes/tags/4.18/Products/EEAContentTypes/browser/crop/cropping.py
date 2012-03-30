""" Cropping Browser views which allows you to crop images
"""
from Acquisition import aq_base
from cStringIO import StringIO
from OFS.Image import Pdata
import PIL.Image
from zope.event import notify
from zope.interface import providedBy
from zope.lifecycleevent import ObjectModifiedEvent

from Products.Five import BrowserView
from Products.Archetypes.interfaces import IImageField
from plone.app.blob.interfaces import IBlobImageField

from plone.app.imaging.traverse import DefaultImageScaleHandler

class CroppableImagesView(BrowserView):
    """
    Lists the image fields together with the scales that are specified
    with the 'fill' parameter to allow later recropping.
    """

    def __init__(self, context, request):
        super(CroppableImagesView, self).__init__(context, request)
        image_fields = [field
                        for field in self.context.Schema().fields()
                        if IBlobImageField in providedBy(field).interfaces()
                        or IImageField in providedBy(field).interfaces()]
        image_fields = [f
                        for f in image_fields
                        if f.get_size(self.context)>0]
        self.image_fields = image_fields

    def imageFields(self):
        """ Returns image Fields found in the context
        """
        return [img_field.getName() for img_field in self.image_fields]

class CropImageView(BrowserView):
    """ Browser View responsible for cropping the image field
    """

    def __init__(self, context, request):
        super(CropImageView, self).__init__(context, request)
        self.field_name = request.get('field')

    def field(self):
        """ Image field getter
        """
        field = "get" + self.field_name.capitalize()
        image = getattr(self.context, field, '')
        if image:
            img = image()
            img_size = img.getSize()
            if img_size != tuple:
                data = getattr(aq_base(img), 'data')
                if isinstance(data, Pdata):
                    data = str(data)
                original_file = StringIO(data)
                img_size = PIL.Image.open(original_file).size

            size = "%sx%spx" % (img_size[0], img_size[1])
            f = { 'name' : self.field_name, 'image' : size }
            return f
        else:
            return {'name': 'image', 'image' : ''}

    def publishTraverse(self, request, name):
        """ Custom traversal to allow cropImage to be called
        """
        if name == "cropImage":
            return self.cropImage
        return super(CropImageView, self).publishTraverse(request, name)

    def scaleToLargeRatios(self):
        """ Image ratio for the original image
        """
        field = self.context.getField(self.field_name)
        large_scale = field.getScale(self.context, 'large')
        if not large_scale:
            # Ok we don't have a 'large' scale, so we'll create one.
            handler = DefaultImageScaleHandler(field)
            data = handler.createScale(self.context, 'large', 768, 768)
            handler.storeScale(self.context, 'large', **data)
            large_scale = field.getScale(self.context, 'large')

        original = field.getScale(self.context)
        return (float(original.width)/float(large_scale.width),
                float(original.height)/float(large_scale.height),)

    def cropImage(self, **kwargs):
        """ Crops the image
        """
        preview_ratio_x, preview_ratio_y = self.scaleToLargeRatios()
        box = (int(preview_ratio_x*float(self.request['x1'])),
               int(preview_ratio_y*float(self.request['y1'])),
               int(preview_ratio_x*float(self.request['x2'])),
               int(preview_ratio_y*float(self.request['y2'])),)
        field = self.context.getField(self.field_name)

        value = field.get(self.context)
        data = getattr(aq_base(value), 'data', value)
        if isinstance(data, Pdata):
            data = str(data)

        original_file = StringIO(data)
        image = PIL.Image.open(original_file)
        img_format = image.format
        image = image.crop(box)
        image_file = StringIO()
        image.save(image_file, img_format, quality=60)
        image_file.seek(0)
        file_data = image_file.getvalue()
        field.set(self.context, file_data)
        notify(ObjectModifiedEvent(self.context))

