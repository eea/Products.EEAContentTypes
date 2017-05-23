""" Flash
"""
from Products.Five import BrowserView


class RelatedFlash(BrowserView):
    """ Related Flash
    """

    def relatedFlash(self):
        """ Flash
        """
        context = self.context
        related = context.getRelatedItems()
        for obj in related:
            if obj.portal_type == 'FlashFile':
                return obj
        return None

    def relatedFlashStyle(self):
        """ Flash style
        """
        flash = self.relatedFlash()
        if not flash:
            return ''

        try:
            width = int(flash.getWidth())
        except Exception:
            return ''

        return 'width: %spx; margin-left: -%spx;' % (width, int(width / 2))
