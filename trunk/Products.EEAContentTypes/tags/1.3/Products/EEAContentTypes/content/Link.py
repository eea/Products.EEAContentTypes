# monkey patch, GIS Application getRemoteUrl should return absolute_url

from urllib import quote
from Products.ATContentTypes.content.link import ATLink


def override_getRemoteUrl(self):
    """ """
    if self.portal_type == 'GIS Application':
	return self.absolute_url()
    else:
	value = self.Schema()['remoteUrl'].get(self)
	if not value: value = '' # ensure we have a string
	return quote(value, safe='?$#@/:=+;$,&')

ATLink.getRemoteUrl = override_getRemoteUrl


