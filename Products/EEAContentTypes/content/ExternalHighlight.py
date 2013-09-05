""" ExternalHighlight """

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from datetime import datetime
from eea.forms.fields.ManagementPlanField import ManagementPlanField
from eea.forms.widgets.ManagementPlanWidget import ManagementPlanWidget
from eea.themecentre.interfaces import IThemeTagging
from lxml import html
from plone.app.blob.config import blobScalesAttr
from plone.app.blob.field import BlobField
from plone.app.blob.interfaces import IBlobImageField
from plone.app.blob.mixins import ImageFieldMixin
from Products.Archetypes.Field import Image as ZODBImage
from Products.Archetypes.Field import ImageField
from Products.Archetypes import DisplayList
from Products.Archetypes.utils import shasattr
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFCore.permissions import View
from Products.CMFPlone.utils import getToolByName
from eea.themecentre.content.ThemeTaggable import ThemeTaggable
from Products.LinguaPlone import public
from Products.validation.config import validation
from Products.validation import V_REQUIRED
from Products.validation.interfaces.IValidator import IValidator
from zope.interface import implements
import logging
import difflib

logger = logging.getLogger('Products.EEAContentTypes.content.ExternalHighlight')


class ImageCaptionRequiredIfImageValidator:
    """ Image caption validator
    """
    implements(IValidator)

    def __init__( self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        image = instance.getImage()
        caption = instance.getImageCaption()
        if (image or value and value.filename) and not caption:
            return "Image caption is required for your image."
        return 1

validation.register(ImageCaptionRequiredIfImageValidator('ifImageRequired'))

class MaxValuesValidator:
    """ Max values validator
    """
    implements(IValidator)

    def __init__( self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        maxValues = getattr(kwargs['field'].widget, 'maxValues', None)
        values = value
        if isinstance(value, str):
            values = value.split(' ')
        if maxValues is not None and len(values)>maxValues:
            return "To many words, please enter max %s words." % maxValues
        return 1

validation.register(MaxValuesValidator('maxWords'))


class ExistsKeyFactsValidator:
    """ Check if markup with keyFacts class has been added and if so add a new
    key fact within a 'key-facts' directory of the given contenttype
    """
    implements(IValidator)

    def __init__( self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    @staticmethod
    def createKeyFact(fact_text, folder, keyfact_id, wft):
        folder.invokeFactory(type_name="SOERKeyFact",
                             id=keyfact_id)
        soer_keyfact = folder.get(keyfact_id)
        soer_keyfact.processForm(data=1, metadata=1, values={
            'description': (
                fact_text
            ),
        }
        )
        wft.doActionFor(soer_keyfact, 'publish')

    def __call__(self, value, instance, *args, **kwargs):

        # check if current value is same as the current value on the field
        field = kwargs.get('field')
        if field:
            raw_value = field.getRaw(instance)
            if raw_value == value:
                return 1

        # find content which has a keyFact class in order to add soer keyfacts
        content = html.fromstring(value)
        facts = content.find_class('keyFact')
        facts_length = len(facts)

        if facts_length:
            wft = getToolByName(instance, 'portal_workflow')
            if not instance.get('key-facts', None):
                instance.invokeFactory(type_name="Folder", id="key-facts")
            folder = instance.get('key-facts')
            folder_children = folder.objectValues()
            existing_facts_len = 0
            existing_facts = []
            for obj in folder_children:
                if "keyfact-" in obj.id:
                    existing_facts.append(obj)
                    existing_facts_len += 1

            for i, fact in enumerate(facts):
                keyfact_id = 'keyfact-%d' % (i + 1)
                keyfact = folder.get(keyfact_id, None)
                fact_text = fact.text_content().encode('utf-8')
                if not keyfact:
                    self.createKeyFact(fact_text, folder, keyfact_id, wft)
                else:
                    match = False
                    for child in existing_facts:
                        description = child.getField('description')
                        description_text = description.getRaw(child)
                        match_ratio = difflib.SequenceMatcher(None,
                                                              description_text,
                                                              fact_text).ratio()
                        # use standard library difflib module to check for the
                        # ratio match of the two given strings and if they
                        # have a high rate then update the keyfact description
                        if 0.85 < match_ratio < 1.0:
                            match = True
                            description.set(child, fact_text)
                            child.reindexObject(idxs=["Description"])
                        if match_ratio == 1.0:
                            match = True

                    if not match:
                        existing_facts_len += 1
                        keyfact_id = 'keyfact-%d' % existing_facts_len
                        self.createKeyFact(fact_text, folder, keyfact_id, wft)

        return 1


validation.register(ExistsKeyFactsValidator('existsKeyFacts'))


class ImageBlobField(BlobField, ImageFieldMixin):
    """ derivative of blobfield for extending schemas """
    implements(IBlobImageField)

    #BBB Backward compatible content_class property.
    #XXX This should be removed in Products.EEAContentTypes > 2.25
    _properties = BlobField._properties.copy()
    _properties.update({
        'content_class': ZODBImage
    })

    def set(self, instance, value, **kwargs):
        """ Setter
        """
        if value == "DELETE_IMAGE":
            value = "DELETE_FILE"

        super(ImageBlobField, self).set(instance, value, **kwargs)
        if hasattr(aq_base(instance), blobScalesAttr):
            delattr(aq_base(instance), blobScalesAttr)

        if value == "DELETE_FILE":
            return

        # Generate scales on edit to avoid ZODB commits on view
        sizes = self.getAvailableSizes(instance)
        for size in sizes.keys():
            self.getScale(instance, size)

    #BBB Backward compatible.
    #XXX This should be removed in Products.EEAContentTypes > 2.25
    def get(self, instance, **kwargs):
        """ Getter
        """
        value = super(ImageBlobField, self).get(instance, **kwargs)
        if (shasattr(value, '__of__', acquire=True)
            and not kwargs.get('unwrapped', False)):
            return value.__of__(instance)
        return value

    def getAvailableSizes(self, instance):
        """ Get sizes
        """
        return self.sizes

    def getScale(self, instance, scale=None, **kwargs):
        """ Scale getter
        """
        img = self.getAccessor(instance)()
        size = img.getSize()

        if not size:
            return None

        #BBB Backward compatible.
        #XXX This should be removed in Products.EEAContentTypes > 2.25
        if isinstance(img, ZODBImage):
            return ImageField.getScale(self, instance, scale, **kwargs)

        return super(ImageBlobField,
                     self).getScale(instance, scale, **kwargs)


schema = public.Schema((

    ImageBlobField('image',
        required = False,
        storage = public.AnnotationStorage(migrate=True),
        languageIndependent = True,
        swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
        pil_quality = zconf.pil_config.quality,
        pil_resize_algo = zconf.pil_config.resize_algo,
        max_size = (1280,1024),
        sizes= {'xlarge': (633, 356),
                'wide' : (325, 183 ),
                'large'   : (768, 768),
                'preview' : (400, 400),
                'mini'    : (180,135),
                'thumb'   : (128, 128),
                'tile'    :  (64, 64),
                'icon'    :  (32, 32),
                'listing' :  (16, 16),
               },
        validators = (
                    ('isNonEmptyFile', V_REQUIRED),
                    ('imageMinSize', V_REQUIRED),
                    ('checkFileMaxSize', V_REQUIRED),
                    ),
        widget = public.ImageWidget(
            description = (
                "Will be shown in the news listing, and in the news "
                "item itself. Image will be scaled to a sensible size "
                "and image width should be of minimum 1024px"),
            description_msgid = "help_news_image",
            label= "Image",
            label_msgid = "label_news_image",
            i18n_domain = "plone",
            show_content_type = False)
        ),

    public.StringField(
        name='imageLink',
        widget=public.StringWidget(
            label="Image Link",
            label_msgid="label_news_image_link",
            description="Enter a URL that the image should be linked to",
            description_msgid="help_image_link",
            i18n_domain='EEAContentTypes',
            size="40",
        ),
        validators=('isURL',),
    ),

    public.StringField(
        name='imageCaption',
        widget=public.StringWidget(
            label="Image Caption",
            description="Enter a caption for the image (max 5 words)",
            description_msgid="help_image_caption",
            label_msgid="label_image_caption",
            size="40",
            i18n_domain='EEAContentTypes',
            maxValues=5,
        ),
        i18n_domain="plone",
        searchable=True,
        validators=('maxWords',)
    ),

    public.TextField(
        name='imageNote',
        index="ZCTextIndex|TextIndex:brains",
        widget=public.TextAreaWidget(
            label="Image Note",
            description="Enter a note about this image.",
            label_msgid='EEAContentTypes_label_imageNote',
            description_msgid='EEAContentTypes_help_imageNote',
            i18n_domain='EEAContentTypes',
        )
    ),

    public.StringField(
        name='imageSource',
        index="FieldIndex:brains",
        widget=public.StringWidget(
            label="Image Source",
            description="Enter the source of this image.",
            label_msgid='EEAContentTypes_label_imageSource',
            description_msgid='EEAContentTypes_help_imageSource',
            i18n_domain='EEAContentTypes',
        )
    ),

    public.StringField(
        name='imageCopyright',
        index="FieldIndex:brains",
        widget=public.StringWidget(
            label="Image Copyright",
            description="Enter the copyright information for this image.",
            label_msgid='EEAContentTypes_label_imageCopyright',
            description_msgid='EEAContentTypes_help_imageCopyright',
            i18n_domain='EEAContentTypes',
        )
    ),

    public.ReferenceField(
        name='media',
        widget=public.ReferenceWidget(
            label='Media',
            label_msgid='EEAContentTypes_label_media',
            i18n_domain='EEAContentTypes',
        ),
        allowed_types="('ATImage','FlashFile')",
        multiValued=0,
        relationship="frontpageMedia",
        accessor="_getMedia"
    ),

    public.StringField(
        name='newsTitle',
        index_method="getNewsTitle",
        index="FieldIndex:brains",
        widget=public.StringWidget(
            label="News title",
            description=("Enter title that will be visible on the frontpage "
                         "when this highlight is listed."),
            label_msgid='EEAContentTypes_label_newsTitle',
            description_msgid='EEAContentTypes_help_newsTitle',
            i18n_domain='EEAContentTypes',
        ),
        accessor="_getNewsTitle"
    ),

    public.TextField(
        name='teaser',
        index_method="getTeaser",
        index="ZCTextIndex|TextIndex:brains",
        widget=public.TextAreaWidget(
            label="Teaser",
            description="Short informative teaser for the frontpage.",
            maxlength="600",
            label_msgid='EEAContentTypes_label_teaser',
            description_msgid='EEAContentTypes_help_teaser',
            i18n_domain='EEAContentTypes',
        ),
        accessor="_getTeaser"
    ),

    public.StringField(
        name='url',
        index="FieldIndex:brains",
        widget=public.StringWidget(
            label="External URL",
            description="Enter URL to external content.",
            label_msgid='EEAContentTypes_label_url',
            description_msgid='EEAContentTypes_help_url',
            i18n_domain='EEAContentTypes',
            visible={'edit': 'invisible', 'view': 'visible'},
        ),
        languageIndependent = True
    ),

    public.StringField(
        name='visibilityLevel',
        index="FieldIndex:brains",
        widget=public.SelectionWidget(
            label="Visibility Level",
            label_msgid='EEAContentTypes_label_visibilityLevel',
            i18n_domain='EEAContentTypes',
            visible=False, #disabled/deprecated by default for most content
        ),
        enforceVocabulary=1,
        vocabulary="getVisibilityLevels",
        languageIndependent = True
    ),

    public.DateTimeField(
        name='publishDate',
        widget=public.CalendarWidget(
            label="Publish Date",
            label_msgid="label_effective_date",
            description_msgid="help_effective_date",
            i18n_domain="plone",
            description=("Date when the content should become available on "
                         "the public site."),
        ),
        languageIndependent = True
    ),

    public.DateTimeField(
        name='expiryDate',
        index="True",
        widget=public.CalendarWidget(
            label="Expiration Date",
            description=("Date when the content should become iunavailable on "
                         "the public site."),
            label_msgid='EEAContentTypes_label_expiryDate',
            description_msgid='EEAContentTypes_help_expiryDate',
            i18n_domain='EEAContentTypes',
        ),
        languageIndependent = True
    ),

    ManagementPlanField(
        name='management_plan',
        languageIndependent=True,
        required_for_published=True,
        required=True,
        default=(datetime.now().year, ''),
        validators = ('management_plan_code_validator',),
        vocabulary_factory = u"Temporal coverage",
        widget = ManagementPlanWidget(
            format="select",
            label="EEA Management Plan",
            description=("EEA Management plan code. Internal EEA project "
                         "line code, used to assign an EEA product output to "
                         "a specific EEA project number in the "
                         "management plan."),
            label_msgid='dataservice_label_eea_mp',
            description_msgid='dataservice_help_eea_mp',
            i18n_domain='eea.dataservice',
        )
        ),

),
)

ExternalHighlight_schema = getattr(ATFolder, 'schema', public.Schema(())
    ).copy() + getattr(ThemeTaggable, 'schema', public.Schema(())
    ).copy() + schema.copy()

class ExternalHighlight(ATFolder, ThemeTaggable):
    """ External highlight
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATFolder, '__implements__', ()),) + (
        getattr(ThemeTaggable, '__implements__' ,()),
    )

    allowed_content_types = ['FlashFile', 'ATImage', 'Image', 'File'] + list(
        getattr(ATFolder, 'allowed_content_types', [])) + list(
        getattr(ThemeTaggable, 'allowed_content_types', []))
    _at_rename_after_creation = True

    schema = ExternalHighlight_schema

    # Methods

    security.declarePublic('getVisibilityLevels')
    def getVisibilityLevels(self):
        """ Visibility levels
        """
        levels = ( ('top', 'High visibility'),
                   ('middle','Medium visibility'),
                   ('bottom','Low visibility') )

        return DisplayList( levels )

    security.declarePublic('getPublishDate')
    def getPublishDate(self):
        """ Effective date getter
        """
        return self.getEffectiveDate()

    security.declarePublic('setPublishDate')
    def setPublishDate(self, value, **kw):
        """ Effective date setter
        """
        self.setEffectiveDate(value)

    security.declarePublic('getTeaser')
    def getTeaser(self):
        """ Teaser getter
        """
        return self._getTeaser() or self.Description()

    security.declarePublic('getNewsTitle')
    def getNewsTitle(self):
        """ News title getter
        """
        return  self._getNewsTitle() or self.Title()

    security.declarePublic('getMedia')
    def getMedia(self):
        """ Media getter
        """
        return self.getImage() or self._getMedia()

    security.declarePublic('getExpiryDate')
    def getExpiryDate(self):
        """ Expiration date getter
        """
        return self.getExpirationDate()

    security.declarePublic('setExpiryDate')
    def setExpiryDate(self, value, **kw):
        """ Expiration date setter
        """
        self.setExpirationDate(value)

    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)

    security.declareProtected(View, 'tag')
    def getScale(self, scale):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').getScale(self, scale)

    security.declarePublic('getThemeVocabs')
    def getThemeVocabs(self):
        """ Theme vocabularies getter
        """
        pass

    #TODO: on plone4 migration, we should use a traverser instead of this
    #also, valentine.imagescale is pluggable and could be used instead of this
    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return ATFolder.__bobo_traverse__(self, REQUEST, name)

    def setThemes(self, value, **kw):
        """ Use the tagging adapter to set the themes. """
        value = [val for val in value if val is not None]
        tagging = IThemeTagging(self)
        tagging.tags = value

