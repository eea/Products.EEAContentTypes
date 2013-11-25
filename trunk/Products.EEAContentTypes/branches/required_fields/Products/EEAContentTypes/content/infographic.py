""" Definition of the Infographic content type
"""
from Products.Archetypes.ArchetypeTool import registerType

from zope.interface import implements
from Products.Archetypes import atapi
from Products.EEAContentTypes.config import EEAMessageFactory as _, PROJECTNAME
from plone.app.blob import content
from Products.EEAContentTypes.content.interfaces import IInfographic


SCHEMA = atapi.Schema((
    atapi.StringField(
        name='imageCopyright',
        schemata="default",
        widget=atapi.StringWidget(
            label=_("Image Copyright"),
            description=_("Enter the copyright information for this image."),
            i18n_domain='eea',
        )
    ),

    atapi.TextField(
        name='license',
        schemata="creators",
        allowable_content_types=('text/plain',),
        widget=atapi.TextAreaWidget(
            label=_(u'License'),
            description=_(u'License information')
        )
    ),
    atapi.TextField(
        name='publisher',
        schemata="creators",
        allowable_content_types=('text/plain',),
        widget=atapi.TextAreaWidget(
            label=_(u'Publisher'),
            description=_(u'Publisher information')
        )
    ),
    atapi.BooleanField(
        schemata='settings',
        name='presentation',
        required=False,
        languageIndependent=True,
        widget=atapi.BooleanWidget(
            label=_(u'Presentation mode'),
            description=_(u"If selected, this will give users the ability to "
                          u"view the contents as presentation slides.")
        )
    )
))


class Infographic(content.ATBlob):
    """ Infographic """

    implements(IInfographic)

    meta_type = "Infographic"
    portal_type = "Infographic"
    archetypes_name = "Infographic"

    schema = (
        content.ATBlobSchema.copy() +
        SCHEMA.copy()
    )

registerType(Infographic, PROJECTNAME)
