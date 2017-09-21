""" Browser views
"""
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView as FiveBrowserView
import json


def get_language_codes():
    """ get languages for each country we support
    """
    return {
        "Austria": [["German", "de"]],
        "Belgium": [["Dutch", "nl"], ["French", "fr"], ["German", "de"]],
        "Bulgaria": [["Bulgarian", "bg"]],
        "Croatia": [["Croatian", "hr"]],
        "Cyprus": [["Greek", "el"], ["Turkish", "tr"]],
        "Czech Republic": [["Czech", "cs"]],
        "Denmark": [["Danish", "da"]],
        "Estonia": [["Estonian", "et"]],
        "Finland": [["Finnish", "fi"]],
        "France": [["French", "fr"]],
        "Germany": [["German", "de"]],
        "Greece": [["Greek", "el"]],
        "Hungary": [["Hungarian", "hu"]],
        "Iceland": [["Icelandic", "is"]],
        "Ireland": [["English", "en"]],
        "Italy": [["Italian", "it"]],
        "Latvia": [["Latvian", "lv"]],
        "Liechtenstein": [["German", "de"]],
        "Lithuania": [["Lithuanian", "lt"]],
        "Luxembourg": [["German", "de"], ["French", "fr"]],
        "Malta": [["Maltese", "mt"]],
        "Norway": [["Norwegian", "no"]],
        "Poland": [["Polish", "pl"]],
        "Portugal": [["Portuguese", "pt"]],
        "Romania": [["Romanian", "ro"]],
        "Serbia": [["English", "en"]],  # we do not have rs language
        "Slovakia": [["Slovak", "sk"]],
        "Slovenia": [["Slovenian", "sl"]],
        "Spain": [["Spanish", "es"]],
        "Sweden": [["Swedish", "sv"]],
        "Switzerland": [["German", "de"], ["French", "fr"], ["Italian", "it"]],
        "Netherlands": [["Dutch", "nl"]],
        "The Netherlands": [["Dutch", "nl"]],
        "Turkey": [["Turkish", "tr"]],
        "United Kingdom": [["English", "en"]],
        "Bosnia and Herzegovina": [["Croatian", "hr"]],
        "Kosovo": [["Croatian", "hr"], ["Turkish", "tr"]],
        "Kosovo*": [["Croatian", "hr"], ["Turkish", "tr"]],
        "Macedonia": [["Croatian", "hr"], ["Turkish", "tr"]],
        "The Former Yugoslav Republic of Macedonia": [["Croatian", "hr"], ["Turkish", "tr"]],
        "Montenegro": [["Croatian", "hr"]]
    }


class ViewCountryRegionsJSON(FiveBrowserView):
    """ Json View of each CountryRegionSection
    """
    def __init__(self, context, request):
        self.request = request
        self.context = context

    def __call__(self, *args, **kwargs):
        cat = getToolByName(self.context, "portal_catalog")
        brains = cat(portal_type="CountryRegionSection")
        data = {}
        lang_codes = get_language_codes()

        for brain in brains:
            obj = brain.getObject()
            url = obj.absolute_url()
            title = obj.title
            ctype = obj.getType()
            if type(ctype) is not str:
                ctype = "country"
            data[obj.id] = {
                    "url": obj.getRemoteUrl(),
                    "obj_id": obj.id,
                    "bg_url": url + "/image_panoramic",
                    "body": obj.getBody(),
                    "description": obj.getDescription(),
                    "title": title,
                    "type": ctype,
                    "external_links": list(obj.getExternalLinks()),
                    "languages": lang_codes.get(title, ["English"])}
            
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(data)
