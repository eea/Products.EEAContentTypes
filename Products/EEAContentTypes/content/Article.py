""" Article """
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.Archetypes.Schema import getNames
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone import log
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.ExternalHighlight import ExternalHighlight
from Products.EEAContentTypes.content.ExternalHighlight import schema as \
     ExtHighlightSchema
from Products.EEAContentTypes.content.Highlight import Highlight
from Products.EEAContentTypes.content.interfaces import IArticle
from eea.rdfmarshaller.interfaces import(
    IArchetype2Surf, ISurfSession, IATField2Surf
)
from eea.rdfmarshaller.marshaller import ATCT2Surf
from eea.themecentre.interfaces import IThemeTagging
from zope.component import adapts, queryMultiAdapter
from zope.interface import implements
import sys
import rdflib
from Products.LinguaPlone.public import (
    Schema, LinesField, InAndOutWidget, registerType)

schema = Schema((
    LinesField(
        'publication_groups',
        schemata='categorization',
        vocabulary=NamedVocabulary("publications_groups"),
        languageIndependent=True,
        index="KeywordIndex:brains",
        widget=InAndOutWidget(
            label=_(u'Publication groups'),
         description=_(u'Fill in publication groups'),
            i18n_domain='eea',
            ),
        ),
),
)

Article_schema = getattr(Highlight, 'schema', Schema(())).copy() + \
                  schema.copy()

fields2Move2DefaultSchemata = ['management_plan', 'image', 'imageLink',
                               'imageCaption', 'imageNote']
for fieldname in getNames(ExtHighlightSchema):
    field = Article_schema[fieldname]
    if fieldname in fields2Move2DefaultSchemata:
        field.schemata = 'default'
    elif field.schemata != 'metadata':
        field.schemata = 'Front Page'

Article_schema['text'].required = True
Article_schema.moveField('image', before='imageCaption')
Article_schema.moveField('themes', before='image')

#visibility level is "deprecated/hidden" by default
# used on feature article 
Article_schema["visibilityLevel"].widget.visible = True

class Article(Highlight):
    """
    Articles are very similar to Highlights: folderish news-alike
    pages which contains information abous specific subjects and can be
    displayed on frontpage of a website and sent as notification as any other
    news-alike content type.
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ExternalHighlight, '__implements__', ()),) + (
        getattr(ATNewsItem, '__implements__', ()),)
    implements(IArticle)

    # This name appears in the 'add' box
    archetype_name = 'Article'

    meta_type = 'Article'
    portal_type = 'Article'
    allowed_content_types = [] + list(getattr(
        ExternalHighlight, 'allowed_content_types', [])) + list(
            getattr(ATNewsItem, 'allowed_content_types', []))
    filter_content_types = 1
    global_allow = 1
    immediate_view = 'base_view'
    default_view = 'highlight_view'
    suppl_views = ()
    typeDescription = "Article"
    typeDescMsgId = 'description_edit_highlight'

    _at_rename_after_creation = True

    schema = Article_schema
    content_icon = 'highlight_icon.gif'

    # LinguaPlone doesn't check base classes for mutators
    security.declareProtected(ModifyPortalContent, 'setThemes')
    def setThemes(self, value, **kw):
        """ Use the tagging adapter to set the themes. """
        #value = filter(None, value)
        value = [val for val in value if val]
        tagging = IThemeTagging(self)
        tagging.tags = value

registerType(Article, PROJECTNAME)


class Article2Surf(ATCT2Surf):
    """Override the ATCT2Surf adapter because the media field accessor doesn't
    return the real values;

    NOTE: It should not be necessary to copy so much code from
    eea.rdfmarshaller, but there's no 3 way adapter for (contenttype,
    fieldtype, surfsession) that would solve the problem.
    """
    implements(IArchetype2Surf)
    adapts(IArticle, ISurfSession)

    def _schema2surf(self):
        """ Surf
        """
        context = self.context
        #session = self.session
        resource = self.surfResource
        language = context.Language()
        for fld in context.Schema().fields():
            fieldName = fld.getName()
            if fieldName in self.blacklist_map:
                continue
            fieldAdapter = queryMultiAdapter((fld, self.session),
                                             interface=IATField2Surf)
            if fieldAdapter.exportable:
                if fieldName != "media":
                    value = fieldAdapter.value(context)
                else:
                    value = context.getMedia()
                if (value and value != "None") or \
                        (isinstance(value, basestring) and value.strip()) :
                    prefix = self.prefix
                    if isinstance(value, (list, tuple)):
                        value = list(value)
                    else:
                        value = (str(value), language)
                    if fieldName in self.field_map:
                        fieldName = self.field_map.get(fieldName)
                    elif fieldName in self.dc_map:
                        fieldName = self.dc_map.get(fieldName)
                        prefix = 'dcterms'
                    try:
                        setattr(resource, '%s_%s' % (prefix, fieldName), value)
                    except Exception:
                        log.log('RDF marshaller error for context[field] '
                                '"%s[%s]": \n%s: %s' % (
                                    context.absolute_url(), fieldName,
                                    sys.exc_info()[0],
                                    sys.exc_info()[1]),
                                severity=log.logging.WARN)
        parent = getattr(aq_inner(context), 'aq_parent', None)
        if parent is not None:
            resource.dcterms_isPartOf = rdflib.URIRef(parent.absolute_url())
        resource.save()
        return resource

