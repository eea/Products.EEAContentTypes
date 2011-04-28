from Products.Archetypes.atapi import AnnotationStorage
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from eea.dataservice.fields.ManagementPlanField import ManagementPlanField
from eea.dataservice.vocabulary import DatasetYears
from eea.dataservice.widgets.ManagementPlanWidget import ManagementPlanWidget
from zope.interface import implements
from plone.app.blob.subtypes.file import SchemaExtender as BaseSchemaExtender
from datetime import datetime


class ExtensionManagementPlanfield(ExtensionField, ManagementPlanField):
    """ derivative of blobfield for extending schemas """


class SchemaExtender(object):
    implements(ISchemaExtender)

    fields = BaseSchemaExtender.fields + [
        ExtensionManagementPlanfield(
            name='eeaManagementPlan',
            languageIndependent=True,
            required=True,
            default=(datetime.now().year, ''),
            validators = ('management_plan_code_validator',),
            vocabulary=DatasetYears(),
            storage = AnnotationStorage(migrate=True),
            widget = ManagementPlanWidget(
                format="select",
                label="EEA Management Plan",
                description = ("EEA Management plan code."),
                label_msgid='dataservice_label_eea_mp',
                description_msgid='dataservice_help_eea_mp',
                i18n_domain='eea.dataservice',
                )
            )
    ]
