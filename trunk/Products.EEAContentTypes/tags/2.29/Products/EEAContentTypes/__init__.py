# -*- coding: utf-8 -*-
""" EEA Content Types
"""
import logging
logger = logging.getLogger('Products.EEAContentTypes')

import patches
import langprefs
import catalog
patches, langprefs, catalog

from Products.GenericSetup import EXTENSION, profile_registry
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore import utils as cmfutils
from Products.CMFCore import DirectoryView
from Products.Archetypes.atapi import process_types
from Products.Archetypes import listTypes
from Products.ATContentTypes.content.schemata import marshall_register
from Products.ATContentTypes.content import event, topic

from Products.EEAContentTypes.config import (
    DEFAULT_ADD_CONTENT_PERMISSION,
    ADD_CONTENT_PERMISSIONS,
    PROJECTNAME,
    product_globals
)

DirectoryView.registerDirectory('skins', product_globals)
DirectoryView.registerDirectory(
    'skins/EEAContentTypes',
    product_globals)

profile_registry.registerProfile(
    'eeacontenttypes',
    'EEAContentTypes',
    'Extension profile with EEA workflows and content types',
    'profile/default',
    'EEAContentTypes',
    EXTENSION,
    for_=IPloneSiteRoot)

def finalizeSchema(schema, disableRelated=False, moveDiscussion=True,
                   moveThemeTag=True):
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
    """ Setup schema
    """
    from content import (
        Promotion,
        PressRelease,
        Highlight,
        CallForInterest,
        CallForTender,
        CFTRequestor,
        Event
    )
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
        finalizeSchema(schema, moveDiscussion=moveDiscussion,
                       disableRelated=disableRelated, moveThemeTag=moveThemeTag)

    topic.ATTopicSchema['acquireCriteria'].widget.condition = (
        "python:folder.getParentNode().portal_type in ('Topic', 'RichTopic')")

def initialize(context):
    """ Zope 2
    """
    ##code-section custom-init-top #fill in your manual code here
    ##/code-section custom-init-top

    # imports packages and types for registration
    import content #pylint: disable-msg=W0612
    content

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
    for i in range(0, len(all_content_types)):
        klassname = all_content_types[i].__name__
        if not klassname in ADD_CONTENT_PERMISSIONS:
            continue

        context.registerClass(meta_type   = all_ftis[i]['meta_type'],
                              constructors= (all_constructors[i],),
                              permission  = ADD_CONTENT_PERMISSIONS[klassname])

    setupSchemas()
