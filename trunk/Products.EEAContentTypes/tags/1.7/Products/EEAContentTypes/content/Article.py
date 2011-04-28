# -*- coding: utf-8 -*-
#
# File: Article.py
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

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.EEAContentTypes.content.ExternalHighlight import ExternalHighlight
from Products.EEAContentTypes.content.Highlight import Highlight
from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.EEAContentTypes.config import *
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.CMFPlone import PloneMessageFactory as _

from Products.CMFCore.permissions import ModifyPortalContent
from eea.themecentre.interfaces import IThemeTagging
from Products.EEAContentTypes.content.ExternalHighlight import schema as ExtHighlightSchema
from Products.Archetypes.Schema import getNames
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *

from interfaces import IArticle


schema = Schema((
            LinesField('publication_groups',
                schemata='relations',
                vocabulary=NamedVocabulary("publications_groups"),
                languageIndependent=True,
                index="KeywordIndex:brains",
                widget=InAndOutWidget(
                    label=_(u'label_publication_groups', default=u'Publication groups'),
                    description=_(u'description_publication_groups', default=u'Fill in publication groups'),
                    i18n_domain='eea.reports',
                ),
            ),

),
)

Article_schema =  getattr(Highlight, 'schema', Schema(())).copy() + \
                  schema.copy()

fields2Move2DefaultSchemata = ['image','imageLink', 'imageCaption','imageNote']
for fieldname in getNames(ExtHighlightSchema):
    field = Article_schema[fieldname]
    if fieldname in fields2Move2DefaultSchemata:
        field.schemata = 'default'
    elif field.schemata != 'metadata':
        field.schemata = 'Front Page'

Article_schema['text'].required = True
Article_schema.moveField('image', before='imageCaption')
Article_schema.moveField('themes', before='image')

class Article(Highlight):
    """<p>Articles are very similar to Highlights: folderish news-alike pages which contains information abous specific subjects and can be 
    displayed on frontpage of a website and sent as notification as any other news-alike content type.</p>
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ExternalHighlight,'__implements__',()),) + (getattr(ATNewsItem,'__implements__',()),)
    implements(IArticle)

    # This name appears in the 'add' box
    archetype_name = 'Article'

    meta_type = 'Article'
    portal_type = 'Article'
    allowed_content_types = [] + list(getattr(ExternalHighlight, 'allowed_content_types', [])) + list(getattr(ATNewsItem, 'allowed_content_types', []))
    filter_content_types = 1
    global_allow = 1
    immediate_view = 'base_view'
    default_view = 'highlight_view'
    suppl_views = ()
    typeDescription = "Article"
    typeDescMsgId = 'description_edit_highlight'

    _at_rename_after_creation = True

    schema = Article_schema
    content_icon   = 'highlight_icon.gif'

    # LinguaPlone doesn't check base classes for mutators
    security.declareProtected(ModifyPortalContent, 'setThemes')
    def setThemes(self, value, **kw):
        """ Use the tagging adapter to set the themes. """
        value = filter(None, value)
        tagging = IThemeTagging(self)
        tagging.tags = value

registerType(Article, PROJECTNAME)



