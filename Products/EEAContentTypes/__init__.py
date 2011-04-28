# -*- coding: utf-8 -*-
#
# File: EEAContentTypes.py
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


# There are three ways to inject custom code here:
#
#   - To set global configuration variables, create a file AppConfig.py.
#       This will be imported in config.py, which in turn is imported in
#       each generated class and in this file.
#   - To perform custom initialisation after types have been registered,
#       use the protected code section at the bottom of initialize().
#   - To register a customisation policy, create a file CustomizationPolicy.py
#       with a method register(context) to register the policy.

from zLOG import LOG, INFO, DEBUG

LOG('EEAContentTypes', DEBUG, 'Installing Product')

try:
    import CustomizationPolicy
except ImportError:
    CustomizationPolicy = None

import patches
import langprefs
import catalog

from Globals import package_home
from Products.GenericSetup import EXTENSION, profile_registry
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore import utils as cmfutils
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore import DirectoryView
from Products.CMFPlone.utils import ToolInit
from Products.Archetypes.atapi import *
from Products.Archetypes import listTypes
from Products.Archetypes.utils import capitalize

import os, os.path

from Products.EEAContentTypes.config import *

DirectoryView.registerDirectory('skins', product_globals)
DirectoryView.registerDirectory('skins/EEAContentTypes',
                                    product_globals)

##code-section custom-init-head #fill in your manual code here
from Products.ATContentTypes.content.schemata import marshall_register
from Products.ATContentTypes.content import *
from Products.RichTopic.RichTopic import RichTopicSchema

from Products.EEAContentTypes import cache

profile_registry.registerProfile(
                    'eeacontenttypes',
                    'EEAContentTypes',
                    'Extension profile with EEA workflows and content types',
                    'profile/default',
                    'EEAContentTypes',
                    EXTENSION,
                    for_=IPloneSiteRoot)

def finalizeSchema(schema, disableRelated=False, moveDiscussion=True, moveThemeTag=True):
    """Finalizes an ATCT type schema to alter some fields
    """
    schema.moveField('relatedItems', pos='bottom')
    if disableRelated:
        schema['relatedItems'].widget.visible['edit'] = 'invisible'
    else:
        schema['relatedItems'].widget.visible['edit'] = 'visible'
        schema.moveField('relatedItems', after='text')

    if moveThemeTag:
        schema.moveField('themes', before='relatedItems')

    if moveDiscussion:
        schema['allowDiscussion'].schemata = 'metadata'
        schema.moveField('allowDiscussion', after='relatedItems')

    marshall_register(schema)
    return schema

def setupSchemas():
    from content import *
    # (schema, moveDiscussion, disableRelated, moveThemeTag)
    types = ( (Promotion.Promotion_schema, True, False, True),
              (PressRelease.PressRelease_schema, True, False, True),
              (Highlight.Highlight_schema, False, False, True),
              (event.ATEvent.schema, True, True, False),
              (Event.QuickEvent.schema, True, True, False),
              (CallForInterest.CallForInterest_schema, True, True, False),
              (CallForTender.CallForTender_schema, True, True, False),
              (CFTRequestor.CFTRequestor_schema, True, True, False),)
    for schema, moveDiscussion, disableRelated, moveThemeTag in types:
        finalizeSchema(schema, moveDiscussion=moveDiscussion, disableRelated=disableRelated, moveThemeTag=moveThemeTag)

    topic.ATTopicSchema['acquireCriteria'].widget.condition = "python:folder.getParentNode().portal_type in ('Topic', 'RichTopic')"
##/code-section custom-init-head


def initialize(context):
    ##code-section custom-init-top #fill in your manual code here
    ##/code-section custom-init-top

    # imports packages and types for registration
    import content
    import browser


    # Initialize portal content
    all_content_types, all_constructors, all_ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = all_content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = all_constructors,
        fti                = all_ftis,
        ).initialize(context)

    # Give it some extra permissions to control them on a per class limit
    for i in range(0,len(all_content_types)):
        klassname=all_content_types[i].__name__
        if not klassname in ADD_CONTENT_PERMISSIONS:
            continue

        context.registerClass(meta_type   = all_ftis[i]['meta_type'],
                              constructors= (all_constructors[i],),
                              permission  = ADD_CONTENT_PERMISSIONS[klassname])

    # Apply customization-policy, if theres any
    if CustomizationPolicy and hasattr(CustomizationPolicy, 'register'):
        CustomizationPolicy.register(context)
        print 'Customization policy for EEAContentTypes installed'

    ##code-section custom-init-bottom #fill in your manual code here
    import setup
    setupSchemas()
    ##/code-section custom-init-bottom

