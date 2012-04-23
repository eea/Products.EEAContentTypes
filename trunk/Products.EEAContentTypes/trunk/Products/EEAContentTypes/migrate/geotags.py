""" Migration script from location widget to geotags
"""
from Products.Five.browser import BrowserView
from Products.EEAContentTypes.content.interfaces import IGeoPosition
from eea.geotags.interfaces import IGeoTags

class LocationMigrate(BrowserView):
    """ Run location migration for events
    """
    def __call__(self):
        context = self.context
        catalog = context.portal_catalog
        folder_path = '/'.join(context.getPhysicalPath())
        brains = catalog.searchResults(portal_type=('QuickEvent', 'Event'),
                        path={'query': folder_path, 'depth': 1})
        for brain in brains:
            obj = brain.getObject()
            loc = IGeoPosition(obj)
            geo = IGeoTags(obj)
            template = {
                'type': 'FeatureCollection',
                'features': []
            }
            feature = {
                'type': 'Feature',
                'bbox': [],
                'geometry': {
                    'type': 'Point',
                    'coordinates': [loc.latitude, loc.longitude],
                    },
                'properties': {
                    'name': loc.context.location,
                    'title': loc.context.location,
                    'center': [loc.latitude, loc.longitude],
                    'country': loc.country_code,
                }
            }
            template['features'].append(feature)
            geo.tags = template
            obj.reindexObject()
        return "done"
