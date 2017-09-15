""" Browser views
"""
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView as FiveBrowserView
import json


def get_language_codes():
    """ get languages for each country we support
    """
    return {
        'Austria': ['German'],
        'Belgium': ['Dutch', 'French', 'German'],
        'Bulgaria': ['Bulgarian'],
        'Croatia': ['Croatian'],
        'Cyprus': ['Greek', 'Turkish'],
        'Czech Republic': ['Czech'],
        'Denmark': ['Danish'],
        'Estonia': ['Estonian'],
        'Finland': ['Finnish'],
        'France': ['French'],
        'Germany': ['German'],
        'Greece': ['Greek'],
        'Hungary': ['Hungarian'],
        'Iceland': ['Icelandic'],
        'Ireland': ['English'],
        'Italy': ['Italian'],
        'Latvia': ['Latvian'],
        'Liechtenstein': ['German'],
        'Lithuania': ['Lithuanian'],
        'Luxembourg': ['German', 'French'],
        'Malta': ['Maltese'],
        'Norway': ['Norwegian'],
        'Poland': ['Polish'],
        'Portugal': ['Portuguese'],
        'Romania': ['Romanian'],
        'Serbia': ['English'],  # we do not have rs language
        'Slovakia': ['Slovak'],
        'Slovenia': ['Slovenian'],
        'Spain': ['Spanish'],
        'Sweden': ['Swedish'],
        'Switzerland': ['German', 'French', 'Italian'],
        'Netherlands': ['Dutch'],
        'The Netherlands': ['Dutch'],
        'Turkey': ['Turkish'],
        'United Kingdom': ['English'],
        'Bosnia and Herzegovina': ['Croatian'],
        'Kosovo': ['Croatian', 'Turkish'],
        'Kosovo*': ['Croatian', 'Turkish'],
        'Macedonia': ['Croatian', 'Turkish'],
        'The Former Yugoslav Republic of Macedonia': ['Croatian', 'Turkish'],
        'Montenegro': ['Croatian']
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
                    'body': obj.getBody(),
                    'title': title,
                    'type': ctype,
                    'external_links': list(obj.getExternalLinks()),
                    'languages': lang_codes.get(title, ['English'])
                }
            
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(data)
