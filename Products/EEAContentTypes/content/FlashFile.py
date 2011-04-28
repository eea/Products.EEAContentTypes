# File: FlashFile.py
# 
# Copyright (c) 2006 by 
# Generator: ArchGenXML Version 1.4.1 svn/devel 
#            http://plone.org/products/archgenxml
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#
__author__  = '''unknown <unknown>'''
__docformat__ = 'plaintext'


from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.file import ATFile


# additional imports from tagged value 'import'
from Products.CMFCore.permissions import View

from Products.EEAContentTypes.config import *
##code-section module-header #fill in your manual code here
##/code-section module-header

from interfaces import IFlashAnimation


schema=Schema((
    IntegerField('width',
        widget=IntegerWidget(
            label='Width',
            label_msgid='EEAContentTypes_label_width',
            description_msgid='EEAContentTypes_help_width',
            i18n_domain='EEAContentTypes',
        )
    ),

    IntegerField('height',
        widget=IntegerWidget(
            label='Height',
            label_msgid='EEAContentTypes_label_height',
            description_msgid='EEAContentTypes_help_height',
            i18n_domain='EEAContentTypes',
        )
    ),

    StringField('bgcolor',
        default="",
        widget=StringWidget(
            label="Background color",
            description="The HEX code(#112233) for background color of the flash application. Default is transparent",
            label_msgid='EEAContentTypes_label_bgcolor',
            description_msgid='EEAContentTypes_help_bgcolor',
            i18n_domain='EEAContentTypes',
        )
    ),

),
)


##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

FlashFile_schema = getattr(ATFile,'schema',Schema(())) + \
    schema

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class FlashFile(ATFile):
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATFile,'__implements__',()),)
    implements(IFlashAnimation)


    # This name appears in the 'add' box
    archetype_name             = 'FlashFile'

    meta_type                  = 'FlashFile'
    portal_type                = 'FlashFile'
    allowed_content_types      = [] + list(getattr(ATFile, 'allowed_content_types', []))
    filter_content_types       = 0
    global_allow               = 1
    allow_discussion           = 0
    #content_icon               = 'FlashFile.gif'
    immediate_view             = 'flashfile_view'
    default_view               = 'flashfile_view'
    suppl_views                = ('flashfile_view', 'flashfile_noheader_view', 'flashfile_fixed_width_view', 'flashfile_popup_view', 'base_view')
    typeDescription            = "FlashFile"
    typeDescMsgId              = 'description_edit_flashfile'

    schema = FlashFile_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods

    security.declarePublic('index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ Use the chosen template to display the flash file.
        """
        
        return self()



registerType(FlashFile,PROJECTNAME)
# end of class FlashFile

##code-section module-footer #fill in your manual code here
##/code-section module-footer
