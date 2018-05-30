"""Integration with GISMapApplication
"""
import logging
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from persistent.mapping import PersistentMapping
from zope.annotation.interfaces import IAnnotations

logger = logging.getLogger("eea.indicators")

KEY = 'GISMAPS_EMBEDS'

class GetGISMapEmbed(BrowserView):
    """Get the embed type for an interactive map that's set as related
    """

    def __call__(self):
        """Not usable standalone so we return self
        """
        return self

    def get_embed_type(self, uid):
        """Return interactive map's embed type as a string "static|interactive"
        """
        info = self.get_gismap().get(uid)
        if info:
            return info[1]  #only the embed type
        return None

    def get_gismap(self):
        """Given an object, it will return the interactive map+embed type
        assigned.

        It returns a mapping of
        <gismap uid A>:
            [gismap, embed_type],
        <gismap uid B>:
            [gismap, embed_type],
        """
        annot = IAnnotations(self.context).get(KEY, {})

        uids_cat = getToolByName(self.context, 'uid_catalog')
        info = {}
        for uid in annot.keys():
            brains = uids_cat.searchResults(UID=uid)
            if not brains:
                msg = "Couldn't find interactive map with UID %s" % uid
                logger.warning(msg)
                continue
            gismap = brains[0].getObject()
            if gismap is None:
                msg = "Couldn't find object for brain with UID %s" % uid
                logger.warning(msg)
                continue

            info[uid] = (gismap, annot.get(uid, None))

        return info

class SetGISMapEmbed(BrowserView):
    """Edit the embed type for an interactive map that's set as related.

    We store the values in an annotation on the context object;
    This annotation is a dictionary, where the keys are the UIDs
    of the interactive map objects and the value is a string
    "static|interactive"
    """

    def __call__(self):
        """Info is a dict of {uid: embed type} values
        """
        form = self.request.form
        uid = form.get("gismap_uid", "").strip()
        embed = form.get("embed", "interactive").strip()

        obj = self.context
        annot = IAnnotations(obj)

        if not KEY in annot:
            annot[KEY] = PersistentMapping()

        #just simple put sa pair (uid, embed) in the annotation
        annot[KEY][uid] = embed

        self.context._p_changed = True

        return "OK"

def handle_gismap_delete(context, event):
    """ Remove annotations from assessmentparts when an interactive map
        has been deleted
    """
    context_uid = context.UID()
    refs = context.getBRefs()

    for o in refs:
        annot = IAnnotations(o).get(KEY, {})
        if context_uid in annot.keys():
            del annot[context_uid]
            annot._p_changed = True
            o._p_changed = True
