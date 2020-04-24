""" Custom zope schema
"""

from zope.interface import implements
from OFS.Folder import Folder
from Products.EEAContentTypes.controlpanels.interfaces import IScreenshotPortalType

class PortalType(Folder):
    """ Storage for custom portal types
    """
    implements(IScreenshotPortalType)
    meta_type = 'Screenshots Portal Type'
    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w'},
        {'id': 'emulate', 'type': 'string', 'mode': 'w'},
        {'id': 'waitforselector', 'type': 'string', 'mode': 'w'},
        {'id': 'el', 'type': 'string', 'mode': 'w'},
        {'id': 'click', 'type': 'string', 'mode': 'w'},
        {'id': 'no', 'type': 'string', 'mode': 'w'},
        {'id': 'portal_type', 'type': 'string', 'mode': 'w'},
        {'id': 'service_url', 'type': 'string', 'mode': 'w'},

        {'id': 'pdf', 'type': 'boolean', 'mode': 'w'},
        {'id': 'fullPage', 'type': 'boolean', 'mode': 'w'},

        {'id': 'w', 'type': 'int', 'mode': 'w'},
        {'id': 'h', 'type': 'int', 'mode': 'w'},
        {'id': 'waitfor', 'type': 'int', 'mode': 'w'}
    )

    title = ''
    emulate = ''
    portal_type = ''
    waitforselector = ''
    el = ''
    click = ''
    no = ''
    service_url = ''
    pdf = False
    fullPage = True
    w = 1920
    h = 1080
    waitfor = 0
