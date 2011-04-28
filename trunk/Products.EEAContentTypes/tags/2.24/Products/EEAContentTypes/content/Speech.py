""" Speech """

# -*- coding: utf-8 -*-
#
# File: Speech.py
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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.EEAContentTypes.content.Highlight import Highlight
from Products.EEAContentTypes.config import *

##code-section module-header #fill in your manual code here
from Products.CMFCore.permissions import ModifyPortalContent
from eea.themecentre.interfaces import IThemeTagging
##/code-section module-header

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Speech_schema = BaseSchema.copy() + \
    getattr(Highlight, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Speech(Highlight, BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(Highlight,'__implements__',()),) + (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Speech'

    meta_type = 'Speech'
    portal_type = 'Speech'
    allowed_content_types = [] + list(getattr(Highlight, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 1
    immediate_view = 'base_view'
    default_view = 'highlight_view'
    suppl_views = ()
    typeDescription = "Speech"
    typeDescMsgId = 'description_edit_speech'

    _at_rename_after_creation = True

    schema = Speech_schema

    ##code-section class-header #fill in your manual code here
    content_icon = 'speech_icon.gif'
    ##/code-section class-header

    # Methods

    security.declarePublic('getPublishDate')
    def getPublishDate(self):
        return self.getEffectiveDate()

    security.declarePublic('setPublishDate')
    def setPublishDate(self, value, **kw):
        self.setEffectiveDate(value)

    # LinguaPlone doesn't check base classes for mutators
    security.declareProtected(ModifyPortalContent, 'setThemes')
    def setThemes(self, value, **kw):
        """ Use the tagging adapter to set the themes. """
        value = filter(None, value)
        tagging = IThemeTagging(self)
        tagging.tags = value


registerType(Speech, PROJECTNAME)
# end of class Speech

##code-section module-footer #fill in your manual code here
##/code-section module-footer



