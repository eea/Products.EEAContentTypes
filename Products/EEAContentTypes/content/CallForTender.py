""" CallForTender """
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import (
    Schema, ReferenceField, ReferenceWidget, BaseFolderSchema, BaseFolder,
    registerType
)
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.CallForInterest import CallForInterest
from Products.EEAContentTypes.content.interfaces import ICallForTender
import zope.interface


schema = Schema((
    ReferenceField(
        name='awardNotice',
        widget=ReferenceWidget(
            label='Award notice',
            label_msgid='EEAContentTypes_award_notice',
            i18n_domain='EEAContentTypes',
            helper_js = ("callfortender_widget.js",)
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
    """ Call for tenders
    """
    security = ClassSecurityInfo()
    archetype_name = 'CallForTender'

    meta_type = 'CallForTender'
    portal_type = 'CallForTender'
    allowed_content_types = [
        'CFTRequestor', 'CFT Requestor', 'File', 'Document'] + list(getattr(
            CallForInterest, 'allowed_content_types', []))
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
        """ Next doc
        """
        return self.getField('nextDoc').get(self)

    def getPossibleAwardNotice(self, *args, **kw):
        """ Award notice
        """
        result = [ ( self.UID(), 'none yet') ]
        docs = self.portal_catalog(
            path = {
                'query' : '/'.join(self.getPhysicalPath()),
                'depth' : 1 },
            portal_type = ['Document','File'],
            review_state = 'published'
        )
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

    def setAwardNotice(self, values, field):
        """ Set award notice UID
        """
        field = self.schema[field]
        field.set(self, values)

registerType(CallForTender, PROJECTNAME)
