""" Browser views
"""
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView as FiveBrowserView
import json


class ViewCountryRegionsJSON(FiveBrowserView):
    """ Json View of each CountryRegionSection
    """
    def __init__(self, context, request):
        self.request = request
        self.context = context

    def __call__(self, *args, **kwargs):
        cat = getToolByName(self.context, 'portal_catalog')
        brains = cat(portal_type="CountryRegionSection")
        data = {"items": []}
        for brain in brains:
            obj = brain.getObject()
            url = obj.absolute_url()
            data['items'].append({
                obj.title: {
                    'url': obj.getRemoteUrl(),
                    'bg_url': url + '/image_panoramic',
                    'flag_url': url + '/flag_mini',
                    'body': obj.getBody(),
                    'external_links': list(obj.getExternalLinks())
                }
            })
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(data)
