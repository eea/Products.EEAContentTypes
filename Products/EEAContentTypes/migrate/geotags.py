""" Migration script from location widget to geotags
"""
from Products.Five.browser import BrowserView
from Products.EEAContentTypes.content.interfaces import IGeoPosition
from eea.geotags.interfaces import IGeoTags
import logging

logger = logging.getLogger('EEAContentTypes.geotypes.migrate')

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
            try:
                loc = IGeoPosition(obj)
            except Exception:
                logger.info("Event not migrated %s" % obj.absolute_url())
                continue
            geo = IGeoTags(obj)
            name  = loc.context.location
            name_list = name.split(',')
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
                    'name': name,
                    'title': name,
                    'center': [loc.latitude, loc.longitude],
                    'country': loc.country_code,
                    'other':{
                        'countryCode': loc.country_code,
                        'countryName': name_list[-1],
                        'adminName1': name_list[0],
                        'lat': loc.latitude,
                        'lng': loc.longitude,
                        'name': name_list[0],
                    },
                    'tags' : "",

                }
            }
            template['features'].append(feature)
            geo.tags = template
            obj.reindexObject()
        return "done"
