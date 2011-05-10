""" Migration interfaces
"""
from zope.interface import Interface

class IContentToMigrate(Interface):
    """ Marker interface for Migration Content. See configure.zcml
    """
