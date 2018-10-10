""" Utility to check Rancher environment status
"""
import json
import logging
from zope.interface import implements
from eventlet.green import urllib2
from contextlib import closing
from ftw.globalstatusmessage.interfaces import IStatusMessageAutomaticEnable
from eea.cache import cache


TIMEOUT = 15
RANCHER_METADATA = 'http://rancher-metadata/latest'
MEMCACHE_AGE = 300
logger = logging.getLogger("Products.EEAContentTypes")


class RancherStatus(object):
    """ Global status message utility for automatic enable
    """
    implements(IStatusMessageAutomaticEnable)

    def get_rancher_metadata(self, url):
        """ Returns Rancher metadata API
        """
        try:
            with closing(urllib2.urlopen(url, timeout=TIMEOUT)) as conn:
                result = json.loads(conn.read())
        except Exception as err:
            logger.warn(err)
            result = []
        return result

    def get_stacks(self):
        """ Returns all Rancher stacks from the current environment
        """
        url = "%s/stacks" % RANCHER_METADATA
        request = urllib2.Request(url, headers={"Accept" : "application/json"})
        return self.get_rancher_metadata(request)

    @cache(lambda *args: 'rancher-status', lifetime=MEMCACHE_AGE)
    def __call__(self):
        for stack in self.get_stacks():
            if stack.get('system'):
                continue
            services = stack.get("services", [])
            if services:
                for service in services:
                    if service.get("state") in ["upgrading"]:
                        logger.info("GSM auto-enabled: %s - %s",
                                    service.get('name'), service.get("state"))
                        return "upgrading"
        logger.info("GSM auto-disabled: no upgrading services")
        return ""
