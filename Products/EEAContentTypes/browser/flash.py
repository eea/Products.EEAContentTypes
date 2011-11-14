#import zope.interface
#import zope.component

from Products.Five import BrowserView
#from Products.CMFCore.utils import getToolByName

class RelatedFlash(BrowserView):

    def relatedFlash(self):
        context = self.context
        related = context.getRelatedItems()
        for obj in related:
            if obj.portal_type == 'FlashFile':
                return obj
        return None

    def relatedFlashStyle(self):
        flash = self.relatedFlash()
        width = flash.getWidth()
        return 'width: %spx; margin-left: -%spx;' % ( width, int(width/2))
