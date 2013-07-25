""" Event handlers
"""
from DateTime import DateTime

def handle_content_state_changed(obj, event):
    """ Set effective to now if effected is not set and object is published
    """
    _marker = object()
    if event.workflow.getInfoFor(obj, 'review_state', _marker) == 'published':
        effective = event.object.effective()
        if not effective:
            now = DateTime()
            object.setEffectiveDate(now)

