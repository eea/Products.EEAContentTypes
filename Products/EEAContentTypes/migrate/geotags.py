
""" Migration script from location widget to geotags
"""
from Products.Five.browser import BrowserView
from eea.geotags.interfaces import IGeoTags
import logging
from Products.Archetypes import atapi
import time
import json
import urllib
import transaction
logger = logging.getLogger('EEAContentTypes.geotypes.migrate')
from Products.EEAContentTypes.content.interfaces import IGeoPositioned
from zope.interface import noLongerProvides
from zope.annotation.interfaces import IAnnotations

class LocationMigrate(BrowserView):
    """ Run location migration for events
    """
    def __call__(self):
        context = self.context
        catalog = context.portal_catalog
        folder_path = '/'.join(context.getPhysicalPath())
        depth = 6 if self.context.portal_type == "Folder" else 0
        brains = catalog.searchResults(portal_type = ('QuickEvent', 'Event'),
             path = {'query': folder_path, 'depth': depth}, Language = "all",
                                                        show_inactive = True)
        errors = ["Errors:"]
        not_found = ["Not Found:"]
        no_location = ["No location"]

        count = 0

        for brain in brains:
            try:
                obj = brain.getObject()
                url = obj.absolute_url()
                location = obj.location
                if type(location) == tuple:
                    location = location[0]
                location = location.encode('utf-8')
                if not location or \
                            location == u'<street address>, <city>, <country>':
                    obj.location = ''
                    logger.info("NO Location %s" % url)
                    no_location.append("NO Location %s" % url)
                    continue

                template = {
                    'type': 'FeatureCollection',
                    'features': []
                }
                # check if geoposition information is already set on the object
                anno = IAnnotations(self.context)
                anno_loc = anno.get(['coordonates'])
                anno_country = anno.get(['country_code'])
                if anno_loc and anno_country:
                    latitude = anno_loc.get('latitude')
                    longitude = anno_loc.get('longitude')
                    country_code = anno_country.get('country_code')
                    name = location
                    name_list = name.split(',')
                    feature = {
                        'type': 'Feature',
                        'bbox': [],
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [latitude, longitude],
                            },
                        'properties': {
                            'name': '',
                            'title': name,
                            'description': name,
                            'center': [latitude, longitude],
                            'country': country_code,
                            'other':{
                                'countryCode': country_code,
                                'countryName': name_list[-1],
                                'adminName1': name_list[0],
                                'lat': latitude,
                                'lng': longitude,
                                'name': name_list[0],
                            },
                            'tags' : ""
                        }
                    }
                    # remove these entries from annotation as they
                    # are no longer needed, and remove IGeoPositioned  
                    del(anno[['coordonates']])
                    del(anno[['country_code']])
                    noLongerProvides(obj, IGeoPositioned)
                else:
                    # search with google geoposition information for
                    # current location
                    time.sleep(1.0)
                    params = {
                              'address': location,
                              'sensor' : 'false'}
                    u = urllib.urlopen(
                      "http://maps.googleapis.com/maps/api/geocode/json?%s" % \
                                                      urllib.urlencode(params))
                    gbuffer = u.read()
                    js = json.loads(gbuffer)
                    res = js.get('results')
                    if res:
                        res = res[0]
                    else:
                        item = "url: %s  location: %s" % (url, obj.location)
                        not_found.append(item)
                        continue

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
                            'description': location,
                            'center': [loc['lat'], loc['lng']],
                            'other': res,
                            'tags' : res['types']
                        }
                    }

                geo = IGeoTags(obj)

                template['features'].append(feature)

                field = obj.getField('location')
                atapi.LinesField.set(field, obj, obj.location)
                geo.tags = template
                obj.reindexObject()

                count += 1
                if count % 10 == 0:
                    logger.info("Committing geotags migration transaction")
                    transaction.commit()
            except Exception, exp:
                message = exp.message
                if not message:
                    message = exp.args
                error_msg = "%s with error: \n %s" % \
                        (url, message)
                logger.info(error_msg)
                errors.append(error_msg)
                continue

        if len(not_found) > 1 or len(no_location) > 1:
            return (not_found, no_location, errors)
        else:
            return errors if len(errors) > 1 else "done"

