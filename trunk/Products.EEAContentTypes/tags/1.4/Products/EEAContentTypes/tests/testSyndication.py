# -*- coding: utf-8 -*-
#
# File: testSyndication.py
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

import os
from DateTime import DateTime
from Globals import package_home
from eea.testcase.base import EEAMegaTestCase
from Products.basesyndication.interfaces import IFeedEntry
from Products.EEAContentTypes.config import product_globals

image = open(os.path.join(package_home(product_globals),'tests', 'image.png'),'rb')
image = image.read()

class TestSyndication(EEAMegaTestCase):
    """ Test-cases for syndication. """

    def afterSetUp(self):
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
        entry = IFeedEntry(self.folder.doc)
        self.assertEquals(entry.getTitle(), 'Some Document')

        entry = IFeedEntry(self.folder.event)
        self.assertEquals(entry.getTitle(), 'Some Event [Sweden]')

    def testDate(self):
        entry = IFeedEntry(self.folder.doc)
        self.assertEquals(entry.getEffectiveDate(), self.effective_date)

        entry = IFeedEntry(self.folder.event)
        self.assertEquals(entry.getEffectiveDate(), self.start_date)

    def testFolderThumb(self):
        # simulate publications which are folders
        img = self.folder[self.folder.invokeFactory('Image', id='img1', image=image, title='Simple Image')]
        entry = IFeedEntry(self.folder)
        self.failUnless('img' in entry.getBody())

    def testHighlightThumb(self):
        highlight = self.folder[self.folder.invokeFactory('Highlight', id='h1', image=image, title='Highlight')]
        entry = IFeedEntry(highlight)
        self.failUnless('img' in entry.getBody())

        
def test_suite():
    import unittest
    return  unittest.TestSuite(unittest.makeSuite(TestSyndication))
