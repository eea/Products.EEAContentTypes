# -*- coding: utf-8 -*-
#
# File: CallForTender.py
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
from Products.EEAContentTypes.content.CallForInterest import CallForInterest
from Products.EEAContentTypes.config import *

##code-section module-header #fill in your manual code here
import zope.interface
from interfaces import ICallForTender

##/code-section module-header

schema = Schema((
    ReferenceField(
        name='awardNotice',
        widget=ReferenceWidget(
            label='Award notice',
            label_msgid='EEAContentTypes_award_notice',
            i18n_domain='EEAContentTypes',
        ),
        allowed_types="('Document','File')",
        multiValued=0,
        relationship="awardNotice",
        vocabulary="getPossibleAwardNotice",
        accessor="getAwardNoticeObject"
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

CallForTender_schema = BaseFolderSchema.copy() + \
    getattr(CallForInterest, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class CallForTender(CallForInterest, BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(CallForInterest,'__implements__',()),) + (getattr(BaseFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'CallForTender'

    meta_type = 'CallForTender'
    portal_type = 'CallForTender'
    allowed_content_types = ['CFTRequestor', 'CFT Requestor', 'File', 'Document'] + list(getattr(CallForInterest, 'allowed_content_types', []))
    filter_content_types = 1
    global_allow = 1
    #content_icon = 'CallForTender.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "CallForTender"
    typeDescMsgId = 'description_edit_callfortender'

    _at_rename_after_creation = True

    schema = CallForTender_schema

    ##code-section class-header #fill in your manual code here
    zope.interface.implements(ICallForTender)
    ##/code-section class-header

    # Methods

    # Manually created methods

    def getNextDoc(self):
        return self.getField('nextDoc').get(self)

    def getPossibleAwardNotice(self, *args, **kw):
        result = [ ( self.UID(), 'none yet') ]
        docs = self.portal_catalog( path = { 'query' : '/'.join(self.getPhysicalPath()),
                                             'depth' : 1 },
                                    portal_type = ['Document','File'],
                                    review_state = 'published')
        for brain in docs:
            obj = brain.getObject()
            result.append( (obj.UID(), obj.getId()))
        return result

    def getAwardNotice(self):
        award = self.getAwardNoticeObject()
        if award is None or self == award:
            return None
        return award.UID()

registerType(CallForTender, PROJECTNAME)
# end of class CallForTender

##code-section module-footer #fill in your manual code here
##/code-section module-footer



