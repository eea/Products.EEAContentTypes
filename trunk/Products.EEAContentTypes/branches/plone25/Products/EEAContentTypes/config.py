""" Config
"""
from Products.CMFCore.permissions import setDefaultRoles
from Globals import DevelopmentMode

DEBUG = DevelopmentMode
PROJECTNAME = "EEAContentTypes"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
ADD_CONTENT_PERMISSIONS = {
    'CallForTender': 'Add CallForTender',
    'CFTRequestor': 'Add CFTRequestor',
    'QuickEvent': 'EEA: Add QuickEvent',
}

setDefaultRoles('Add CallForTender', ('Manager','Editor'))
setDefaultRoles('Add CFTRequestor', ('Manager'))


product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = [ 'kupu', ]

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = [ ]

# STYLESHEETS = [{'id': 'my_global_stylesheet.css'},
#              {'id': 'my_contenttype.css',
#              'expression': 'python:object.getTypeInfo().getId() == "MyType"'}]
# You can do the same with JAVASCRIPTS.
STYLESHEETS = []
JAVASCRIPTS = []

##code-section config-bottom #fill in your manual code here
ADD_CONTENT_PERMISSIONS['QuickEvent'] = 'EEA: Add QuickEvent'
setDefaultRoles('EEA: Add QuickEvent', ('Manager'))
##/code-section config-bottom

DEFAULT_PAGE_TYPES = ( 'FlashFile', 'Highlight' )
JAVASCRIPTS = [ {'id' : 'swfobject.js'},
                {'id' : 'resize.js' },
                {'id' : 'hideemail.js' } ]

DEPENDENCIES = [ 'ATVocabularyManager', ]

# URL normalizer
MAX_URL_WORDS = 5
URL_ORPHANS = 1
