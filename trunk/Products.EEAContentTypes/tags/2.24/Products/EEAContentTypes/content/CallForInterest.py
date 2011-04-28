""" CallForInterest """

# -*- coding: utf-8 -*-
#
# File: CallForInterest.py
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
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.document import ATDocument
from Products.EEAContentTypes.config import *

##code-section module-header #fill in your manual code here
from Products.CMFCore.permissions import View
##/code-section module-header

schema = Schema((

    StringField(
        name='callForId',
        widget=StringWidget(
            label='Call for id',
            label_msgid='EEAContentTypes_label_callForId',
            i18n_domain='EEAContentTypes',
        ),
        required=1
    ),

    DateTimeField(
        name='closeDate',
        widget=CalendarWidget(
            label='Close date',
            label_msgid='EEAContentTypes_label_closeDate',
            i18n_domain='EEAContentTypes',
        ),
        required=1
    ),

    DateTimeField(
        name='openDate',
        widget=CalendarWidget(
            label='Open date',
            label_msgid='EEAContentTypes_label_openDate',
            i18n_domain='EEAContentTypes',
        ),
        required=1
    ),

    DateTimeField(
        name='applicationDate',
        widget=CalendarWidget(
            label='Application date',
            label_msgid='EEAContentTypes_label_applicationDate',
            i18n_domain='EEAContentTypes',
        ),
        required=1
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

CallForInterest_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
    getattr(ATDocument, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class CallForInterest(ATFolder, ATDocument):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATFolder,'__implements__',()),) + (getattr(ATDocument,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'CallForInterest'

    meta_type = 'CallForInterest'
    portal_type = 'CallForInterest'
    allowed_content_types = ['File', 'Document'] + \
            list(getattr(ATFolder, 'allowed_content_types', [])) + \
            list(getattr(ATDocument, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 1
    #content_icon = 'CallForInterest.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "CallForInterest"
    typeDescMsgId = 'description_edit_callforinterest'

    _at_rename_after_creation = True

    schema = CallForInterest_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    # Manually created methods

    security.declareProtected(View, 'getText')
    def getText(self):
        return self.getField('text').get(self)

    security.declareProtected(View, 'CookedBody')
    def CookedBody(self, stx_level='ignored'):
        return self.getText()

    def setOpenDate(self, value):
        self.setEffectiveDate(value)

    def setCloseDate(self, value):
        self.setExpirationDate(value)

    def setEffectiveDate(self, value):
        self.getField('effectiveDate').set(self, value)
        return self.getField('openDate').set(self, value)

    def setExpirationDate(self, value):
        self.getField('expirationDate').set(self, value)
        return self.getField('closeDate').set(self, value)

registerType(CallForInterest, PROJECTNAME)
# end of class CallForInterest

##code-section module-footer #fill in your manual code here
##/code-section module-footer



