""" Content init module """

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

# Subpackages
# Additional

# Validators
from Products.validation import validation
from Products.EEAContentTypes.content.validators import (
    ManagementPlanCodeValidator,
)

validation.register(
    ManagementPlanCodeValidator('management_plan_code_validator'))

# Classes
import Products.EEAContentTypes.content.CallForTender #pyflakes
import Products.EEAContentTypes.content.PressRelease  #pyflakes
import Products.EEAContentTypes.content.Speech  #pyflakes
import Products.EEAContentTypes.content.ExternalHighlight #pyflakes
import Products.EEAContentTypes.content.Highlight #pyflakes
import Products.EEAContentTypes.content.Article #pyflakes
import Products.EEAContentTypes.content.Promotion #pyflakes
import Products.EEAContentTypes.content.CFTRequestor #pyflakes
import Products.EEAContentTypes.content.ThemeTaggable #pyflakes
import Products.EEAContentTypes.content.CallForInterest #pyflakes
import Products.EEAContentTypes.content.FlashFile #pyflakes
import Products.EEAContentTypes.content.Event #pyflakes
import Products.EEAContentTypes.content.Link #pyflakes

# monkey patch, changes default value of RSSFeedRecipe.entriesWithThumbnail
from Products.PloneRSSPortlet.content import RSSFeed
RSSFeed.RSSFeedRecipeSchema['entriesWithThumbnail'].default = 10000

# monkey patch, replaces reference field of certain content types to
# an orderable reference field
from Products.EEAContentTypes.content.orderablereffield import field
from Products.EEAContentTypes.content.orderablereffield import (
    types_and_schema,
)

from Products.Archetypes.ClassGen import generateMethods
for otype, oschema in types_and_schema:
    schema.addField(field)
    schema.moveField('relatedItems', pos='bottom')
    generateMethods(otype, [oschema])

# monkey patch, by default file is not translatable, fix this
from Products.ATContentTypes.content import file as atfile
atfile.ATFileSchema['file'].languageIndependent = False

from Products.ATContentTypes.content import image
image.ATImageSchema['rights'].languageIndependent = True
