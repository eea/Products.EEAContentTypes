""" Content init module """

# Validators
import Products.EEAContentTypes.content.validators

# Classes
import Products.EEAContentTypes.content.Article
import Products.EEAContentTypes.content.CFTRequestor
import Products.EEAContentTypes.content.CallForInterest
import Products.EEAContentTypes.content.CallForTender
import Products.EEAContentTypes.content.Event
import Products.EEAContentTypes.content.ExternalHighlight
import Products.EEAContentTypes.content.FlashFile
import Products.EEAContentTypes.content.CloudVideo
import Products.EEAContentTypes.content.GISApplication
import Products.EEAContentTypes.content.Highlight
import Products.EEAContentTypes.content.Link
import Products.EEAContentTypes.content.PressRelease
import Products.EEAContentTypes.content.Promotion
import Products.EEAContentTypes.content.Speech
import Products.EEAContentTypes.content.ThemeTaggable

# monkey patch, replaces reference field of certain content types to
# an orderable reference field
from Products.EEAContentTypes.content.orderablereffield import field
from Products.EEAContentTypes.content.orderablereffield import (
    types_and_schema,
)

from Products.Archetypes.ClassGen import generateMethods
for otype, schema in types_and_schema:
    schema.addField(field)
    schema.moveField('relatedItems', pos='bottom')
    generateMethods(otype, [field])

# monkey patch, by default file is not translatable, fix this
from Products.ATContentTypes.content import file as atfile
atfile.ATFileSchema['file'].languageIndependent = False

# #4898 Set Content-Disposition: attachment for PDF files
inlineMimetypes = atfile.ATFile.inlineMimetypes
if 'application/pdf' in inlineMimetypes:
    inlineMimetypes = set(inlineMimetypes)
    inlineMimetypes.remove('application/pdf')
    atfile.ATFile.inlineMimetypes = tuple(inlineMimetypes)

from Products.ATContentTypes.content import image
image.ATImageSchema['rights'].languageIndependent = True
