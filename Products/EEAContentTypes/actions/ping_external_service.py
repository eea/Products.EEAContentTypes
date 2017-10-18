import logging

from eventlet.green import urllib2

from OFS.SimpleItem import SimpleItem

from zope import schema
from zope.component import adapts
from zope.formlib import form
from zope.interface import implements, Interface
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from plone.app.contentrules.browser.formhelper import AddForm, EditForm

logger = logging.getLogger("Products.EEAContentTypes")

class IPingExternalServiceAction(Interface):
    """ Ping action settings schema
    """
    service_to_ping = schema.TextLine(
        title=u"Service to ping",
        description=u"Service to ping.",
        required=True
    )


class PingExternalServiceAction(SimpleItem):
    """ Ping action settings
    """
    implements(IPingExternalServiceAction, IRuleElementData)

    service_to_ping = ''

    element = 'Products.EEAContentTypes.actions.ping_external_service'

    summary = u'ping external service'

class PingExternalServiceActionExecutor(object):
    """ Ping action executor
    """
    implements(IExecutable)
    adapts(Interface, IPingExternalServiceAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        try:
            url = self.element.service_to_ping
            logger.info("Pinging external service %s", url)
            ping_con = urllib2.urlopen(url, timeout=10)
            ping_response = ping_con.read()
            ping_con.close()
            logger.info(
                "Response from external service %s: %s",
                url,
                ping_response)
        except urllib2.HTTPError, err:
            logger.error(
                "Pinging external service %s failed with message: %s",
                url,
                err.msg)
        except Exception, err:
            logger.error(
                "Pinging external service %s failed with message: %s",
                url,
                err)



class PingExternalServiceAddForm(AddForm):
    """ Ping action addform
    """
    form_fields = form.FormFields(IPingExternalServiceAction)
    label = u"Add Ping External Service Action"
    description = u"A ping External Service action."
    form_name = u"Configure element"

    def create(self, data):
        """ Ping action create method
        """
        a = PingExternalServiceAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class PingExternalServiceEditForm(EditForm):
    """ Ping action editform
    """
    form_fields = form.FormFields(IPingExternalServiceAction)
    label = u"Edit Ping External Service Action"
    description = u"A ping External Service action."
    form_name = u"Configure element"
