""" Validators """

from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation
from zope.interface import implements
import PIL
from cStringIO import StringIO
from OFS.Image import Pdata
from Acquisition import aq_base
import re
import urllib2
from Products.Archetypes.interfaces import ISchema

class ManagementPlanCodeValidator:
    """ Validator
    """
    implements(IValidator)

    def __init__(self,
                 name,
                 title='Management plan code',
                 description='Management plan code validator'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):
        """ check if management plan code is in right format """
        # check we have 3 digits separated by dots
        errmsg = "Validation failed, management plan code is not in " \
                 "the format #.#.# e.g. 1.5.2"
        digits = value[1].split('.')
        if len(digits) == 3:
            for dig in digits:
                try:
                    int(dig)
                except ValueError:
                    return (errmsg)
            return 1
        else:
            return (errmsg)

validation.register(
    ManagementPlanCodeValidator('management_plan_code_validator'))


class ImageMinSize:
    """ Image minimum size validator
    """
    implements(IValidator)

    def __init__( self, name, title='ImageSizeValidator',
                        description='Image size validator'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        """ check to see if the image is at least 1024px """
        try:
            image = PIL.Image.open(value)
        except AttributeError:
            # OFS Image 
            data = getattr(aq_base(value), 'data')
            if isinstance(data, Pdata):
                data = str(data)
            img_stream = StringIO(data)
            image = PIL.Image.open(img_stream)
        if image.size[0] < 1024:
            return "Image needs to be at least 1024px in width"
        return 1

validation.register(ImageMinSize('imageMinSize'))


# validator functions used for youtube cloudUrl check for mediacentre
# and eeacontenttypes
def youtube_params(vid_url, params = None):
    """ youtube iframe used for cloudUrl field setter
    """
    symbol = "&" if "?" in vid_url else "?"
    params = params or symbol + "autoplay=1&playnext=1&egm=1&rel=1" \
                                            "&fs=1&wmode=opaque"
    return '<iframe width="640" height="360" ' \
            'src="http://www.youtube.com/embed/%s%s" ' \
            'frameborder="0" allowfullscreen></iframe>' % (vid_url, params)

def youtube_cloud_validator(value, instance = None):
    """ check if cloudUrl has a youtube link and construct an iframe out
    of it if it's just a link
    """
    pattern = re.compile('[0-9a-zA-z]{8,100}')
    obj_schema = ISchema(instance)
    field = obj_schema['cloudUrl']
    mutator = field.getMutator(instance)
    value = value or ""
    if 'youtu.be' in value:
        # transform youtu.be links iframe code
        url = urllib2.urlopen(value).url
        res = pattern.findall(url)
        if 'list' in url:
            vid_url = res[0] + '?list=' + res[-1]
        else:
            vid_url = res[0]
        value = youtube_params(vid_url)

    elif 'playlist' in value:
        # transform playlist link to iframe code
        res = pattern.findall(value)
        vid_url = 'videoseries?list=' + res[1]
        value = youtube_params(vid_url)

    elif ('youtube' in value) and ('iframe' not in value):
        # transform long youtube link to iframe code
        res = pattern.findall(value)
        if 'list' in value:
            vid_url = res[0] + '?list=' + res[-1]
        else:
            vid_url = res[0]
        value = youtube_params(vid_url)

    mutator(value)

class YoutubeCloudUrlValidator:
    """ Image minimum size validator
    """
    implements(IValidator)

    def __init__( self, name, title='YoutubeCloudUrlValidator',
                        description='YoutubeCloudUrl Validator'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        """ check and transform links if we don't get iframe code
        for youtube
        """
        youtube_cloud_validator(value, instance)

validation.register(YoutubeCloudUrlValidator('youtubeCloudUrlValidator'))
