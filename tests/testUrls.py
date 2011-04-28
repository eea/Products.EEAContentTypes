# -*- coding: utf-8 -*-
#
# File: testFrontpage.py
#
# Copyright (c) 2006 by []
# Generator: ArchGenXML Version 1.5.1-svn
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

from Products.EEAContentTypes.tests.EEAContentTypeTestCase import EEAContentTypeTestCase
from Products.EEAContentTypes.interfaces import IRelations
from eea.themecentre.interfaces import IThemeTagging
from zope.app.component.hooks import setSite
from zope.component import getMultiAdapter

def link(obj):
    return getMultiAdapter((obj, obj.REQUEST), name="url").listing_url()

def blink(brain):
    obj = brain.getObject()
    return getMultiAdapter((obj, obj.REQUEST), name="url").listing_url(brain=brain)

class TestLinks(EEAContentTypeTestCase):
    """ Test-cases for class(es) relations. """

    def afterSetUp(self):
        #setSite(self.portal)
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
        self.assertEquals(link(self.folder.doc), 'http://nohost/plone/Members/test_user_1_/doc')
        self.assertEquals(link(self.folder.promotion), 'http://eea.europa.eu')
        self.assertEquals(link(self.folder.link), 'http://www.google.com')
        self.assertEquals(link(self.folder.press), 'http://nohost/plone/Members/test_user_1_/press')

    def testAnonymous(self):
        self.setRoles(['Anonymous'])
        self.checkObjects()

    def testLoggedIn(self):
        self.setRoles(['Manager'])
        self.checkObjects()

    def testBrains(self):
        brains = self.portal.portal_catalog(getId=['doc', 'press', 'promotion', 'link'],
                                            sort_on='getId')
        self.assertEquals(blink(brains[0]), 'http://nohost/plone/Members/test_user_1_/doc')
        self.assertEquals(blink(brains[1]), 'http://www.google.com')
        self.assertEquals(blink(brains[2]), 'http://nohost/plone/Members/test_user_1_/press')
        self.assertEquals(blink(brains[3]), 'http://eea.europa.eu')

def test_suite():
    import unittest
    return  unittest.TestSuite(unittest.makeSuite(TestLinks))
