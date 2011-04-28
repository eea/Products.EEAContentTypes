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

from Products.Five import zcml
import Products.EEAContentTypes
from Products.EEAContentTypes.tests.EEAContentTypeTestCase import EEAContentTypeTestCase

class TestMultilingual(EEAContentTypeTestCase):
    """Test cases for LinguaPlone and multilingual features."""

    def afterSetUp(self):
        zcml.load_config('configure.zcml', Products.EEAContentTypes)

    def test_smartFolderCriteria(self):
        self.setRoles(['Manager'])
        self.folder.invokeFactory('RichTopic', id='topic')
        crit = self.folder.topic.addCriterion('Creator', 'ATSimpleStringCriterion')
        crit.setValue('dummyuser')

        # translate the smart folder and check if it has the criteria
        # that was added to the original smart folder
        self.folder.topic.addTranslation('sv')
        svcrit = self.folder['topic-sv']['crit__Creator_ATSimpleStringCriterion']
        self.assertEqual(svcrit.Value(), 'dummyuser')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = makeSuite(TestMultilingual)

    from Products.PloneTestCase import layer
    from Products.PloneTestCase import setup

    if setup.USELAYER:
        if not hasattr(suite, 'layer'):
                suite.layer = layer.PloneSite

    return  TestSuite(suite)
