""" Schema extender
"""
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaModifier
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from eea.design.browser.interfaces import IEEACommonLayer


class RelatedItemsModifier(object):
    """ Adds the keepReferencesOnCopy feature to all content types
        so related items are not lost when objects are copied.
    """
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IEEACommonLayer

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        """ Modify schema
        """
        schema['relatedItems'].keepReferencesOnCopy = True
        return schema
