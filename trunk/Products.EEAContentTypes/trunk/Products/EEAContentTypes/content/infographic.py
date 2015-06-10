""" Definition of the Infographic content type
"""
from AccessControl import ClassSecurityInfo

from Products.Archetypes.ArchetypeTool import registerType
from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import image
from plone.app.blob import field

from Products.EEAContentTypes.config import EEAMessageFactory as _, PROJECTNAME
from Products.EEAContentTypes.content.interfaces import IInfographic

SCHEMA = atapi.Schema((

    field.ImageField(
        name="image",
        schemata="default",
        sizes=None,
        required=True,
        primary=True,
        widget=field.ImageWidget(
            label=_("Infographic"),
            description=_("Infographic image"),
            i18n_domain='eea',
        )
    ),

))


class Infographic(image.ATImage):
    """ Infographic """

    implements(IInfographic)

    meta_type = "Infographic"
    portal_type = "Infographic"
    archetypes_name = "Infographic"

    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    schema = (
        image.ATImageSchema.copy() +
        SCHEMA.copy()
    )
    schema["title"].required = True
    schema["relatedItems"].required_for_published = True


registerType(Infographic, PROJECTNAME)
