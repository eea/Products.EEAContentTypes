""" Promotion """

# -*- coding: utf-8 -*-
#
# File: Promotion.py
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


from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.CMFCore.permissions import ModifyPortalContent
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.ThemeTaggable import ThemeTaggable
from Products.EEAContentTypes.content.interfaces import IExternalPromotion
from Products.LinguaPlone.public import Schema, StringField
from Products.LinguaPlone.public import StringWidget, registerType
from eea.promotion.interfaces import IFrontpageSectionIndex
from zope.component import adapts
from zope.interface import implements

schema = Schema((

    StringField(
        name='url',
        widget=StringWidget(
            label='Url',
            label_msgid='EEAContentTypes_label_url',
            i18n_domain='EEAContentTypes',
        )
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Promotion_schema = getattr(ATNewsItem, 'schema', Schema(())).copy() + \
    getattr(ThemeTaggable, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
Promotion_schema['allowDiscussion'].schemata = 'metadata'
Promotion_schema['relatedItems'].schemata = 'metadata'
Promotion_schema['text'].schemata = 'metadata'

##/code-section after-schema

class Promotion(ATNewsItem, ThemeTaggable):
    """
    """
    security = ClassSecurityInfo()
    implements(IExternalPromotion)
    __implements__ = (getattr(ATNewsItem,'__implements__',()),) + \
            (getattr(ThemeTaggable,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Promotion'

    meta_type = 'Promotion'
    portal_type = 'Promotion'
    allowed_content_types = [] + list(getattr(ATNewsItem,
            'allowed_content_types', [])) + list(getattr(ThemeTaggable,
            'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 0
    content_icon   = 'document_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Promotion"
    typeDescMsgId = 'description_edit_promotion'

    _at_rename_after_creation = True

    schema = Promotion_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declareProtected(ModifyPortalContent, 'setThemes')
    def setThemes(self, value, **kw):
        """Manually specifing mutator, solves ticket #3972"""
        ThemeTaggable.setThemes(self, value, **kw)


registerType(Promotion, PROJECTNAME)
# end of class Promotion

##code-section module-footer #fill in your manual code here
##/code-section module-footer


class FrontpageSectionIndex(object):
    """ """
    implements(IFrontpageSectionIndex)
    adapts(IExternalPromotion)

    def __init__(self, context, request):
        """ """
        self.context = context

    def __call__(self):
        """ """
        return u'/'.join(self.context.getPhysicalPath()[:-1])
