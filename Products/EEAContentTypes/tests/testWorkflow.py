# -*- coding: utf-8 -*-
#
# File: testWorkflow.py
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

from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase
from AccessControl.SecurityManagement import getSecurityManager

class TestWorkflow(EEAContentTypeTestCase):
    """ Test-cases for class(es) workflow. """

    def afterSetUp(self):
        self.workflow = self.portal.portal_workflow
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])
        
        self.folder.invokeFactory('Document', id='doc')        
        self.setRoles('Manager')
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.historyMarker = '<td class="state-published">Publish</td>'

    def testAnonymous(self):
	self.logout()
	res = self.folder.doc.workflow_action_message(type='document', editUrl='url').find(self.historyMarker)
	self.assertEquals(res, -1)
	res1 = self.folder.doc.workflow_confirmation_message(type='document').find(self.historyMarker)
	self.assertEquals(res1, -1)

    def testManager(self):
	self.login('manager')
	res = self.folder.doc.workflow_action_message(type='document', editUrl='url').find(self.historyMarker)
	self.failIf(res == -1)
	res1 = self.folder.doc.workflow_confirmation_message(type='document').find(self.historyMarker)
	self.failIf(res1 == -1)

def test_suite():
    import unittest
    return  unittest.TestSuite(unittest.makeSuite(TestWorkflow))
