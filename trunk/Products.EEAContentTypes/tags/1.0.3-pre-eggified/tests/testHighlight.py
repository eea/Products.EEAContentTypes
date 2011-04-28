# -*- coding: utf-8 -*-
#
# File: testHighlight.py
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

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

##code-section module-header #fill in your manual code here
##/code-section module-header

#
# Test-cases for class(es) ExternalHighlight
#

from Testing import ZopeTestCase
from Products.EEAContentTypes.config import *
from Products.EEAContentTypes.tests.EEAContentTypeTestCase import EEAContentTypeTestCase

# Import the tested classes
from Products.EEAContentTypes.content.ExternalHighlight import ExternalHighlight
from Products.CMFCore.utils import getToolByName

##code-section module-beforeclass #fill in your manual code here
from Products.EEAContentTypes.browser.frontpage import Frontpage
from Globals import package_home
from DateTime import DateTime

image = open(os.path.join(package_home(product_globals),'tests', 'image.png'),'rb')
image = image.read()
##/code-section module-beforeclass


class testHighlight(EEAContentTypeTestCase):
    """Test-cases for class(es) ExternalHighlight, Highlight."""

    ##code-section class-header_testHighlight #fill in your manual code here
    ##/code-section class-header_testHighlight

    def afterSetUp(self):
        highlight = {'type': 'Highlight', 'id' : 'high%s', 'text' : 'data%s',
                     'title' : 'Foo%s',
                     'teaser' : 'teaser%s'}
        for i in range(15):
            id=highlight['id'] % i
            text = highlight['text'] % i
            title = highlight['title'] % i
            self.folder.invokeFactory('Highlight', id=id, text=text,
                                      title=title)


        self.folder.invokeFactory('Image', id='image1', image=image, title='Image title')
        self.workflow = self.portal.portal_workflow
        self.setRoles('Manager')
        portal_properties = getToolByName(self.portal, 'portal_properties')
        frontpage_properties = getattr(portal_properties, 'frontpage_properties')
        self.noOfHigh = 3
        self.noOfMedium = 4
        self.noOfLow = 10
        frontpage_properties.manage_changeProperties(noOfHigh=self.noOfHigh,noOfMedium=self.noOfMedium,noOfLow=self.noOfLow)
        
    # from class ExternalHighlight:
    def test_getVisibilityLevels(self):
        pass

    # from class ExternalHighlight:
    def test_getPublishDate(self):
        high = self.folder.high1
        now = DateTime()
        high.setEffectiveDate(now)
        self.failIf(high.getPublishDate() != now)

    # from class ExternalHighlight:
    def test_setPublishDate(self):
        high = self.folder.high1
        now = DateTime()
        high.setPublishDate(now)
        self.failIf(high.getEffectiveDate() != now)

    # from class ExternalHighlight:
    def test_getTeaser(self):
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
        high = self.folder.high1
        answer = 'Foo1'
        result = high.getNewsTitle()
        self.failIf( answer != result )

    # from class ExternalHighlight:
    def test_getMedia(self):
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
        high = self.folder.high1
        now = DateTime()
        high.setExpirationDate(now)
        self.failIf(high.getExpiryDate() != now)

    # from class ExternalHighlight:
    def test_setExpiryDate(self):
        high = self.folder.high1
        now = DateTime()
        high.setExpiryDate(now)
        result = high.getExpirationDate()
        self.failIf( result != now, result)

    # Manually created methods

    def test_getRelatedThemes(self):
        pass

    def test_getThemeVocabs(self):
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testHighlight))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


