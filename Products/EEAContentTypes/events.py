from DateTime import DateTime

def handle_content_state_changed(obj, event):

    _marker = object()
    if event.workflow.getInfoFor(obj, 'review_state', _marker) == 'published':
        effective = event.object.effective()
        if not effective:
            now = DateTime()
            object.setEffectiveDate(now)

