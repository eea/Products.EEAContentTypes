# -*- coding: utf-8 -*-
#
# File: testOrganisation.py
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
# Test-cases for class(es) Organisation
#

from Testing import ZopeTestCase
from Products.EEAContentTypes.config import *
from Products.EEAContentTypes.tests.EEAContentTypeTestCase import EEAContentTypeTestCase

# Import the tested classes
from Products.EEAContentTypes.browser.organisation import Organisation

##code-section module-beforeclass #fill in your manual code here
from Globals import package_home
rdfFilename = os.path.join(package_home(product_globals),'tests', 'eeastaff.rdf')

##/code-section module-beforeclass


class testOrganisation(EEAContentTypeTestCase):
    """Test-cases for class(es) Organisation."""

    ##code-section class-header_testOrganisation #fill in your manual code here
    ##/code-section class-header_testOrganisation

    def afterSetUp(self):
        pass

    # from class Organisation:
    def test_getOrgData(self):
        rdf = open(rdfFilename, 'r')
        view = Organisation(rdf, self.app.REQUEST)
        result = [ res['orgname'] for res in view.getOrgData(org='IDS') ]
        answer = [ 'IDS1', 'IDS3' ]
        message = '%s != %s' % (result, answer)
        self.failIf( result != answer, message)

    # from class Organisation:
    def test_getManagers(self):
        rdf = open(rdfFilename, 'r')
        view = Organisation(rdf, self.app.REQUEST)
        manager =view.getManager()
        result = manager['job_title']
        answer = 'Executive Director'
        message = '%s != %s' % (result, answer)
        self.failIf( result != answer, message)

    # Manually created methods


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testOrganisation))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


