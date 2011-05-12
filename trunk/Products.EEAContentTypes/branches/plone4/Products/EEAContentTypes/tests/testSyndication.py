""" Syndication tests
"""

from App.Common import package_home
from DateTime import DateTime
from Products.EEAContentTypes.config import product_globals
from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase
from Products.basesyndication.interfaces import IFeedEntry
import os


#from eea.testcase.base import EEAMegaTestCase

image = open(os.path.join(package_home(
    product_globals), 'tests', 'image.png'), 'rb')
image = image.read()


class TestSyndication(EEAContentTypeTestCase):
    """ Test-cases for syndication. """

    def afterSetUp(self):
        """ Set up
        """
        self.setRoles('Manager')
        self.workflow = self.portal.portal_workflow
        self.effective_date = DateTime(year=2008, month=4, day=3)
        self.start_date = DateTime(year=2007, month=1, day=1)

        self.folder.invokeFactory('Document', id='doc')
        doc = self.folder.doc
        doc.setTitle('Some Document')
        doc.setEffectiveDate(self.effective_date)
        doc.reindexObject()

        self.folder.invokeFactory('QuickEvent', id='event')
        event = self.folder.event
        event.setTitle('Some Event')
        event.setLocation('Sweden')
        event.setEffectiveDate(self.effective_date)
        event.setStartDate(self.start_date)
        event.reindexObject()

    def testTitle(self):
        """ Title
        """
        entry = IFeedEntry(self.folder.doc)
        self.assertEquals(entry.getTitle(), 'Some Document')

        entry = IFeedEntry(self.folder.event)
        self.assertEquals(entry.getTitle(), 'Some Event [Sweden]')

    def testDate(self):
        """ Date
        """
        entry = IFeedEntry(self.folder.doc)
        self.assertEquals(entry.getEffectiveDate(), self.effective_date)

        entry = IFeedEntry(self.folder.event)
        self.assertEquals(entry.getEffectiveDate(), self.start_date)

    def testFolderThumb(self):
        """ Folder thumb
        """
        # simulate publications which are folders
        self.folder.invokeFactory(
            'Image', id='img1', image=image, title='Simple Image')
        entry = IFeedEntry(self.folder)
        self.failUnless('img' in entry.getBody())

    def testHighlightThumb(self):
        """ Highlight thumb
        """
        highlight = self.folder[self.folder.invokeFactory(
            'Highlight', id='h1', image=image, title='Highlight')]
        entry = IFeedEntry(highlight)
        self.failUnless('img' in entry.getBody())


def test_suite():
    """ Suite
    """
    import unittest
    return  unittest.TestSuite(unittest.makeSuite(TestSyndication))
