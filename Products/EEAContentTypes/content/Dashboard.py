""" GisApplication Content type
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.link import ATLink
from Products.Archetypes.atapi import TextField, RichWidget, TextAreaWidget
from Products.Archetypes.atapi import Schema, registerType
from zope.interface import implements
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.interfaces import IInteractiveDashboard


schema = Schema((
    TextField(
        name='embed',
        languageIndependent=True,
        searchable=True,
        required_for_published=False,
        required=False,
        allowable_content_types=('text/html',),
        default_content_type="text/html",
        default_output_type="text/x-html-safe",
        widget=TextAreaWidget(
            label="Embed code",
            description=("Tableau embed code should be pasted here."),
            label_msgid='EEAContentTypes_label_embed',
            i18n_domain='eea',),
        ),

    TextField(
        name='body',
        searchable=True,
        required_for_published=False,
        required=False,
        allowable_content_types=('text/html',),
        default_content_type="text/html",
        default_output_type="text/x-html-safe",
        widget=RichWidget(
            label="More information",
            description=("Description of methodology "
                         "and calculations behind this."),
            label_msgid='EEAContentTypes_label_body',
            i18n_domain='eea',
            ),
        ),
))

DASHBOARD_schema = getattr(ATLink, 'schema', Schema(())).copy() + schema
DASHBOARD_schema['description'].required = True
DASHBOARD_schema['remoteUrl'].required = False
DASHBOARD_schema['remoteUrl'].widget.visible = {
    "edit": "invisible", "view": "invisible"}
DASHBOARD_schema['subject'].required = True


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
