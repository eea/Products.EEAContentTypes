# -*- coding: utf-8 -*-
#
# File: Install.py
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


#import os.path
#import sys
from StringIO import StringIO
#from sets import Set
#from App.Common import package_home
from Products.CMFCore.utils import getToolByName
#from Products.CMFCore.utils import manage_addTool
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from zExceptions import NotFound #, BadRequest

#from Products.Archetypes.Extensions.utils import installTypes
#from Products.Archetypes.Extensions.utils import install_subskin
#from Products.Archetypes.config import TOOL_NAME as ARCHETYPETOOLNAME
#from Products.Archetypes.atapi import listTypes
from Products.EEAContentTypes.config import PROJECTNAME
#from Products.EEAContentTypes.config import product_globals as GLOBALS

def addRoles(portal):
    roles = list(portal.acl_users.portal_role_manager.listRoleIds())
    newRoles = ['Editor', 'CommonEditor', 'ProofReader', 'ContentManager', 'WebReviewer']
    for role in newRoles:
        if role not in roles:
            portal.acl_users.portal_role_manager.addRole(role)

def install(portal, reinstall=False):
    """ External Method to install EEAContentTypes """
    out = StringIO()
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.setImportContext('profile-EEAContentTypes:eeacontenttypes')
    if reinstall:
        print >> out, "Renstallation of %s:" % PROJECTNAME
        setup_tool.runImportStep('kupu-setup')
        setup_tool.runImportStep('eeacontenttypes_various')
    else:
        print >> out, "Installation log of %s:" % PROJECTNAME
        addRoles(portal)
        print >> out, "Roles added to portal_rola_manager"
        setup_tool.runAllImportSteps()

    return out.getvalue()

def uninstall(self):
    out = StringIO()

    # try to call a workflow uninstall method
    # in 'InstallWorkflows.py' method 'uninstallWorkflows'
    try:
        uninstallWorkflows = ExternalMethod('temp', 'temp',
                                            PROJECTNAME+'.InstallWorkflows',
                                            'uninstallWorkflows').__of__(self)
    except NotFound:
        uninstallWorkflows = None

    if uninstallWorkflows:
        print >>out, 'Workflow Uninstall:'
        res = uninstallWorkflows(self, out)
        print >>out, res or 'no output'
    else:
        print >>out,'no workflow uninstall'

    # try to call a custom uninstall method
    # in 'AppInstall.py' method 'uninstall'
    try:
        auninstall = ExternalMethod('temp', 'temp',
                                   PROJECTNAME+'.AppInstall', 'uninstall')
    except NotFound:
        auninstall = None

    if auninstall:
        print >>out,'Custom Uninstall:'
        res = auninstall(self)
        if res:
            print >>out,res
        else:
            print >>out,'no output'
    else:
        print >>out,'no custom uninstall'

    return out.getvalue()

def beforeUninstall(self, reinstall, product, cascade):
    """ try to call a custom beforeUninstall method in 'AppInstall.py'
        method 'beforeUninstall'
    """
    out = StringIO()
    try:
        beforeuninstall = ExternalMethod('temp', 'temp',
                                   PROJECTNAME+'.AppInstall', 'beforeUninstall')
    except NotFound:
        beforeuninstall = []

    if beforeuninstall:
        print >>out, 'Custom beforeUninstall:'
        res = beforeuninstall(self, reinstall=reinstall
                                  , product=product
                                  , cascade=cascade)
        if res:
            print >>out, res
        else:
            print >>out, 'no output'
    else:
        print >>out, 'no custom beforeUninstall'
    return (out,cascade)

def afterInstall(self, reinstall, product):
    """ try to call a custom afterInstall method in 'AppInstall.py' method
        'afterInstall'
    """
    out = StringIO()
    try:
        afterinstall = ExternalMethod('temp', 'temp',
                                   PROJECTNAME+'.AppInstall', 'afterInstall')
    except NotFound:
        afterinstall = None

    if afterinstall:
        print >>out, 'Custom afterInstall:'
        res = afterinstall(self, product=None
                               , reinstall=None)
        if res:
            print >>out, res
        else:
            print >>out, 'no output'
    else:
        print >>out, 'no custom afterInstall'
    return out
