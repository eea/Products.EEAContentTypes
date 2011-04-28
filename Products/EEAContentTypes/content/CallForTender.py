""" CallForTender """

# -*- coding: utf-8 -*-

__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.EEAContentTypes.config import *
from Products.EEAContentTypes.content.CallForInterest import CallForInterest
from interfaces import ICallForTender
import zope.interface


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


CallForTender_schema = BaseFolderSchema.copy() + \
    getattr(CallForInterest, 'schema', Schema(())).copy() + \
    schema.copy()


class CallForTender(CallForInterest, BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(CallForInterest,'__implements__',()),) + (getattr(BaseFolder,'__implements__',()),)

    archetype_name = 'CallForTender'

    meta_type = 'CallForTender'
    portal_type = 'CallForTender'
    allowed_content_types = ['CFTRequestor', 'CFT Requestor', 'File', 'Document'] + \
            list(getattr(CallForInterest, 'allowed_content_types', []))
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

    zope.interface.implements(ICallForTender)


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

    security.declarePublic("getAwardNotice")
    def getAwardNotice(self):
        """Returns award notice UID"""
        award = self.getAwardNoticeObject()
        if award is None or self == award:
            return None
        return award.UID()

    security.declareProtected("Modify content", "setAwardNotice")
    def setAwardNotice(self, values, field):
        field = self.schema[field]
        field.set(self, values)

registerType(CallForTender, PROJECTNAME)
