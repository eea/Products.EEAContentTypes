""" Link """
from urllib import quote
from Products.ATContentTypes.content.link import ATLink
from Products.CMFCore.utils import getToolByName


def override_getRemoteUrl(self):
    """ Get remote URL """
    # In the GIS Application edit form, the remoteUrl should be the one to
    # edit.
    mtool = getToolByName(self, 'portal_membership')
    if (mtool.isAnonymousUser() and (self.portal_type == 'GIS Application')):
        return self.absolute_url()
    else:
        value = self.Schema()['remoteUrl'].get(self)
    if not value:
        value = '' # ensure we have a string

    return quote(value, safe='?$#@/:=+;$,&')

ATLink.getRemoteUrl = override_getRemoteUrl
