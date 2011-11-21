""" PressRelease """

# -*- coding: utf-8 -*-
#
# File: PressRelease.py
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
from Products.EEAContentTypes.content.Highlight import Highlight
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.quotation import quotation_schema

##code-section module-header #fill in your manual code here
try:
    from Products.LinguaPlone.public import (Schema, BaseSchema,
            BaseContent, registerType)
    Schema, BaseSchema, BaseContent, registerType

except ImportError:
    # No multilingual support
    from Products.Archetypes.public import (Schema, BaseSchema,
            BaseContent, registerType)


from Products.CMFCore.permissions import ModifyPortalContent
from eea.themecentre.interfaces import IThemeTagging
##/code-section module-header

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PressRelease_schema = BaseSchema.copy() + \
    getattr(Highlight, 'schema', Schema(())).copy() + \
    quotation_schema.copy() + \
    schema.copy()


class PressRelease(Highlight, BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(Highlight, '__implements__', ()),) + (getattr(BaseContent, '__implements__', ()),)

    # This name appears in the 'add' box
    archetype_name = 'Press Release'

    meta_type = 'PressRelease'
    portal_type = 'PressRelease'
    allowed_content_types = [] + list(getattr(Highlight, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 1
    immediate_view = 'base_view'
    default_view = 'pressrelease_view'
    suppl_views = ()
    typeDescription = "Press Release"
    typeDescMsgId = 'description_edit_pressrelease'

    _at_rename_after_creation = True

    schema = PressRelease_schema

    ##code-section class-header #fill in your manual code here
    content_icon = 'press-release_icon.gif'
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
        #value = filter(None, value)
        value = [val for val in value if val]
        tagging = IThemeTagging(self)
        tagging.tags = value


registerType(PressRelease, PROJECTNAME)
# end of class PressRelease

##code-section module-footer #fill in your manual code here
##/code-section module-footer



