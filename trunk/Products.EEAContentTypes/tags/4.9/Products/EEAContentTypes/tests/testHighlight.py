""" Tests for Highlight
"""

from App.Common import package_home
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.config import product_globals
from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase
from eea.design.browser.frontpage import Frontpage
import os


image = open(os.path.join(
    package_home(product_globals), 'tests', 'image.png'), 'rb')
image = image.read()

class testHighlight(EEAContentTypeTestCase):
    """Test-cases for class(es) ExternalHighlight, Highlight."""

    def afterSetUp(self):
        """ Set up
        """
        highlight = {'type': 'Highlight', 'id' : 'high%s', 'text' : 'data%s',
                     'title' : 'Foo%s',
                     'teaser' : 'teaser%s'}
        for i in range(15):
            name = highlight['id'] % i
            text = highlight['text'] % i
            title = highlight['title'] % i
            self.folder.invokeFactory('Highlight', id=name, text=text,
                                      title=title)


        self.folder.invokeFactory('Image', id='image1',
                                  image=image, title='Image title')
        self.workflow = self.portal.portal_workflow
        self.setRoles('Manager')
        portal_properties = getToolByName(self.portal, 'portal_properties')
        frontpage_properties = getattr(portal_properties,
                                       'frontpage_properties')
        self.noOfHigh = 3
        self.noOfMedium = 4
        self.noOfLow = 10
        frontpage_properties.manage_changeProperties(
            noOfHigh=self.noOfHigh,
            noOfMedium=self.noOfMedium,
            noOfLow=self.noOfLow)

    # from class ExternalHighlight:
    def test_getPublishDate(self):
        """ Get publication date
        """
        high = self.folder.high1
        now = DateTime()
        high.setEffectiveDate(now)
        self.failIf(high.getPublishDate() != now)

    # from class ExternalHighlight:
    def test_setPublishDate(self):
        """ Set publication date
        """
        high = self.folder.high1
        now = DateTime()
        high.setPublishDate(now)
        self.failIf(high.getEffectiveDate() != now)

    # from class ExternalHighlight:
    def test_getTeaser(self):
        """ Get teaser
        """
        high = self.folder.high1
        answer = 'Description1'
        high.setDescription(answer)
        result = high.getTeaser()
        self.failIf( answer != result )

        answer = 'teaser1'
        high.setTeaser(answer)
        result = high.getTeaser()
        message = '%s != %s' % (result, answer)
        self.failIf( answer != result, message )

    # from class ExternalHighlight:
    def test_getNewsTitle(self):
        """ Get news title
        """
        high = self.folder.high1
        answer = 'Foo1'
        result = high.getNewsTitle()
        self.failIf( answer != result )

    # from class ExternalHighlight:
    def test_getMedia(self):
        """ Get media
        """
        answer = [ 'high1', 'high2' ]
        for hid in answer:
            high = getattr(self.folder, hid)
            high.setVisibilityLevel('top')
            self.workflow.doActionFor(high, 'publish')
            mediaUID = self.folder.image1.UID()
            high.setMedia(mediaUID)
            high.reindexObject()
        self.folder.high3.setVisibilityLevel('bottom')
        # upload an image for high1
        self.folder.high1.setImage(image)

        view = Frontpage(self.portal, self.app.REQUEST)
        result = [ high['media']['portal_type'] for high in view.getHigh() ]
        answer = [ 'Image', 'Image' ]
        message = '%s != %s' % (result, answer)
        self.failIf( result != answer, message )

    # from class ExternalHighlight:
    def test_getExpiryDate(self):
        """ Get expiry date
        """
        high = self.folder.high1
        now = DateTime()
        high.setExpirationDate(now)
        self.failIf(high.getExpiryDate() != now)

    # from class ExternalHighlight:
    def test_setExpiryDate(self):
        """ Set expiry date
        """
        high = self.folder.high1
        now = DateTime()
        high.setExpiryDate(now)
        result = high.getExpirationDate()
        self.failIf( result != now, result)


def test_suite():
    """ Suite
    """
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testHighlight))
    return suite


