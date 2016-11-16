""" GisApplication Content type
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.link import ATLink
from Products.Archetypes.atapi import TextField, RichWidget
from Products.Archetypes.atapi import Schema, registerType
from zope.interface import implements
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.interfaces import IInteractiveDashboard


schema = Schema((
    TextField(
        name='embed',
        allowable_content_types=('text/html',),
        widget=RichWidget(
            label="Embed code",
            description=("Embed code should be pasted here."),
            label_msgid='EEAContentTypes_label_embed',
            i18n_domain='eea',
            ),
        default_content_type="text/html",
        searchable=True,
        default_output_type="text/x-html-safe",
        required_for_published=False,
        required=False,
        ),

))

DASHBOARD_schema = getattr(ATLink, 'schema', Schema(())).copy() + schema

# Schema overwrites
DASHBOARD_schema['description'].required = True
DASHBOARD_schema['remoteUrl'].required = False
DASHBOARD_schema['remoteUrl'].widget.label = 'Remote url'
DASHBOARD_schema['remoteUrl'].widget.description = \
    'Remote url description'


class Dashboard(ATLink):
    """ Dashboard contenttype
    """
    security = ClassSecurityInfo()
    schema = DASHBOARD_schema
    implements(IInteractiveDashboard)

    # This name appears in the 'add' box
    archetype_name = 'Dashboard (Tableau)'
    portal_type = 'Dashboard (Tableau)'

    meta_type = 'Dashboard'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    allow_discussion = 0
    immediate_view = 'dashboard_view'
    default_view = 'dashboard_view'
    suppl_views = ()
    typeDescription = "Dashboard (Tableau)"
    typeDescMsgId = 'description_edit_dashboard'

    _at_rename_after_creation = True


registerType(Dashboard, PROJECTNAME)
