""" GeoPosition
"""
from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.content.interfaces import IGeoPosition
from Products.EEAContentTypes.content.interfaces import IGeoPositionDecider
from Products.EEAContentTypes.content.interfaces import IGeoPositioned
from persistent.dict import PersistentDict
from xml.dom.minidom import parse
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility, adapts
from zope.interface import alsoProvides, directlyProvides, directlyProvidedBy
from zope.interface import implements
import urllib
import logging

logger = logging.getLogger("Products.EEAContentTypes")

GEOKEYS =   ['latitude', 'longitude']
GEOCOORDS = ['coordonates']
GEOINFO =   ['country_code']

class GeoPositioned(object):
    """ Geographical location (latitude, longitude). """

    implements(IGeoPosition)
    adapts(IGeoPositioned)

    def __init__(self, context):
        """ Initialize adapter. """
        self.context = context
        annotations = IAnnotations(context)

        #Coordonates
        coordonates = annotations.get(GEOCOORDS)
        if coordonates is None:
            geodata = {}
            for geokey in GEOKEYS:
                geodata[geokey] = '0.0'
            coordonates = annotations[GEOCOORDS] = PersistentDict(geodata)

        #Country code
        country_code = annotations.get(GEOINFO)
        if country_code is None:
            geoinfo = {}
            for geokey in GEOINFO:
                geoinfo[geokey] = ''
            annotations[GEOINFO] = PersistentDict(geoinfo)

    def getLatitude(self):
        """ Get latitude. """
        anno = IAnnotations(self.context)
        coordonates = anno.get(GEOCOORDS)
        return coordonates['latitude']

    def setLatitude(self, value):
        """ Set latitude. """
        anno = IAnnotations(self.context)
        coordonates = anno.get(GEOCOORDS)
        coordonates['latitude'] = value

    latitude = property(getLatitude, setLatitude)

    def getLongitude(self):
        """ Get longitude. """
        anno = IAnnotations(self.context)
        coordonates = anno.get(GEOCOORDS)
        return coordonates['longitude']

    def setLongitude(self, value):
        """ Set longitude. """
        anno = IAnnotations(self.context)
        coordonates = anno.get(GEOCOORDS)
        coordonates['longitude'] = value

    longitude = property(getLongitude, setLongitude)

    def getCountryCode(self):
        """ Get country code. """
        anno = IAnnotations(self.context)
        geoinfo = anno.get(GEOINFO)
        return geoinfo['country_code']

    def setCountryCode(self, value):
        """ Set country code. """
        anno = IAnnotations(self.context)
        geoinfo = anno.get(GEOINFO)
        geoinfo['country_code'] = value

    country_code = property(getCountryCode, setCountryCode)

    def getCoordinates(self):
        """ Return longitude and latitude. """
        return (self.getLatitude(), self.getLongitude())


class GeoPositionDecider(object):
    """ Geocoding decider """

    implements(IGeoPositionDecider)
    ifaces = (IGeoPositioned,)

    def matchLocation(self, obj):
        """ Match location
        """
        geodata = None
        location = getattr(obj, 'location', None)
        if not location:
            return geodata

        #get service keys
        service_keys = {}
        portal_properties = getToolByName(obj,
                                          'portal_properties')
        geo_properties = getattr(portal_properties,
                                 'geographical_properties', None)
        if not geo_properties:
            return geodata

        service_keys['google_key'] = geo_properties.getProperty(
            'google_key', '')
        service_keys['yahoo_key'] = geo_properties.getProperty(
            'yahoo_key', '')
        service_keys['mapquest_key'] = geo_properties.getProperty(
            'mapquest_key', '')
        geocoding_to_use = geo_properties.getProperty(
            'geocoding_service_priority', [])

        geodata = geocodeLocation(location, service_keys, geocoding_to_use)
        return geodata

    def provideInterfaces(self, obj, geodata):
        """ Provide interfaces
        """
        for iface in self.ifaces:
            if not iface.providedBy(obj):
                alsoProvides(obj, iface)
            geoevent = IGeoPosition(obj)
            geoevent.setLatitude(geodata[0])
            geoevent.setLongitude(geodata[1])
            geoevent.setCountryCode(geodata[2])

    def run(self, obj):
        """ Run
        """
        geodata = self.matchLocation(obj)
        if geodata:
            self.provideInterfaces(obj, geodata)
        else:
            for iface in self.ifaces:
                if iface.providedBy(obj):
                    directlyProvides(obj, directlyProvidedBy(obj)-iface)

def geopositionEventHandler(obj, event):
    """ Event handler """
    decider = getUtility(IGeoPositionDecider, context=obj)
    decider.run(obj)


#
#Geocoding related, we use Google, Yahoo and Mapquest services
#

