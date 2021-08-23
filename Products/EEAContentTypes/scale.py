""" Custom image scale adapter
"""
from plone.app.blob.scale import Blob
from plone.app.blob.scale import BlobImageScaleFactory
from plone.app.blob.scale import scaleImage
from cStringIO import StringIO
import xml.etree.ElementTree as ET


def get_svg_dimensions(data):
    """ Read width and height from svg either from tag or from viewbox """
    width = -1
    height = -1
    svg = StringIO(data)
    tree = ET.parse(svg)
    root = tree.getroot()
    h = root.attrib.get('height')
    w = root.attrib.get('width')
    if not h:
        viewbox = root.attrib.get('viewBox')
        if viewbox:
            values = viewbox.split(' ')
            w = values[-2]
            h = values[-1]
    height = int(h) if h else height
    width = int(w) if w else width
    return width, height


def calculate_thumbnail_dimensions(data, dimensions):
    """ Use thumbnail logic from PIL to determine the size of the svg thumbnail
        https://github.com/python-pillow/Pillow/blob/4.3.x/PIL/Image.py#L2053
    """
    svg_width, svg_height = get_svg_dimensions(data)
    scale_width = dimensions.get('width', 1200)
    scale_height = dimensions.get('height', 800)
    scaled_width = 0
    scaled_height = 0
    if svg_width > scale_width:
        scaled_height = int(max(svg_height * scale_width / svg_width, 1))
        scaled_width = scale_width
    elif svg_height > scale_height:
        scaled_width = int(max(svg_width * scale_height / svg_height, 1))
        scaled_height = scale_height
    return scaled_width, scaled_height


class EEABlobImageScaleFactory(BlobImageScaleFactory):
    """ adapter for image fields that allows generating scaled images
    """
    def create(self, context, **parameters):
        wrapper = self.field.get(context)
        if wrapper:
            blob = Blob()
            result = blob.open('w')
            if getattr(wrapper, 'content_type', '') == 'image/svg+xml':
                data = wrapper.getBlob().open('r').read()
                dimensions = calculate_thumbnail_dimensions(data, parameters)
                result.write(data)
                file_format = 'svg+xml'
            else:
                _, file_format, dimensions = scaleImage(
                    wrapper.getBlob().open('r'),
                    result=result, **parameters)

            result.close()
            return blob, file_format, dimensions
