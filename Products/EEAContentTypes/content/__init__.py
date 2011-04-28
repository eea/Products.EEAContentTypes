# -*- coding: utf-8 -*-
#
# File: content.py
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


##code-section init-module-header #fill in your manual code here
##/code-section init-module-header


# Subpackages
# Additional

# Classes
import CallForTender
import PressRelease
import Speech
import ExternalHighlight
import Highlight
import Article
import Promotion
import CFTRequestor
import ThemeTaggable
import CallForInterest

##code-section init-module-footer #fill in your manual code here
import FlashFile
import Event
import Link

# monkey patch, changes default value of RSSFeedRecipe.entriesWithThumbnail
from Products.PloneRSSPortlet.content import RSSFeed
RSSFeed.RSSFeedRecipeSchema['entriesWithThumbnail'].default = 10000

# monkey patch, replaces reference field of certain content types to
# an orderable reference field
from Products.EEAContentTypes.content.orderablereffield import field
from Products.EEAContentTypes.content.orderablereffield import types_and_schema

from Products.Archetypes.ClassGen import generateMethods
for type, schema in types_and_schema:
    schema.addField(field)
    schema.moveField('relatedItems', pos='bottom');
    generateMethods(type, [field])

# monkey patch, by default file is not translatable, fix this
from Products.ATContentTypes.content import file
file.ATFileSchema['file'].languageIndependent = False

from Products.ATContentTypes.content import image
image.ATImageSchema['rights'].languageIndependent = True

##/code-section init-module-footer
