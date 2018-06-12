""" Utility to check Rancher environment status
"""
import logging
from zope.interface import implements
from eventlet.green import urllib2
from contextlib import closing
from ftw.globalstatusmessage.interfaces import IStatusMessageAutomaticEnable
from eea.cache import cache


TIMEOUT = 15
RANCHER_METADATA = 'http://rancher-metadata/latest'
MEMCACHE_AGE = 1800
logger = logging.getLogger("Products.EEAContentTypes")


class RancherStatus(object):
    """ Global status message utility for automatic enable
    """
    implements(IStatusMessageAutomaticEnable)

    def get_rancher_metadata(self, url):
        """ Returns Rancher metadata API
        """
        result = ''
        try:
            with closing(urllib2.urlopen(url, timeout=TIMEOUT)) as conn:
                result = conn.read()
        except Exception, err:
            logger.exception(err)
        return result

    def get_stacks(self):
        """ Returns all Rancher stacks from the current environment
        """
        url = "%s/stacks" % RANCHER_METADATA
        stacks = self.get_rancher_metadata(url)
        stacks = stacks.split('\n')
        return stacks

    def get_services(self, stack):
        """ Returns all services from a specific stack 
        """
        url = "%s/stacks/%s/services" % (RANCHER_METADATA, stack)
        services = self.get_rancher_metadata(url)
        services = services.split('\n')
        return services

    def get_service_state(self, stack, service):
        """ Returns the current state of a specific stack
        """
        url = "%s/stacks/%s/services/%s/state" % \
                        (RANCHER_METADATA, stack, service)
        state = self.get_rancher_metadata(url)
        return state

    @cache(lambda *args: MEMCACHE_AGE)
    def __call__(self):
        status = None
        stacks = self.get_stacks()

        for stack in stacks:
            services = ''
            stack_name = stack.split('=')
            if len(stack_name) > 1:
                stack_name = stack_name[1]
                services = self.get_services(stack_name)

                for service in services:
                    state = ''
                    service_name = service.split('=')
                    if len(service_name) > 1:
                        service_name = service_name[1]
                        state = self.get_service_state(stack_name,
                                                       service_name)
                    if state in ['upgrading', 'upgraded']:
                        status = 'upgrading'
                        return status

        return None
