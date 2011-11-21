""" Orderable Field
"""
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.CMFCore.permissions import ModifyPortalContent
from Products.OrderableReferenceField._field import OrderableReferenceField

field = OrderableReferenceField(
    'relatedItems',
    relationship = 'relatesTo',
    multiValued = True,
    isMetadata = True,
    languageIndependent = False,
    index = 'KeywordIndex',
    write_permission = ModifyPortalContent,
    widget = ReferenceBrowserWidget(
        allow_search = True,
        allow_browse = True,
        allow_sorting = True,
        show_indexes = False,
        force_close_on_insert = True,
        label = "Related Item(s)",
        label_msgid = "label_related_items",
        description = "",
        description_msgid = "help_related_items",
        i18n_domain = "plone",
        visible = {'edit' : 'visible', 'view' : 'invisible' }
        )

    )

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.EEAContentTypes.content.Highlight import Highlight
from Products.EEAContentTypes.content.Highlight import Highlight_schema
from Products.EEAContentTypes.content.Article import Article
from Products.EEAContentTypes.content.Article import Article_schema
from Products.EEAContentTypes.content.Speech import Speech
from Products.EEAContentTypes.content.Speech import Speech_schema

types_and_schema = (
    (ATDocument, ATDocumentSchema),
    (Highlight, Highlight_schema),
    (Article, Article_schema),
    (Speech, Speech_schema)
    )
