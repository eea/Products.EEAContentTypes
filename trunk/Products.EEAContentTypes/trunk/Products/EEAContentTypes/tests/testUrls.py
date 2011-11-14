""" URLs tests
"""
from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase
from zope.component import getMultiAdapter

def link(obj):
    """ Link
    """
    return getMultiAdapter((obj, obj.REQUEST), name="url").listing_url()

def blink(brain):
    """ @@url
    """
    obj = brain.getObject()
    return getMultiAdapter((obj, obj.REQUEST),
                           name="url").listing_url(brain=brain)

class TestLinks(EEAContentTypeTestCase):
    """ Test-cases for class(es) relations. """

    def afterSetUp(self):
        """ Set up
        """
        self.setRoles('Manager')
        self.workflow = self.portal.portal_workflow
        self.folder.acl_users._doAddUser('reviewer', 'secret', ['Reviewer'], [])

        self.folder.invokeFactory('Document', id='doc')
        self.folder.invokeFactory('Promotion', id='promotion')
        self.folder.invokeFactory('Link', id='link')
        self.folder.invokeFactory('PressRelease', id='press')

        self.folder.promotion.setUrl('http://eea.europa.eu')
        self.folder.link.setRemoteUrl('http://www.google.com')

        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.workflow.doActionFor(self.folder.promotion, 'publish')
        self.workflow.doActionFor(self.folder.link, 'publish')
        self.workflow.doActionFor(self.folder.press, 'submit')
        self.workflow.doActionFor(self.folder.press, 'publish')

        self.folder.doc.reindexObject()
        self.folder.promotion.reindexObject()
        self.folder.link.reindexObject()
        self.folder.press.reindexObject()

    def checkObjects(self):
        """ Check objects
        """
        self.assertEquals(link(self.folder.doc),
                          'http://nohost/plone/Members/test_user_1_/doc')
        self.assertEquals(link(self.folder.promotion),
                          'http://eea.europa.eu')
        self.assertEquals(link(self.folder.link),
                          'http://www.google.com')
        self.assertEquals(link(self.folder.press),
                          'http://nohost/plone/Members/test_user_1_/press')

    def testAnonymous(self):
        """ Anonyous tests
        """
        self.setRoles(['Anonymous'])
        self.checkObjects()

    def testLoggedIn(self):
        """ Authenticated tests
        """
        self.setRoles(['Manager'])
        self.checkObjects()

    def testBrains(self):
        """ Catalog brains test
        """
        brains = self.portal.portal_catalog(
            getId=['doc', 'press', 'promotion', 'link'], sort_on='getId')
        self.assertEquals(blink(brains[0]),
                          'http://nohost/plone/Members/test_user_1_/doc')
        self.assertEquals(blink(brains[1]),
                          'http://www.google.com')
        self.assertEquals(blink(brains[2]),
                          'http://nohost/plone/Members/test_user_1_/press')
        self.assertEquals(blink(brains[3]),
                          'http://eea.europa.eu')

def test_suite():
    """ Suite
    """
    import unittest
    return  unittest.TestSuite(unittest.makeSuite(TestLinks))
