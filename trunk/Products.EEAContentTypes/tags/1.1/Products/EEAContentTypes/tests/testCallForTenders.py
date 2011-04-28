# -*- coding: utf-8 -*-
#
# File: testCallForTenders.py
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
from DateTime import DateTime
##/code-section module-header

#
# Test-cases for class(es) CallForTender, CFTRequestor
#

from Testing import ZopeTestCase
from Products.EEAContentTypes.config import *
from Products.EEAConntentTypes.tests.base import EEAContentTypeTestCase

# Import the tested classes
from Products.EEAContentTypes.content.CallForTender import CallForTender
from Products.EEAContentTypes.content.CFTRequestor import CFTRequestor

##code-section module-beforeclass #fill in your manual code here
##/code-section module-beforeclass


class testCallForTenders(EEAContentTypeTestCase):
    """Test-cases for class(es) CallForTender, CFTRequestor."""

    ##code-section class-header_testCallForTenders #fill in your manual code here
    ##/code-section class-header_testCallForTenders

    def afterSetUp(self):
        pass

    # Manually created methods

    def test_CFTRequestor(self):
        self.setRoles('Manager')
        root = self.folder
        workflowTool = root.portal_workflow


        today = DateTime()
        id = root.invokeFactory(type_name='CallForTender', id="cft",
                                title='Call for tender',
                                openDate=today,
                                closeDate=today,
                                applicationDate=today )
        cft = getattr(root, id)
        workflowTool.doActionFor(cft, "open")

        # Anonymous visitor
        self.logout()

        # create some customers
        id = cft.invokeFactory(type_name='CFTRequestor', id="cust1")
        customer = getattr(cft, id)
        customer.update(title='name', firstname='firstname',
                        lastname ='lastname',
                        email= 'email@ff.ff')

        workflowTool.doActionFor(customer, "submit")
        actions = workflowTool.getActionsFor(customer)
        self.failUnless(len(actions) == 0, actions)


    def testCFIDates(self):
        self.setRoles('Manager')
        root = self.folder
        today = DateTime()
        _zone = DateTime().timezone()
        id = root.invokeFactory(type_name='CallForInterest', id="cfi",
                                title='Call for interest',
                                openDate=today,
                                closeDate=today,
                                applicationDate=today )
        cfi = getattr(root, id)
        self.failIf(today.toZone(_zone).ISO() != cfi.EffectiveDate())
        self.failIf(today != cfi.getEffectiveDate())
        self.failIf(today != cfi.effective())
        self.failIf(today != cfi.expires())
        self.failIf(today.toZone(_zone).ISO() != cfi.ExpirationDate())
        self.failIf(today != cfi.getExpirationDate())

        tomorrow = today + 1
        cfi.setCloseDate(tomorrow)
        self.failIf(tomorrow != cfi.getCloseDate())
        self.failIf(tomorrow != cfi.expires())
        self.failIf(tomorrow.toZone(_zone).ISO() != cfi.ExpirationDate())
        self.failIf(tomorrow != cfi.getExpirationDate())

        yesterday = today - 1
        cfi.setOpenDate(yesterday)
        self.failIf(yesterday != cfi.getOpenDate())
        self.failIf(yesterday != cfi.effective())        
        self.failIf(yesterday.toZone(_zone).ISO() != cfi.EffectiveDate())
        self.failIf(yesterday != cfi.getEffectiveDate())

        cfi.setExpirationDate(today)
        self.failIf(today != cfi.expires())
        self.failIf(today.toZone(_zone).ISO() != cfi.ExpirationDate())
        self.failIf(today != cfi.getExpirationDate())
        self.failIf(today != cfi.getCloseDate())

        cfi.setEffectiveDate(today)
        self.failIf(today.toZone(_zone).ISO() != cfi.EffectiveDate())
        self.failIf(today != cfi.getEffectiveDate())
        self.failIf(today != cfi.effective())
        self.failIf(today != cfi.getOpenDate())
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCallForTenders))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


