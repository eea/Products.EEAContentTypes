""" CFTRequestor
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.Archetypes.atapi import Schema, StringField, StringWidget
from Products.Archetypes.atapi import SelectionWidget, registerType
from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.config import  PROJECTNAME
from Products.validation.validators import ExpressionValidator
from Products.EEAContentTypes.content.interfaces import ICFTRequestor
from zope.component import getMultiAdapter
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent
import transaction


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

CFTRequestor_schema = getattr(ATCTContent, 'schema', Schema(())).copy() + \
    schema.copy()

CFTRequestor_schema['description'].schemata = 'metadata'
CFTRequestor_schema['title'].widget.label = 'Name'

class CFTRequestor(ATCTContent):
    """ CFT Requestor
    """
    security = ClassSecurityInfo()

    # This name appears in the 'add' box
    archetype_name = 'CFTRequestor'

    meta_type = 'CFTRequestor'
    portal_type = 'CFTRequestor'
    allowed_content_types = [] + list(
        getattr(ATCTContent, 'allowed_content_types', []))
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

    implements(ICFTRequestor)

    security.declarePrivate('_renameAfterCreation')
    def _renameAfterCreation(self, check_auto_id=False):
        """Renames an requestor like its UID.
        """
        transaction.savepoint(optimistic=True)
        new_id = '%s' % self.UID()
        self.setId(new_id)
        return new_id

    def objectModified(self):
        """ Object modified
        """
        notify(ObjectModifiedEvent(self))

    def reindexObject(self, **kw):
        """ Reindex
        """
        return

registerType(CFTRequestor, PROJECTNAME)


def submit_requestor(obj, event):
    """ Submit requestor
    """
    valid = getMultiAdapter((obj, obj.REQUEST), name='isValid')
    if valid.validate():
        obj.setRemoteAddr(obj.REQUEST.get('REMOTE_ADDR'))
        wf = getToolByName(obj, 'portal_workflow')
        actions = wf.getTransitionsFor(obj)
        if len(actions) > 0:
            wf.doActionFor(obj, 'submit')
