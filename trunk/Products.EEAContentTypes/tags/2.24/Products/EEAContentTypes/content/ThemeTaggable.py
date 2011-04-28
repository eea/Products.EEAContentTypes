""" ThemeTaggable """

# -*- coding: utf-8 -*-
#
# File: ThemeTaggable.py
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
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.EEAContentTypes.config import *

try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *

##code-section module-header #fill in your manual code here
from Products.validation.config import validation
from Products.validation.interfaces import ivalidator
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent
from eea.themecentre.interfaces import IThemeTagging
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.component import getUtility

class MaxValuesValidator:
    __implements__ = (ivalidator,)

    def __init__( self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        maxValues = getattr(kwargs['field'].widget,'maxValues', None)
        value = [ val for val in value
                      if val ]
        if maxValues is not None and len(value)>maxValues:
            return "To many values, please choose max %s." % maxValues
        return 1

validation.register(MaxValuesValidator('maxValues'))
##/code-section module-header

schema = Schema((

    StringField(
        name='themes',
        validators=('maxValues',),
        widget=InAndOutWidget
        (
            maxValues=3,
            label="Themes",
            description="Choose max 3 themes",
            label_msgid='EEAContentTypes_label_themes',
            description_msgid='EEAContentTypes_help_themes',
            i18n_domain='EEAContentTypes',
        ),
        languageIndependent=True,
        vocabulary='_getMergedThemes',
        index="KeywordIndex:brains",
        enforceVocabulary=1,
        default=[],
        accessor='getThemes',
        mutator='setThemes',
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

ThemeTaggable_schema = schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class ThemeTaggable(BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseContent,'__implements__',()),)

    allowed_content_types = []
    _at_rename_after_creation = True

    schema = ThemeTaggable_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods
    def getThemes(self):
        tagging = IThemeTagging(self)
        return tagging.tags

    security.declareProtected(ModifyPortalContent, 'setThemes')
    def setThemes(self, value, **kw):
        """ Use the tagging adapter to set the themes. """
        value = filter(None, value)
        tagging = IThemeTagging(self)
        tagging.tags = value

    def _getMergedThemes(self):
        vocab = getUtility(IVocabularyFactory,
                           name="Allowed themes for edit")(self)
        return [(term.value, term.title) for term in vocab]
