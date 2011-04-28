# -*- coding: utf-8 -*-
#
# File: ExternalHighlight.py
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
from Products.ATContentTypes.content.folder import ATFolder
from Products.EEAContentTypes.content.ThemeTaggable import ThemeTaggable
from Products.EEAContentTypes.config import *

##code-section module-header #fill in your manual code here
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *

from Products.ATContentTypes.configuration import zconf
from Products.Archetypes import DisplayList
from Products.CMFCore.permissions import View
from Products.validation.config import validation
from Products.validation.interfaces import ivalidator
from Products.validation import V_REQUIRED
from Products.CMFCore.utils import getToolByName

# management plan code field imports
from datetime import datetime
from eea.dataservice.fields.ManagementPlanField import ManagementPlanField
from eea.dataservice.vocabulary import DatasetYears
from eea.dataservice.widgets.ManagementPlanWidget import ManagementPlanWidget

from eea.themecentre.interfaces import IThemeTagging
class ImageCaptionRequiredIfImageValidator:
    __implements__ = (ivalidator,)

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
    __implements__ = (ivalidator,)

    def __init__( self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        maxValues = getattr(kwargs['field'].widget,'maxValues', None)
        values = value
        if isinstance(value, str):
            values = value.split(' ')
        if maxValues is not None and len(values)>maxValues:
            return "To many words, please enter max %s words." % maxValues
        return 1

validation.register(MaxValuesValidator('maxWords'))

##/code-section module-header
schema = Schema((
    
    ImageField('image',
        required = False,
        storage = AnnotationStorage(migrate=True),
        languageIndependent = True,
        max_size = (1280,1024),
        sizes= {'large'   : (768, 768),
                'preview' : (400, 400),
                'mini'    : (180,135),
                'thumb'   : (128, 128),
                'tile'    :  (64, 64),
                'icon'    :  (32, 32),
                'listing' :  (16, 16),
               },
        validators = ('isNonEmptyFile', ),
        widget = ImageWidget(
            description = "Will be shown in the news listing, and in the news item itself. Image will be scaled to a sensible size.",
            description_msgid = "help_news_image",
            label= "Image",
            label_msgid = "label_news_image",
            i18n_domain = "plone",
            show_content_type = False)
        ),

    StringField(
        name='imageLink',
        widget=StringWidget(
            label="Image Link",
            label_msgid="label_news_image_link",
            description="Enter a URL that the image should be linked to",
            description_msgid="help_image_link",
            i18n_domain='EEAContentTypes',
            size="40",
        ),
        validators=('isURL',),
    ),

    StringField(
        name='imageCaption',
        widget=StringWidget(
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

    TextField(
        name='imageNote',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Image Note",
            description="Enter a note about this image.",
            label_msgid='EEAContentTypes_label_imageNote',
            description_msgid='EEAContentTypes_help_imageNote',
            i18n_domain='EEAContentTypes',
        )
    ),

    StringField(
        name='imageSource',
        index="FieldIndex:brains",
        widget=StringWidget(
            label="Image Source",
            description="Enter the source of this image.",
            label_msgid='EEAContentTypes_label_imageSource',
            description_msgid='EEAContentTypes_help_imageSource',
            i18n_domain='EEAContentTypes',
        )
    ),

    StringField(
        name='imageCopyright',
        index="FieldIndex:brains",
        widget=StringWidget(
            label="Image Copyright",
            description="Enter the copyright information for this image.",
            label_msgid='EEAContentTypes_label_imageCopyright',
            description_msgid='EEAContentTypes_help_imageCopyright',
            i18n_domain='EEAContentTypes',
        )
    ),

    ReferenceField(
        name='media',
        widget=ReferenceWidget(
            label='Media',
            label_msgid='EEAContentTypes_label_media',
            i18n_domain='EEAContentTypes',
        ),
        allowed_types="('ATImage','FlashFile')",
        multiValued=0,
        relationship="frontpageMedia",
        accessor="_getMedia"
    ),

    StringField(
        name='newsTitle',
        index_method="getNewsTitle",
        index="FieldIndex:brains",
        widget=StringWidget(
            label="News title",
            description="Enter title that will be visible on the frontpage when this highlight is listed.",
            label_msgid='EEAContentTypes_label_newsTitle',
            description_msgid='EEAContentTypes_help_newsTitle',
            i18n_domain='EEAContentTypes',
        ),
        accessor="_getNewsTitle"
    ),

    TextField(
        name='teaser',
        index_method="getTeaser",
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Teaser",
            description="Short informative teaser for the frontpage.",
            maxlength="600",
            label_msgid='EEAContentTypes_label_teaser',
            description_msgid='EEAContentTypes_help_teaser',
            i18n_domain='EEAContentTypes',
        ),
        accessor="_getTeaser"
    ),

    StringField(
        name='url',
        index="FieldIndex:brains",
        widget=StringWidget(
            label="External URL",
            description="Enter URL to external content.",
            label_msgid='EEAContentTypes_label_url',
            description_msgid='EEAContentTypes_help_url',
            i18n_domain='EEAContentTypes',
            visible={'edit': 'invisible', 'view': 'visible'},
        ),
        languageIndependent = True
    ),

    StringField(
        name='visibilityLevel',
        index="FieldIndex:brains",
        widget=SelectionWidget(
            label="Visibility Level",
            label_msgid='EEAContentTypes_label_visibilityLevel',
            i18n_domain='EEAContentTypes',
        ),
        enforceVocabulary=1,
        vocabulary="getVisibilityLevels",
        languageIndependent = True
    ),

    DateTimeField(
        name='publishDate',
        widget=CalendarWidget(
            label="Publish Date",
            label_msgid="label_effective_date",
            description_msgid="help_effective_date",
            i18n_domain="plone",
            description="Date when the content should become available on the public site.",
        ),
        languageIndependent = True
    ),

    DateTimeField(
        name='expiryDate',
        index="True",
        widget=CalendarWidget(
            label="Expiration Date",
            description="Date when the content should become iunavailable on the public site.",
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
        vocabulary=DatasetYears(),
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

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

ExternalHighlight_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
    getattr(ThemeTaggable, 'schema', Schema(())).copy() + \
    schema.copy()
# themes is required for all news-alike content types
ExternalHighlight_schema['themes'].required = True
##code-section after-schema #fill in your manual code here
##/code-section after-schema

class ExternalHighlight(ATFolder, ThemeTaggable):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATFolder,'__implements__',()),) + (getattr(ThemeTaggable,'__implements__',()),)

    allowed_content_types = ['FlashFile', 'ATImage', 'Image', 'File'] + list(getattr(ATFolder, 'allowed_content_types', [])) + list(getattr(ThemeTaggable, 'allowed_content_types', []))
    _at_rename_after_creation = True

    schema = ExternalHighlight_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('getVisibilityLevels')
    def getVisibilityLevels(self):
        levels = ( ('top', 'High visibility'),
                   ('middle','Medium visibility'),
                   ('bottom','Low visibility') )

        return DisplayList( levels )

    security.declarePublic('getPublishDate')
    def getPublishDate(self):
        return self.getEffectiveDate()

    security.declarePublic('setPublishDate')
    def setPublishDate(self, value, **kw):
        self.setEffectiveDate(value)

    security.declarePublic('getTeaser')
    def getTeaser(self):
        """
        """
        return self._getTeaser() or self.Description()

    security.declarePublic('getNewsTitle')
    def getNewsTitle(self):
        """
        """
        return  self._getNewsTitle() or self.Title()

    security.declarePublic('getMedia')
    def getMedia(self):
        """
        """
        return self.getImage() or self._getMedia()

    security.declarePublic('getExpiryDate')
    def getExpiryDate(self):
        """
        """
        return self.getExpirationDate()

    security.declarePublic('setExpiryDate')
    def setExpiryDate(self, value, **kw):
        """
        """
        self.setExpirationDate(value)

    # Manually created methods

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
        """
        """
        pass

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
        value = filter(None, value)
        tagging = IThemeTagging(self)
        tagging.tags = value


# end of class ExternalHighlight

##code-section module-footer #fill in your manual code here
##/code-section module-footer



