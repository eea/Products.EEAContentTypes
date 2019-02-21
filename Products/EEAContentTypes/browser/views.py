""" Browser views
"""
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView as FiveBrowserView
import json


def get_language_codes():
    """ get languages for each country we support
    """
    return {
        "Albania": [["Albanian", "sq"]],
        "Austria": [["German", "de"]],
        "Belgium": [["Dutch", "nl"], ["French", "fr"], ["German", "de"]],
        "Bulgaria": [["Bulgarian", "bg"]],
        "Croatia": [["Croatian", "hr"]],
        "Cyprus": [["Greek", "el"], ["Turkish", "tr"]],
        "Czech Republic": [["Czech", "cs"]],
        "Denmark": [["Danish", "da"]],
        "Estonia": [["Estonian", "et"]],
        "Finland": [["Finnish", "fi"],["Swedish", "sv"]],
        "France": [["French", "fr"]],
        "Germany": [["German", "de"]],
        "Greece": [["Greek", "el"]],
        "Hungary": [["Hungarian", "hu"]],
        "Iceland": [["Icelandic", "is"]],
        "Ireland": [["English", ""], ["Irish", "ga"]],
        "Italy": [["Italian", "it"]],
        "Latvia": [["Latvian", "lv"]],
        "Liechtenstein": [["German", "de"]],
        "Lithuania": [["Lithuanian", "lt"]],
        "Luxembourg": [["German", "de"], ["French", "fr"]],
        "Malta": [["Maltese", "mt"],["English", ""]],
        "Norway": [["Norwegian", "no"]],
        "Poland": [["Polish", "pl"]],
        "Portugal": [["Portuguese", "pt"]],
        "Romania": [["Romanian", "ro"]],
        "Serbia": [["Serbian", "sr"]], 
        "Slovakia": [["Slovak", "sk"]],
        "Slovenia": [["Slovenian", "sl"]],
        "Spain": [["Spanish", "es"]],
        "Sweden": [["Swedish", "sv"]],
        "Switzerland": [["German", "de"], ["French", "fr"], ["Italian", "it"]],
        "Netherlands": [["Dutch", "nl"]],
        "The Netherlands": [["Dutch", "nl"]],
        "Turkey": [["Turkish", "tr"]],
        "United Kingdom": [["English", ""]],
        "Bosnia and Herzegovina": [["Bosnian", "bs"], ["Croatian", "hr"], ["Serbian", "sr"]],
        "Kosovo": [["Albanian", "sq"], ["Serbian", "sr"]],
        "Kosovo*": [["Albanian", "sq"], ["Serbian", "sr"]],
        "Macedonia": [["Macedonian", "mk"]],
        "North Macedonia": [["Macedonian", "mk"]],
        "Montenegro": [["Croatian", "hr"], ["Serbian", "sr"]]
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
                    "description": obj.description,
                    "title": title,
                    "type": ctype,
                    "external_links": list(obj.getExternalLinks()),
                    "languages": lang_codes.get(title, ["English", ""])}
            
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(data)
