""" Migration script from location widget to geotags
"""
from Products.Five.browser import BrowserView
from eea.geotags.interfaces import IGeoTags
import logging
import urllib
import json
from Products.Archetypes import atapi
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

        errors = []
        for brain in brains:
            try:
                obj = brain.getObject()
                geo = IGeoTags(obj)
                location = obj.location
                if type(location) == tuple:
                    location = location[0]
                location = location.encode('utf-8')
                params = {
                          'address': location,
                          'sensor' : 'false'}
                u = urllib.urlopen(
                    "http://maps.googleapis.com/maps/api/geocode/json?%s" % \
                                                    urllib.urlencode(params))
                gbuffer = u.read()
                js = json.loads(gbuffer)
                res = js.get('results')[0]

                template = {
                    'type': 'FeatureCollection',
                    'features': []
                }
                loc = res['geometry']['location']
                viewport = res['geometry']['viewport']
                ne = viewport['northeast']
                sw = viewport['southwest']
                feature = {
                    'type': 'Feature',
                    'bbox': [sw['lat'], sw['lng'], ne['lat'], ne['lng']],
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [loc['lat'], loc['lng']],
                        },
                    'properties': {
                        'name': location,
                        'title': res['address_components'][0]['long_name'],
                        'description': res['formatted_address'],
                        'center': [loc['lat'], loc['lng']],
                        'other': res,
                        'tags' : res['types']
                    }
                }

                template['features'].append(feature)

                field = obj.getField('location')
                atapi.LinesField.set(field, obj, obj.location)
                geo.tags = template
                obj.reindexObject()
            except Exception, exp:
                error_msg = "%s with error: \n %s" % \
                        (obj.absolute_url(), exp.message)
                logger.info(error_msg)
                errors.append(error_msg)
                continue

        return errors if len(errors) else "done"

