""" IMG view
"""
from zope.interface import implements
from zope.publisher.interfaces import NotFound
from Products.Five.browser import BrowserView
from eea.imagescales.browser.interfaces import IImageView
from eea.imagescales.browser import atfield, atfolder


class ImageView(BrowserView):
    """This adapter is for EEA content types have two ways of
    storing thumbnails.

    First we try to use the standard ATField adapter which looks for a
    file in the an image field. If that fails, we fall back to the folder
    adapter which looks for the first image in the folder.
    """

    implements(IImageView)

    def __init__(self, context, request):
        super(ImageView, self).__init__(context, request)
        self.img1 = atfield.ATFieldImageView(self.context, self.request)
        self.img2 = atfolder.FolderImageView(self.context, self.request)

    def display(self, scalename='thumb'):
        """ Display
        """
        return self.img1.display(scalename) or self.img2.display(scalename)

    def __call__(self, scalename='thumb'):
        if self.img1.display(scalename):
            return self.img1(scalename)
        if self.img2.display(scalename):
            return self.img2(scalename)
        raise NotFound(self.request, self.name)
