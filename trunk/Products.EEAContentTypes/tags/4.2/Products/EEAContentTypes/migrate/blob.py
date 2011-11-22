""" Migrate File/Image Field to BlobField
"""
import logging
from StringIO import StringIO
from Products.Archetypes.Field import Image as ZODBImage
from OFS.Image import File as ZODBFile
from Products.Five.browser import BrowserView

logger = logging.getLogger('EEAContentTypes.migrate')

class Migrate(BrowserView):
    """ Migrate Highlight image field from OFS.Image
        to plone.app.blob BlobField
    """
    def __init__(self, context, request):
        super(Migrate, self).__init__(context, request)
        self._status = False
        self._field = 'image'
        self._ztype = ZODBImage

    @property
    def status(self):
        """ Migration status
        """
        return self._status

    @property
    def field(self):
        """ Field to migrate
        """
        return self._field

    @property
    def ztype(self):
        """ Field type
        """
        return self._ztype

    def migrate(self, field):
        """ Migrate OFS.Image to blob
        """
        storage = field.getStorage()
        try:
            zfile = storage.get(self.field, self.context)
        except AttributeError:
            logger.info('\t There is no %s to migrate', self.field)
            return False

        if not isinstance(zfile, self.ztype):
            logger.info('\t %s is already a Blob', self.field)
            return False

        data = StringIO(zfile.data)
        filename = getattr(zfile, 'filename', self.context.getId())
        if isinstance(filename, unicode):
            filename = filename.encode('utf-8')
        data.filename = filename

        ctype = getattr(zfile, 'content_type', None)
        if ctype:
            if isinstance(ctype, unicode):
                ctype = ctype.encode('utf-8')
            data.content_type = ctype

        field.getMutator(self.context)(data)
        logger.info('\t %s is now a Blob', self.field)
        return True

    def migrate_scales(self, field):
        """ Migrate OFS.Image scales to blobs
        """
        storage = field.getStorage()
        sizes = field.getAvailableSizes(self.context).keys()
        logger.info('\t Updating image scales: %s', ', '.join(sizes))
        for size in sizes:
            storage.unset('image_%s' % size, self.context)
            field.getScale(self.context, size)
        return True

    def __call__(self, **kwargs):
        field = self.context.getField(self.field)

        logger.info('Updating %s %s field to blob',
                    self.context.absolute_url(1), self.field)

        self._status = self.migrate(field)
        self._status = self.migrate_scales(field) and self._status
        return "Migration complete. Check the Zope log for more details."

class FlashFileMigrate(Migrate):
    """ Custom migration script for Flash File
    """
    def __init__(self, context, request):
        super(FlashFileMigrate, self).__init__(context, request)
        self._field = 'file'
        self._ztype = ZODBFile

    def migrate_scales(self, field):
        """ FileField has no scales
        """
        return True
