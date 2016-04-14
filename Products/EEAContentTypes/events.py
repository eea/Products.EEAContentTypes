""" Event handlers
"""
from DateTime import DateTime
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import Attribute
from zope.interface import implements


def handle_content_state_changed(obj, event):
    """ Set effective to now if effected is not set and object is published
    """
    _marker = object()
    if event.workflow.getInfoFor(obj, 'review_state', _marker) == 'published':
        effective = event.object.effective_date
        if not effective:
            now = DateTime()
            obj.setEffectiveDate(now)


class IGISMapApplicationWillBeRemovedEvent(IObjectEvent):
    """An interactive map will be removed."""
    oldParent = Attribute("The old location parent for the object.")
    oldName = Attribute("The old location name for the object.")


class GISMapApplicationWillBeRemovedEvent(ObjectEvent):
    """An interactive map will be removed from a container.
    """
    implements(IGISMapApplicationWillBeRemovedEvent)

    def __init__(self, obj, oldParent=None, oldName=None):
        ObjectEvent.__init__(self, obj)
        self.oldParent = oldParent
        self.oldName = oldName
