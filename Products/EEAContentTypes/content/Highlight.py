""" Highlight """

# -*- coding: utf-8 -*-
#
# File: Highlight.py
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

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.EEAContentTypes.content.ExternalHighlight import ExternalHighlight
from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.EEAContentTypes.config import *
from Products.EEAContentTypes.content.quotation import quotation_schema

##code-section module-header #fill in your manual code here
from Products.CMFCore.permissions import ModifyPortalContent
from eea.themecentre.interfaces import IThemeTagging
from Products.EEAContentTypes.content.ExternalHighlight import schema as ExtHighlightSchema
from Products.Archetypes.Schema import getNames
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *
##/code-section module-header

from interfaces import IExternalHighlight

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Highlight_schema =  getattr(ATNewsItem, 'schema', Schema(())).copy() + \
    getattr(ExternalHighlight, 'schema', Schema(())).copy() + \
    quotation_schema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here

# put all the external highlights fields into their own schema
ExternalHighlightSchema = ExtHighlightSchema.copy()

fields2Move2DefaultSchemata = ['management_plan']
for fieldname in getNames(ExternalHighlightSchema):
    field = Highlight_schema[fieldname]
    if fieldname in fields2Move2DefaultSchemata:
        field.schemata = 'default'
    elif field.schemata != 'metadata':
        field.schemata = 'Front Page'

Highlight_schema['text'].required = True
Highlight_schema.moveField('image', before='imageCaption')
##/code-section after-schema

class Highlight(ExternalHighlight, ATNewsItem):
    """<p>Hightlights are links with descriptions presented as news on
    the website.</p>
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ExternalHighlight,'__implements__',()),) + (getattr(ATNewsItem,'__implements__',()),)
    implements(IExternalHighlight)

    # This name appears in the 'add' box
    archetype_name = 'Highlight'

    meta_type = 'Highlight'
    portal_type = 'Highlight'
    allowed_content_types = [] + list(getattr(ExternalHighlight, 'allowed_content_types', [])) + list(getattr(ATNewsItem, 'allowed_content_types', []))
    filter_content_types = 1
    global_allow = 1
    immediate_view = 'base_view'
    default_view = 'highlight_view'
    suppl_views = ()
    typeDescription = "Highlight"
    typeDescMsgId = 'description_edit_highlight'

    _at_rename_after_creation = True

    schema = Highlight_schema

    ##code-section class-header #fill in your manual code here
    content_icon   = 'highlight_icon.gif'
    ##/code-section class-header


    security.declarePublic('getPublishDate')
    def getPublishDate(self):
        return self.getEffectiveDate()

    security.declarePublic('setPublishDate')
    def setPublishDate(self, value, **kw):
        self.setEffectiveDate(value)

    getExpiryDate = ExternalHighlight.getExpiryDate
    setExpiryDate = ExternalHighlight.setExpiryDate

    # LinguaPlone doesn't check base classes for mutators
    security.declareProtected(ModifyPortalContent, 'setThemes')
    def setThemes(self, value, **kw):
        """ Use the tagging adapter to set the themes. """
        value = filter(None, value)
        tagging = IThemeTagging(self)
        tagging.tags = value


registerType(Highlight, PROJECTNAME)
# end of class Highlight

##code-section module-footer #fill in your manual code here
##/code-section module-footer



