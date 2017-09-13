""" Browser views
"""
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView as FiveBrowserView
import json


def get_language_codes():
    """ get languages for each country we support
    """
    return {
        'Austria': ['de'],
        'Belgium': ['nl', 'fr', 'de'],
        'Bulgaria': ['bg'],
        'Croatia': ['hr'],
        'Cyprus': ['el', 'tr'],
        'Czech Republic': ['cs'],
        'Denmark': ['da'],
        'Estonia': ['et'],
        'Finland': ['fi'],
        'France': ['fr'],
        'Germany': ['de'],
        'Greece': ['el'],
        'Hungary': ['hu'],
        'Iceland': ['is'],
        'Ireland': ['ie'],
        'Italy': ['it'],
        'Latvia': ['lv'],
        'Liechtenstein': ['de'],
        'Lithuania': ['lt'],
        'Luxembourg': ['de', 'fr'],
        'Malta': ['mt'],
        'Norway': ['no'],
        'Poland': ['pl'],
        'Portugal': ['pt'],
        'Romania': ['ro'],
        'Serbia': ['en'],  # we do not have rs language
        'Slovakia': ['sk'],
        'Slovenia': ['sl'],
        'Spain': ['es'],
        'Sweden': ['sv'],
        'Switzerland': ['de', 'fr', 'it'],
        'Netherlands': ['nl'],
        'Turkey': ['tr'],
        'United Kingdom': ['en'],
        'Bosnia and Herzegovina': ['hr'],
        'Kosovo': ['hr', 'tr'],
        'Macedonia': ['hr', 'tr'],
        'Montenegro': ['hr']
    }


class ViewCountryRegionsJSON(FiveBrowserView):
    """ Json View of each CountryRegionSection
    """
    def __init__(self, context, request):
        self.request = request
        self.context = context

    def __call__(self, *args, **kwargs):
        cat = getToolByName(self.context, 'portal_catalog')
        brains = cat(portal_type="CountryRegionSection")
        data = {}
        lang_codes = get_language_codes()

        for brain in brains:
            obj = brain.getObject()
            url = obj.absolute_url()
            title = obj.title
            ctype = obj.getType()
            if type(ctype) is not str:
                ctype = u"country"
            data[obj.id] = {
                    'url': obj.getRemoteUrl(),
                    'bg_url': url + '/image_panoramic',
                    'flag_url': url + '/flag_mini',
                    'body': obj.getBody(),
                    'title': title,
                    'type': ctype,
                    'external_links': list(obj.getExternalLinks()),
                    'languages': lang_codes.get(title, ['en'])
                }
            
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(data)
