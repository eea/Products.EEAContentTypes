from p4a.subtyper.engine import DescriptorWithName
from p4a.subtyper.interfaces import ISubtyper, IPossibleDescriptors
from p4a.subtyper.interfaces import IPortalTypedPossibleDescriptors
from zope.app.publisher.browser.menu import BrowserMenu
from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.component import getUtility, queryAdapter
from zope.interface import implements
import logging


logger = logging.getLogger('eea-p4a.subtyper.menu')


class SubtypesMenu(BrowserMenu):
    """We rewrite this menu because the implementation in p4a.subtyper is broken 
    due to adapter resolution
    """

    implements(IBrowserMenu)

    def _possible_types(self, obj):
        possible = queryAdapter(obj, IPortalTypedPossibleDescriptors)
        if possible and possible.possible:
            return (DescriptorWithName(n, c) for n, c in possible.possible)

        possible = IPossibleDescriptors(obj)
        return (DescriptorWithName(n, c) for n, c in possible.possible)
        

    def _get_menus(self, object, request):
        subtyper = getUtility(ISubtyper)
        existing = subtyper.existing_type(object)

        result = []
        for subtype in self._possible_types(object):
            descriptor = subtype.descriptor

            selected = existing is not None and subtype.name == existing.name

            d = {'title': descriptor.title,
                 'description': descriptor.description or u'',
                 'action': '%s/@@subtyper/change_type?subtype=%s' % \
                     (object.absolute_url(), subtype.name),
                 'selected': selected,
                 'icon': getattr(descriptor, 'icon', u''),
                 'extra': {'id': descriptor.type_interface.__name__,
                           'separator': None,
                           'class': selected and 'actionMenuSelected' or ''},
                 'submenu': None,
                 'subtype': subtype}
            result.append(d)

        return result

    def getMenuItems(self, object, request):
        try:
            return self._get_menus(object, request)
        except Exception, e:
            # it can be very difficult to troubleshoot errors here
            # because sometimes it bubbles up as AttributeError's which
            # the zope2 publisher handles in a very bizarre manner

            logger.exception(e)
            raise

