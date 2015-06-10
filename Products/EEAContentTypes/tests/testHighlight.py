""" Tests for Highlight
"""

from App.Common import package_home
from Products.CMFCore.utils import getToolByName
import os

from Products.EEAContentTypes.config import product_globals
from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase

image = open(os.path.join(
    package_home(product_globals), 'tests', 'image.png'), 'rb')
image = image.read()


class testHighlight(EEAContentTypeTestCase):
    """Test-cases for class(es) ExternalHighlight, Highlight."""

    def afterSetUp(self):
        """ Set up
        """
        highlight = {'type': 'Highlight', 'id': 'high%s', 'text': 'data%s',
                     'title': 'Foo%s',
                     'teaser': 'teaser%s'}
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
    def test_getTeaser(self):
        """ Get teaser
        """
        high = self.folder.high1
        answer = 'Description1'
        high.setDescription(answer)
        result = high.getTeaser()
        self.failIf(answer != result)

        answer = 'teaser1'
        high.setTeaser(answer)
        result = high.getTeaser()
        message = '%s != %s' % (result, answer)
        self.failIf(answer != result, message)

    # from class ExternalHighlight:
    def test_getNewsTitle(self):
        """ Get news title
        """
        high = self.folder.high1
        answer = 'Foo1'
        result = high.getNewsTitle()
        self.failIf(answer != result)


def test_suite():
    """ Suite
    """
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(testHighlight))
    return suite
