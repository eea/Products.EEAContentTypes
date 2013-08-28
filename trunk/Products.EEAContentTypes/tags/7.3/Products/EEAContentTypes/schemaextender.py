""" Schema extender
"""
from archetypes.schemaextender.interfaces import ISchemaModifier
from zope.interface import implements

class RelatedItemsModifier(object):
    """ Adds the keepReferencesOnCopy feature to all content types
        so related items are not lost when objects are copied.
    """
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        """ Modify schema
        """
        schema['relatedItems'].keepReferencesOnCopy = True
        return schema
