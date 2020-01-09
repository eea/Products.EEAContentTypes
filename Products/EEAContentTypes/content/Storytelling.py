""" Storytelling
"""
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder, document
from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.content.interfaces import IStorytelling
from Products.EEAContentTypes.config import PROJECTNAME
from Products.validation import V_REQUIRED
from eea.themecentre.content.ThemeTaggable import ThemeTaggable
from eea.relations.field.referencefield import EEAReferenceField
from eea.relations.widget.referencewidget import EEAReferenceBrowserWidget

SCHEMA = atapi.Schema((
            atapi.TextField(
                schemata='default',
                name='story_titles',
                languageIndependent=False,
                searchable=True,
                required_for_published=False,
                required=True,
                allowable_content_types=('text/plain',),
                default_content_type='text/plain',
                default_output_type='text/plain',
                widget=atapi.TextAreaWidget(
                    label='Story titles',
                    description=('Story titles, one per line.'),
                    label_msgid='EEAContentTypes_label_embed',
                    i18n_domain='eea',),
            ),
            atapi.TextField(
                schemata='default',
                name='full_story_description',
                languageIndependent=False,
                searchable=True,
                required_for_published=False,
                required=False,
                allowable_content_types=('text/html',),
                default_content_type='text/html',
                default_output_type='text/x-html-safe',
                widget=atapi.RichWidget(
                    label='Full story description',
                    description=('Full story description should be added here.'),
                    label_msgid='EEAContentTypes_label_full_story_description',
                    i18n_domain='eea',
                    rows=10,),
            ),
            EEAReferenceField('relatedItems',
                schemata='categorization',
                relationship='relatesTo',
                multiValued=True,
                languageIndependent=True,
                keepReferencesOnCopy=True,
                validators = (('maxRelatedItems', V_REQUIRED),),
                widget=EEAReferenceBrowserWidget(
                    label='Related items',
                    description='Specify relations to other content within Plone.')
            ),
         ))

STORYTELLING_schema = folder.ATFolderSchema.copy() + \
                      document.ATDocumentSchema.copy() + \
                      getattr(ThemeTaggable, 'schema', atapi.Schema(())).copy() + \
                      SCHEMA.copy()

#STORYTELLING_schema['text'].widget.label = 'Story description'


class Storytelling(folder.ATFolder, document.ATDocumentBase, ThemeTaggable):
    """ Storytelling content type
    """
    security = ClassSecurityInfo()
    schema = STORYTELLING_schema
    implements(IStorytelling)
    meta_type = "Storytelling"
    portal_type = "Storytelling"
    archetypes_name = "Storytelling"
    filter_content_types = 0
    allowed_content_types = []
    global_allow = 0
    allow_discussion = 0
    immediate_view = 'storytelling_view'
    default_view = 'storytelling_view'
    suppl_views = ()
    typeDescription = "Storytelling"
    typeDescMsgId = 'description_edit_storytelling'

    _at_rename_after_creation = True

    def getRelatedItemsRaw(self):
        """ Return ordered related items list
        """
        result = []
        field = self.getField('relatedItems')
        raw_items = field.getRaw(self)
        ctool = getToolByName(self, 'portal_catalog')

        for uid in raw_items:
            brain = ctool.unrestrictedSearchResults(UID=uid, show_inactive=True)
            if brain:
                result.append({'url': brain[0].getURL(),
                               'title': brain[0].Title, 'brain': brain[0],
                               'uid': uid})

        return result

    def getRelatedImage(self, obj):
        brains = obj.getFolderContents(contentFilter={'portal_type':'Image'})
        if (len(brains) > 0):
            image = brains[0].getObject()
            images = image.restrictedTraverse("@@images", False)
            if images:
                return images.scale("image", "large")
            else:
                return False
        else:
            if obj.portal_type == 'Assessment':
                return {'width': 768, 'height': 488}
            else:
                return False

    def isRelatedPublished(self, obj):
        wftool = getToolByName(obj, 'portal_workflow')
        state = wftool.getInfoFor(obj, 'review_state', None)
        return state

atapi.registerType(Storytelling, PROJECTNAME)