def geocodeLocation(location, service_keys, services):
    """ Geocode location """
    for service in services:
        if service.find('Google') != -1:
            geoGoogle = geocodeGoogle(location, service_keys)
            if geoGoogle:
                return geoGoogle

        if service.find('Yahoo') != -1:
            geoYahoo = geocodeYahoo(location, service_keys)
            if geoYahoo:
                return geoYahoo

        #TODO: adapt Mapquest service to work only with address. Now is disabled
        if service.find('Mapquest') != -1:
            pass
            #geoMapquest = geocodeMapquest(location, service_keys)
            #if geoMapquest: return geoMapquest
    return None

def geocodeGoogle(location, service_keys, service_type='xml'):
    """ Google service """
    if service_type == 'xml':
        return geocodeGoogleXML(location, service_keys)
    elif service_type == 'csv':
        return geocodeGoogleCSV(location, service_keys)
    else:
        return None

def geocodeGoogleCSV(location, service_keys):
    """ Google geocode via CSV """
    params = {'output': 'csv',
              'q'     : location,
              'key'   : service_keys['google_key']}
    u = urllib.urlopen(
        "http://maps.google.com/maps/geo?%s" % urllib.urlencode(params))
    gbuffer = u.read()
    try:
        control_code, _acc, latitude, longitude = str(gbuffer).split(',')
        if (control_code == '200'):
            #TODO: implement get country code
            res = (latitude, longitude, '')
        else:
            res = None
            logger.warning('Geocoding via Google CSV failed')
    except Exception:
        res = None
        logger.warning('Geocoding via Google CSV failed')
    return res

def geocodeGoogleXML(location, service_keys):
    """ Google geocode via XML """
    #addresses = []
    try:
        params = {'output': 'xml',
                  'q'     : location.encode('utf-8'),
                  'key'   : service_keys['google_key']}

        # parse the xml contents of the url into a dom
        dom = parse(urllib.urlopen(
            "http://maps.google.com/maps/geo?%s" % urllib.urlencode(params)))
        results = dom.getElementsByTagName('Response')
        #result_count = len(results)
        for result in results:
            for mark in result.getElementsByTagName('Placemark'):
                geoInfo = mark.getElementsByTagName('Point')[
                          0].getElementsByTagName('coordinates')[
                          0].childNodes[0].nodeValue.split(',')
                lat = geoInfo[1]
                longitude = geoInfo[0]

                cc = mark.getElementsByTagName('AddressDetails')[
                     0].getElementsByTagName('Country')[
                     0].getElementsByTagName('CountryNameCode')[
                     0].childNodes[0].nodeValue

        res = (lat.encode('utf-8'), longitude.encode('utf-8'),
               cc.encode('utf-8'))
    except Exception:
        res = None
        logger.warning('Geocoding via Google XML failed')
    return res

def geocodeYahoo(location, service_keys):
    """ Yahoo service """
    addresses = []
    try:
        params = {'appid'   : service_keys['yahoo_key'],
                  'location': location.encode('utf-8')}

        # parse the xml contents of the url into a dom
        dom = parse(urllib.urlopen(
            "http://api.local.yahoo.com/MapsService/V1/geocode?%s" %
            urllib.urlencode(params)))
        results = dom.getElementsByTagName('Result')
        #result_count = len(results)
        for result in results:
            d = {'precision': result.getAttribute('precision'),
                 'warning': result.getAttribute('warning')}
            for itm in result.childNodes:
                # if precision is zip, Address childNode will not exist
                if itm.childNodes:
                    d[itm.nodeName] = itm.childNodes[0].data
                else:
                    d[itm.nodeName] = ''
            addresses.append(d)
        addr = addresses[0] #take the first one, it should be the good one
        res = (addr['Latitude'].encode('utf-8'), addr['Longitude'].encode(
            'utf-8'), addr['Country'].encode('utf-8'))
    except Exception:
        res = None
        logger.warning('Geocoding via Yahoo failed')
    return res

def geocodeMapquest(location, service_keys):
    """ Mapquest service """
    #addresses = []
    parms = {'transaction': 'geocode',
             'address':location,
             'postalcode':'',
             'country':'',
             'key': service_keys['mapquest_key']}
    try:
        url = ('http://web.openapi.mapquest.com/oapi/transaction?' %
               urllib.urlencode(parms))
        dom = parse(urllib.urlopen(url))
        results = dom.getElementsByTagName('geocode')
        #result_count = len(results)

        d = {}
        for result in results:
            for itm in result.childNodes:
                if itm.childNodes:
                    if itm.nodeName == 'locations':
                        for child in itm.childNodes[2].childNodes:
                            if child.nodeName == 'geocodeQuality':
                                d['geocodeQuality'] = child.childNodes[0]
                            if child.nodeName == 'latitude':
                                d['latitude'] = child.childNodes[0].data
                            if child.nodeName == 'longitude':
                                d['longitude'] = child.childNodes[0].data
        res = (d['longitude'].encode('utf-8'), d['latitude'].encode('utf-8'))
    except Exception:
        res = None
        logger.warning('Geocoding via Mapquest failed')
    return res
