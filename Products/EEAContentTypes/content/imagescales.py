""" Image scale
"""
from zope.interface import implements
from zope.publisher.interfaces import NotFound
from Products.Five.browser import BrowserView

from eea.depiction.browser.interfaces import IImageView
from eea.depiction.browser import atfield, atfolder


class ImageView(BrowserView):
    """ This adapter is for EEA content types have two ways of storing
    thumbnails.

    First we try to use the standard ATField adapter which looks for a file
    in the an image field. If that fails, we fall back to the folder adapter
    which looks for the first image in the folder.
    """
    implements(IImageView)
    _img1 = False
    _img2 = False

    @property
    def img1(self):
        """ Image from Schema field: image
        """
        if self._img1 is False:
            self._img1 = atfield.ATFieldImageView(self.context, self.request)
        return self._img1

    @property
    def img2(self):
        """ Image from folder contents
        """
        if self._img2 is False:
            self._img2 = atfolder.FolderImageView(self.context, self.request)
        return self._img2

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
