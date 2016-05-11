""" RabbitMQ message action - send a message to the service:
    - it uses the default exchange
    - routing based on the queue name
    - the queue is 'durable' (the messages aren't lost)
"""

import logging
from zope import schema

from zope.interface import implements, Interface

from App.config import getConfiguration
from OFS.SimpleItem import SimpleItem
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from eea.rabbitmq.client import RabbitMQConnector
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from plone.stringinterp.interfaces import IStringInterpolator
from zope.component import adapts
from zope.formlib import form

#load rabbitmq configuration from conf and import connector
config = getConfiguration()
if not hasattr(config, 'product_config'):
    # this happens during unit tests, we load a dummy rabbit config dict
    rabbit_config = {
        'rabbit_host': '',
        'rabbit_port': '',
        'rabbit_username': '',
        'rabbit_password': ''
    }
else:
    configuration = config.product_config.get('rabbitmq', dict())
    try:
        port = int(configuration.get('port', ''))
    except Exception:
        port = 80
    rabbit_config = {
        'rabbit_host': configuration.get('host', ''),
        'rabbit_port': port,
        'rabbit_username': configuration.get('username', ''),
        'rabbit_password': configuration.get('password', '')
    }


logger = logging.getLogger("Products.EEAContentTypes")


class IRabbitMQMessageAction(Interface):
    """ Action settings schema
    """

    queue_name = schema.TextLine(title=_(u"Queue name"),
        description=_(u"Queue where the message will be send"),
        required=True)

    body = schema.Text(title=_(u"Message"),
        description=_(u"The message that you want to send to RabbitMQ."),
        required=True)


class RabbitMQMessageAction(SimpleItem):
    """ Action settings
    """
    implements(IRabbitMQMessageAction, IRuleElementData)

    queue_name = ''
    body = u''

    element = 'Products.EEAContentTypes.actions.rabbitmq_message'

    @property
    def summary(self):
        """ Action summary
        """
        return _(u"Send the '${body}' message to RabbitMQ service using the "
                 "'${queue_name}' queue.",
                 mapping=dict(queue_name=self.queue_name, body=self.body))


class RabbitMQMessageActionExecutor(object):
    """ The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IRabbitMQMessageAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        event = self.event
        queue_name = self.element.queue_name

        obj = event.object

        interpolator = IStringInterpolator(obj)

        body = interpolator(self.element.body.strip())

        if body:
            #send message to the RabbitMQ service
            rabbit = RabbitMQConnector(**rabbit_config)
            rabbit.open_connection()
            try:
                rabbit.declare_queue(queue_name)
                rabbit.send_message(queue_name, body)
            except Exception, err:
                logger.error(
                    'Sending \'%s\' in \'%s\' FAILED with error: %s',
                    body,
                    queue_name,
                    err)
            else:
                logger.info(
                    'Sending \'%s\' in \'%s\' OK',
                    body,
                    queue_name)
            rabbit.close_connection()


class RabbitMQMessageAddForm(AddForm):
    """ An add form for the action
    """
    form_fields = form.FormFields(IRabbitMQMessageAction)
    label = _(u"Add RabbitMQ message Action")
    description = _(u"A RabbitMQ message.")
    form_name = _(u"Configure element")

    # custom template will allow us to add help text
    template = ViewPageTemplateFile('templates/rabbitmq_message.pt')

    def create(self, data):
        """ Action create method
        """
        a = RabbitMQMessageAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class RabbitMQMessageEditForm(EditForm):
    """ An edit form for the action
    """
    form_fields = form.FormFields(IRabbitMQMessageAction)
    label = _(u"Edit RabbitMQ message Action")
    description = _(u"A RabbitMQ message.")
    form_name = _(u"Configure element")

    # custom template will allow us to add help text
    template = ViewPageTemplateFile('templates/rabbitmq_message.pt')
