# -*- coding: utf-8 -*-
#
# File: CFTRequestor.py
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
from Products.ATContentTypes.content.base import ATCTContent
from Products.validation.validators import ExpressionValidator
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.EEAContentTypes.config import *

##code-section module-header #fill in your manual code here
from Products.Archetypes import transaction
from Products.ATContentTypes.content.base import updateAliases

from Products.CMFCore.utils import getToolByName
import zope.interface
import zope.event
import zope.component
import zope.app.event.objectevent
from zope.publisher.interfaces.browser import IBrowserRequest
from interfaces import ICFTRequestor
##/code-section module-header

schema = Schema((

    StringField(
        name='organisation',
        widget=StringWidget(
            label="Organisation",
            label_msgid='EEAContentTypes_label_organisation',
            i18n_domain='EEAContentTypes',
        ),
        required=1
    ),

    StringField(
        name='address1',
        widget=StringWidget(
            label="Address 1",
            label_msgid='EEAContentTypes_label_address1',
            i18n_domain='EEAContentTypes',
        ),
        required=1
    ),

    StringField(
        name='address2',
        widget=StringWidget(
            label="Address 2",
            label_msgid='EEAContentTypes_label_address2',
            i18n_domain='EEAContentTypes',
        )
    ),

    StringField(
        name='city',
        City="City",
        widget=StringWidget(
            label='City',
            label_msgid='EEAContentTypes_label_city',
            i18n_domain='EEAContentTypes',
        ),
        required=1
    ),

    StringField(
        name='postCode',
        widget=StringWidget(
            label="Post Code",
            label_msgid='EEAContentTypes_label_postCode',
            i18n_domain='EEAContentTypes',
        ),
        required=1
    ),

    StringField(
        name='country',
        widget=SelectionWidget(
            label="Country",
            label_msgid='EEAContentTypes_label_country',
            i18n_domain='EEAContentTypes',
        ),
        enforceVocabulary=1,
        vocabulary=NamedVocabulary("""countries"""),
        default="default",
        validators=(ExpressionValidator('''python:value != "default"'''),),
        required=1
    ),

    StringField(
        name='phone',
        widget=StringWidget(
            label="Phone Number",
            label_msgid='EEAContentTypes_label_phone',
            i18n_domain='EEAContentTypes',
        ),
        required=1
    ),

    StringField(
        name='fax',
        widget=StringWidget(
            label="Fax Number",
            label_msgid='EEAContentTypes_label_fax',
            i18n_domain='EEAContentTypes',
        )
    ),

    StringField(
        name='email',
        widget=StringWidget(
            label="Email Address",
            label_msgid='EEAContentTypes_label_email',
            i18n_domain='EEAContentTypes',
        ),
        required=1,
        validators=('isEmail',)
    ),

    StringField(
        name='remoteHost',
        widget=StringWidget(
            label="Remote Host",
            visible={'edit': 'invisible'},
            label_msgid='EEAContentTypes_label_remoteHost',
            i18n_domain='EEAContentTypes',
        )
    ),

    StringField(
        name='remoteAddr',
        widget=StringWidget(
            label="Remote Address",
            visible={'edit': 'invisible'},
            label_msgid='EEAContentTypes_label_remoteAddr',
            i18n_domain='EEAContentTypes',
        )
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

CFTRequestor_schema = getattr(ATCTContent, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
CFTRequestor_schema['description'].schemata = 'metadata'
CFTRequestor_schema['title'].widget.label = 'Name'
##/code-section after-schema

class CFTRequestor(ATCTContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATCTContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'CFTRequestor'

    meta_type = 'CFTRequestor'
    portal_type = 'CFTRequestor'
    allowed_content_types = [] + list(getattr(ATCTContent, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 0
    #content_icon = 'CFTRequestor.gif'
    immediate_view = 'base_view'
    default_view = 'cftrequestor_anon_view'
    suppl_views = ()
    typeDescription = "CFTRequestor"
    typeDescMsgId = 'description_edit_cftrequestor'

    _at_rename_after_creation = True

    schema = CFTRequestor_schema

    ##code-section class-header #fill in your manual code here
    zope.interface.implements(ICFTRequestor)
    aliases = updateAliases(ATCTContent, { 'view' : 'base_view' })
    ##/code-section class-header

    # Methods

    # Manually created methods

    security.declarePrivate('_renameAfterCreation')
    def _renameAfterCreation(self, check_auto_id=False):
        """Renames an requestor like its UID.
        """
        transaction.savepoint(optimistic=True)
        new_id = '%s' % self.UID()
        self.setId(new_id)
        return new_id

    def objectModified(self):
        zope.event.notify(
            zope.app.event.objectevent.ObjectModifiedEvent(self))

    def reindexObject(self, **kw):
        pass
    
registerType(CFTRequestor, PROJECTNAME)
# end of class CFTRequestor

##code-section module-footer #fill in your manual code here

def submit_requestor(obj, event):
    valid = zope.component.getMultiAdapter((obj, obj.REQUEST), name='isValid')
    if valid.validate():
        obj.setRemoteAddr(obj.REQUEST.get('REMOTE_ADDR') )
        wf = getToolByName(obj, 'portal_workflow')
        actions = wf.getTransitionsFor(obj)
        if len(actions) > 0:
            wf.doActionFor(obj, 'submit')
##/code-section module-footer



