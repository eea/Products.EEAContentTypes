""" Action menu Browser views
"""
from Products.EEAContentTypes.content.interfaces import ICountryProfile
from Products.Five import BrowserView as FiveBrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import alsoProvides


class AddCountryProfileInterface(FiveBrowserView):
    """ View
    """
    def __init__(self, context, request):
        self.request = request
        self.context = context

    def __call__(self, *args, **kwargs):
        alsoProvides(self.context, ICountryProfile)
        msg = "Succesfully added ICountryProfile marker Interface"
        url = self.context.absolute_url() + '/view'
        IStatusMessage(self.request).addStatusMessage(
            msg, "info")
        return self.request.response.redirect(url)
