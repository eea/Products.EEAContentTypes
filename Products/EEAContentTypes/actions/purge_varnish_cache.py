""" purge Varnish cache of translations
"""
import logging
from OFS.SimpleItem import SimpleItem
from plone.app.contentrules.browser.formhelper import AddForm
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from z3c.caching.purge import Purge
from zope.interface import implements, Interface
from zope.component import adapts
from zope.event import notify
from zope.formlib import form
try:
    from Products.LinguaPlone.interfaces import ITranslatable
    hasLinguaPloneInstalled = True
except ImportError:
    hasLinguaPloneInstalled = False

logger = logging.getLogger("Products.EEAContentTypes")


class IPurgeVarnishCacheAction(Interface):
    """ Purge Varnish cache action settings schema
    """


class PurgeVarnishCacheAction(SimpleItem):
    """ Purge Varnish cache action settings
    """
    implements(IPurgeVarnishCacheAction, IRuleElementData)

    element = 'Products.EEAContentTypes.actions.purge_varnish_cache'
    summary = u'Purge Varnish cache of translations'


class PurgeVarnishCacheActionExecutor(object):
    """ Purge Varnish cache action executor
    """
    implements(IExecutable)
    adapts(Interface, IPurgeVarnishCacheAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object

        if hasLinguaPloneInstalled and ITranslatable.providedBy(obj):
            translations = obj.getTranslations()
            if len(translations) > 1:
                for trans, _state in translations.values():
                    logging.info("*** PURGING VARNISH CACHE: %s",
                                 trans.absolute_url())
                    notify(Purge(trans))


class PurgeVarnishCacheAddForm(AddForm):
    """ Purge Varnish cache action addform
    """
    form_fields = form.FormFields(IPurgeVarnishCacheAction)
    label = u"Add a Purge Varnish Cache action"
    description = u"Purge Varnish cache of translations."

    def create(self, data):
        """ Purge Varnish cache action create method
        """
        a = PurgeVarnishCacheAction()
        form.applyChanges(a, self.form_fields, data)
        return a
