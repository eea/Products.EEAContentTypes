""" Validators """
import difflib
from cStringIO import StringIO
import re
from lxml import html
from Acquisition import aq_base

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation
from Products.Archetypes.interfaces import ISchema
from Products.EEAContentTypes.config import EEAMessageFactory as _
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
import PIL
from OFS.Image import Pdata
from persistent.dict import PersistentDict

has_opencv = True
try:
    import cv2
except ImportError:
    has_opencv = False



KEY = 'eea.mediacentre.multimedia'


class ManagementPlanCodeValidator(object):
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
                    return errmsg
            return 1
        else:
            return errmsg


validation.register(
    ManagementPlanCodeValidator('management_plan_code_validator'))


class ImageMinSize(object):
    """ Image minimum size validator
    """
    implements(IValidator)

    def __init__(self, name, title='ImageSizeValidator',
                 description='Image size validator'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        """ check to see if the image is at least 1024px """
        # do not run the validator if attempting to delete
        # the image
        if value == "DELETE_IMAGE":
            return 1
        try:
            image = PIL.Image.open(value)
        except AttributeError:
            # OFS Image
            data = getattr(aq_base(value), 'data')
            if isinstance(data, Pdata):
                data = str(data)
            img_stream = StringIO(data)
            image = PIL.Image.open(img_stream)
        pprops = getToolByName(instance, 'portal_properties')
        width = 1920
        height = 1080
        if pprops:
            iprops = pprops.imaging_properties
            width_val = iprops.getProperty('min_width_validator', [])
            for val in width_val:
                if instance.portal_type in val:
                    width = int(val.split('|')[1])
                    height = int(val.split('|')[2])
        if image.size[0] < width:
            return "Image needs to be at least %spx in width" % width
        if image.size[1] < height:
            return "Image needs to be at least %spx in height" % height
        return 1


validation.register(ImageMinSize('imageMinSize'))


def video_cloud_validator(value, instance=None):
    """ check if cloudUrl has a youtube or vimeo link, saves the id
    in an annotation and save a clean link to the video for the field
    """
    obj_schema = ISchema(instance)
    field = obj_schema['cloudUrl']
    if value in field.getAccessor(instance)():
        return
    mutator = field.getMutator(instance)
    if value:
        youtube_id = re.compile(r'[0-9a-zA-z\-_]{8,}[A-Z]*')
        youtube_url = "http://www.youtube.com/watch?v="
        vimeo_url = "http://vimeo.com/"

        annotations = IAnnotations(instance)
        mapping = annotations.get(KEY)
        if mapping is None:
            cloud_url = {'cloud_url': PersistentDict()}
            mapping = annotations[KEY] = PersistentDict(cloud_url)

        if 'cmshare' in value:
            mapping['cloud_url']['cmshare'] = value if 'download' in value \
                else value + '/download'

            # remove youtube entry if found since youtube macro
            # is before vimeo
            cloud = mapping['cloud_url']
            if cloud.get('vimeo'):
                cloud.pop('vimeo')
            if cloud.get('youtube'):
                cloud.pop('youtube')

            if has_opencv:
                cap = cv2.VideoCapture(mapping['cloud_url']['cmshare'])
                ret, frame = cap.read()
                if not frame:
                    return
                ee = PIL.Image.fromarray(frame)

                destfile = StringIO()
                ee.save(destfile, 'JPEG')
                destfile.seek(0)
                instance.setImage(destfile.getvalue())

                cap.release()
                cv2.destroyAllWindows()
        elif 'youtu' and 'playlist' in value:
            # transform youtube playlist link
            res = youtube_id.findall(value)[1]
            vid_id = 'videoseries&' + 'list=' + res
            value = 'http://www.youtube-nocookie.com/playlist?list=' + res
            mapping['cloud_url']['youtube'] = vid_id
            # remove youtube entry if found since youtube macro
            # is before vimeo
            cloud = mapping['cloud_url']
            if cloud.get('vimeo'):
                cloud.pop('vimeo')
            if cloud.get('cmshare'):
                cloud.pop('cmshare')

        elif 'youtu' in value:
            # check youtube links with youtu since they might be
            # used with youtu.be our youtube.com links
            res = youtube_id.findall(value)
            if 'list' in value:
                vid_id = res[0] + '?list=' + res[1]
            else:
                vid_id = res[0]
            value = youtube_url + vid_id
            mapping['cloud_url']['youtube'] = vid_id
            # remove youtube entry if found since youtube macro
            # is before vimeo
            cloud = mapping['cloud_url']
            if cloud.get('vimeo'):
                cloud.pop('vimeo')
            if cloud.get('cmshare'):
                cloud.pop('cmshare')

        elif 'vimeo' in value:
            vimeo = re.compile(r'[\d]{5,}')
            vid_id = vimeo.findall(value)[0]
            value = vimeo_url + vid_id
            cloud = mapping['cloud_url']
            # remove youtube entry if found since youtube macro
            # is before vimeo
            if cloud.get('youtube'):
                cloud.pop('youtube')
            if cloud.get('cmshare'):
                cloud.pop('cmshare')
            cloud['vimeo'] = vid_id
        else:
            return "Please enter a video link from Cmshare, Youtube or " \
                   "Vimeo only"

    mutator(value)


class VideoCloudUrlValidator(object):
    """ Image minimum size validator
    """
    implements(IValidator)

    def __init__(self, name, title='VideoCloudUrlValidator',
                 description='VideoCloudUrl Validator'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        """ check and transform links for video embedding
        """
        res = video_cloud_validator(value, instance)
        if res:
            return res


validation.register(VideoCloudUrlValidator('videoCloudUrlValidator'))


class ImageCaptionRequiredIfImageValidator(object):
    """ Image caption validator
    """
    implements(IValidator)

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        image = instance.getImage()
        caption = instance.getImageCaption()
        if (image or value and value.filename) and not caption:
            return "Image caption is required for your image."
        return 1


validation.register(ImageCaptionRequiredIfImageValidator('ifImageRequired'))


class ExistsKeyFactsValidator(object):
    """ Check if markup with keyFacts class has been added and if so add a new
    key fact within a 'key-facts' directory of the given contenttype
    """
    implements(IValidator)

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description
        self.factory_object = False

    @staticmethod
    def createKeyFact(fact_text, folder, keyfact_id, existing_facts):
        """
        :param fact_text: the text value of the html fact object
        :param folder: folder where SOERKeyFact will be created
        :param keyfact_id: pattern name of created facts
        :param existing_facts: the currently existing_facts
        """
        folder.invokeFactory(type_name="SOERKeyFact",
                             id=keyfact_id)
        soer_keyfact = folder.get(keyfact_id)
        themes = folder.getField('themes').getRaw(folder)
        tags = folder.Subject()
        soer_keyfact.processForm(data=1, metadata=1, values={
            'title': keyfact_id,
            'description': fact_text,
            'subject': tags,
            'themes': themes
        }
                                 )
        existing_facts.append(soer_keyfact)

    def createKeyFacts(self, existing_facts, existing_facts_len,
                       existing_facts_updated, fact, folder,
                       i):
        """
        :param existing_facts: existing soer keyfacts created within the
               key-facts folder
        :param existing_facts_len: length of existing keyfacts
        :param existing_facts_updated: length of existing keyfacts that have
                been updated
        :param fact: html object with class of keyFact which contains the
                description needed for the soer keyfacts
        :param folder: the folder used for storing the keyfacts
        :param i: iterator value
        """
        keyfact_id = 'keyfact-%d' % (i + 1)
        keyfact = folder.get(keyfact_id, None)
        fact_text = unicode(fact.text_content())
        new_facts = False
        if not keyfact:
            self.createKeyFact(fact_text, folder, keyfact_id,
                               existing_facts)
            new_facts = True
        else:
            match = False
            for child in existing_facts:
                description = child.getField('description')
                description_text = description.getRaw(child).decode('utf-8')
                match_ratio = difflib.SequenceMatcher(None,
                                                      description_text,
                                                      fact_text).ratio()
                # use standard library difflib module to check for the
                # ratio match of the two given strings and if they
                # have a high rate then update the keyfact description
                if 0.85 < match_ratio < 1.0:
                    match = True
                    description.set(child, fact_text)
                    child.reindexObject(idxs=["Description"])
                    existing_facts_updated += 1
                    break
                if match_ratio == 1.0:
                    match = True
                    break

            if not match:
                existing_facts_len += 1
                keyfact_id = 'keyfact-%d' % existing_facts_len
                new_facts = True
                self.createKeyFact(fact_text, folder, keyfact_id,
                                   existing_facts)
        return new_facts, existing_facts_updated

    def __call__(self, value, instance, *args, **kwargs):

        # only attempt to construct the keyFacts after the object has been moved
        # from the portal_factory
        if 'portal_factory' in instance.absolute_url(1):
            self.factory_object = True
            return 1
        # check if current value is same as the current value on the field
        field = kwargs.get('field')
        if field:
            raw_value = field.getRaw(instance)
            if raw_value == value and not self.factory_object:
                return 1

        # find content which has a keyFact class in order to add soer keyfacts
        content = html.fromstring(value.decode('utf-8'))
        facts = content.find_class('keyFact')
        facts_length = len(facts)

        new_facts_len = 0

        if facts_length:
            wftool = getToolByName(instance, 'portal_workflow')
            if not instance.get('key-facts', None):
                instance.invokeFactory(type_name="Folder", id="key-facts")
            folder = instance.get('key-facts')
            instance_review_state = wftool.getInfoFor(instance, 'review_state')
            folder_review_state = wftool.getInfoFor(folder, 'review_state')
            if instance_review_state != folder_review_state and \
                            folder_review_state != 'published':
                try:
                    workflow = wftool.getWorkflowsFor(folder)[0]
                    transitions = workflow.transitions
                    # attempt to give the same review_state for the folder as
                    # it's parent's review_state
                    for transition in wftool.getTransitionsFor(folder):
                        tid = transition.get('id')
                        tob = transitions.get(tid)
                        if not tob:
                            continue
                        if tob.new_state_id != instance_review_state:
                            continue
                        wftool.doActionFor(folder, tid)
                        break
                except WorkflowException:
                    pass

            folder_children = folder.objectValues()
            existing_facts_len = 0
            existing_facts_updated = 0
            existing_facts = []
            # count number of existing keyfacts
            for obj in folder_children:
                if "keyfact-" in obj.id:
                    existing_facts.append(obj)
                    existing_facts_len += 1

            children = []
            for i, nfact in enumerate(facts):
                if nfact.tag == "ul":
                    children = nfact.getchildren()
                    for j, fact in enumerate(children):
                        new_facts, existing_facts_updated = self.createKeyFacts(
                            existing_facts,
                            existing_facts_len,
                            existing_facts_updated,
                            fact, folder, j)
                        if new_facts:
                            existing_facts_len += 1
                            new_facts_len += 1
                else:
                    # check situation where
                    if nfact not in children:
                        new_facts, existing_facts_updated = self.createKeyFacts(
                            existing_facts,
                            existing_facts_len,
                            existing_facts_updated,
                            nfact, folder, i)
                    else:
                        new_facts = False
                    if new_facts:
                        existing_facts_len += 1
                        new_facts_len += 1

            status = IStatusMessage(instance.REQUEST)
            if new_facts_len:
                msg = u"Key facts have been extracted and stored from this " \
                      u"page. You may 'manage key facts' through the " \
                      u"contents tab"
                status.add(_(msg))
            if existing_facts_updated:
                msg = u"%d SOER KeyFact have been updated in the " \
                      u"'key-facts' folder of this content type" % \
                      existing_facts_updated
                status.add(_(msg))
        return 1


validation.register(ExistsKeyFactsValidator('existsKeyFacts'))


class MaxValuesValidator(object):
    """ Max values validator
    """
    implements(IValidator)

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        maxValues = getattr(kwargs['field'].widget, 'maxValues', None)
        values = value
        if isinstance(value, str):
            values = value.split(' ')
        if maxValues is not None and len(values) > maxValues:
            return "Too many words, please enter max %s words." % maxValues
        return 1


validation.register(MaxValuesValidator('maxWords'))


class RelatedItemsStorytellingValidator(object):
    """ Maximum 3 related items validator
    """
    implements(IValidator)

    def __init__(self, name, title='RelatedItemsValidator',
                 description='RelatedItemsValidator: maximum 3 items.'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        if len(value) > 3:
            return 'Too many related items. Please enter maximum 3 items!'
        return 1


validation.register(RelatedItemsStorytellingValidator('maxRelatedItems'))
