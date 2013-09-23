""" Tests for Highlight
"""

from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase
from eea.versions.interfaces import IVersionEnhanced
from eea.versions.versions import create_version, assign_new_version_id
from zope.interface import alsoProvides
import os


class testHighlight(EEAContentTypeTestCase):
    """Test-cases for class(es) ExternalHighlight, Highlight."""

    def afterSetUp(self):
        """ Set up
        """
        self.folder.invokeFactory('Highlight', id="h1", 
                                   text="Hello world", title="Hightlight 1")

    def test_VersionModifier(self):
        """ Get publication date
        """
        high = self.folder['h1']

        #Highlights are not versionable by default, 
        #so we need to make it versionable "by hand"
        alsoProvides(high, IVersionEnhanced)
        assign_new_version_id(high, None)

        ver = create_version(high)

        rdf = high.restrictedTraverse('@@rdf')()
        self.failUnless ('<dcterms:isReplacedBy rdf:resource="' + 
               'http://nohost/plone/Members/test_user_1_/h1-1"/>' in rdf)

        rdf = ver.restrictedTraverse('@@rdf')()
        self.failUnless('<dcterms:replaces rdf:resource=' + 
                        '"http://nohost/plone/Members/test_user_1_/h1"/>' in rdf)


def test_suite():
    """ Suite
    """
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testHighlight))
    return suite
