""" Custom image scale adapter
"""
from plone.app.blob.scale import Blob
from plone.app.blob.scale import BlobImageScaleFactory
from plone.app.blob.scale import scaleImage


class EEABlobImageScaleFactory(BlobImageScaleFactory):
    """ adapter for image fields that allows generating scaled images
    """
    def create(self, context, **parameters):
        wrapper = self.field.get(context)
        if wrapper:
            blob = Blob()
            result = blob.open('w')
            if getattr(wrapper, 'content_type', '')  == 'image/svg+xml':
                result.write(wrapper.getBlob().open('r').read())
                dimensions = (
                    parameters.get('width', 1200),
                    parameters.get('height', 800)
                )
                format = 'svg+xml'
            else:
                _, format, dimensions = scaleImage(wrapper.getBlob().open('r'),
                    result=result, **parameters)

            result.close()
            return blob, format, dimensions
