# -*- coding: utf-8 -*-
""" Doctests
"""

from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.tests import base
from zope.app.component.hooks import setSite
import doctest
import unittest, os

#from Products.CMFSquidTool.utils import stopThreads


def createObject(parent, portal_type, oid):
    """ Create object
    """
    parent.invokeFactory(portal_type, id=oid)
    newobj = getattr(parent, oid, None)
    if newobj is not None:
        newobj.reindexObject()


class TestCase(base.EEAContentTypeFunctionalTestCase):
    """ Test case
    """
    def afterSetUp(self):
        """ Set up
        """
        setSite(self.portal)
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Folder', id='folder')
        self.portal.invokeFactory('Folder', id='themes')
        self.createObject = createObject

        createObject(self.portal, 'Document', 'doc1')
        createObject(self.portal, 'File', 'video1')
        createObject(self.portal, 'Document', 'backref1')

        path = os.path.join(os.path.dirname(__file__), 'barsandtones.flv')
        zfile = open(path, 'r')
        self.portal.video1.setFile(zfile)
        zfile.close()
        # mimetype isn't set automatically
        f = self.portal.video1.getPrimaryField().getAccessor(
            self.portal.video1)()
        f.setContentType('video/x-flv')
        config = self.portal.video1.restrictedTraverse('@@video-config.html')
        config.media_activated = True

        user = self.portal.portal_membership.getAuthenticatedMember()
        user.setProperties(email='test@tester.com')

        # make all themes public (non deprecated)
        for theme in self.portal.portal_vocabularies.themes.objectValues():
            self.portal.portal_workflow.doActionFor(theme, 'publish')


class DummyResponse(object):
    """ Fake RESPONSE
    """
    def redirect(self, url):
        """ Redirect
        """
        pass


class PromotionTestCase(base.EEAContentTypeFunctionalTestCase):
    """ Test case for Promotion
    """
    def afterSetUp(self):
        """  Set up
        """
        from zope.publisher.browser import TestRequest
        from eea.design.browser.frontpage import Frontpage
        portal = self.portal
        wf = portal.portal_workflow

        # Create the 'spotlight' and 'multimedia' promotion categories:
        self.setRoles(['Manager'])
        portal.SITE.invokeFactory('Folder', id='quicklinks')
        portal.SITE.quicklinks.invokeFactory(
            'Folder', id='spotlight', title=u'Spotlight')
        portal.SITE.quicklinks.invokeFactory(
            'Folder', id='multimedia', title=u'Multimedia')
        portal.SITE.reindexObject()
        portal.SITE.quicklinks.reindexObject()
        portal.SITE.quicklinks.spotlight.reindexObject()
        portal.SITE.quicklinks.multimedia.reindexObject()
        wf.doActionFor(portal.SITE, 'publish')
        wf.doActionFor(portal.SITE.quicklinks, 'publish')
        wf.doActionFor(portal.SITE.quicklinks.spotlight, 'publish')
        wf.doActionFor(portal.SITE.quicklinks.multimedia, 'publish')

        # Also make sure promotion categories with non-ascii titles work:
        portal.SITE.quicklinks.invokeFactory(
            'Folder', id='mat', title=u'Räksmörgås')
        wf.doActionFor(portal.SITE.quicklinks.mat, 'publish')

        # Set up the frontpage:
        portal_properties = getToolByName(portal, 'portal_properties')
        frontpage_properties = getattr(portal_properties,
                                       'frontpage_properties')
        frontpage_properties.manage_changeProperties(
            promotionFolder='/plone/SITE/quicklinks')

        request = TestRequest()
        request.RESPONSE = DummyResponse()
        frontpage = Frontpage(self.portal, request)

        # Create a news item:
        self.setRoles(['Manager'])
        nid = portal.invokeFactory('News Item', id='test')
        item = portal[nid]
        item.setTitle(u'Foobar')
        wf.doActionFor(item, 'publish')

        self.item = item
        self.frontpage = frontpage
        self.request = request

def test_suite():
    """ Suite """
    from Testing.ZopeTestCase import FunctionalDocFileSuite

    return unittest.TestSuite((
        FunctionalDocFileSuite('related.txt',
                    package='Products.EEAContentTypes.browser',
                    test_class=TestCase,
                    optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                    ),
        FunctionalDocFileSuite('promotion.txt',
                    package='Products.EEAContentTypes',
                    test_class=PromotionTestCase,
                    optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                    ),
        FunctionalDocFileSuite('workflow.txt',
                    test_class=TestCase,
                    package='Products.EEAContentTypes',
                    optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                    ),
        FunctionalDocFileSuite('transitions.txt',
                    test_class=TestCase,
                    package='Products.EEAContentTypes',
                    optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                    ),
        FunctionalDocFileSuite('language.txt',
                    test_class=base.EEAContentTypeFunctionalTestCase,
                    package='Products.EEAContentTypes.browser',
                    optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                    ),
        ))
