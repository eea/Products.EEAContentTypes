from Products.CMFCore.utils import getToolByName

def moveObject(self, state_change, **kw):
    # get the object and its ID
    obj = state_change.object
    id = obj.getId()

    # get the src folder and the destination folder
    config = getToolByName(obj, 'portal_properties').frontpage_properties
    dstFldr = None
    types = (('News Item', news_folder),
             ('Highlight', highlight_folder),
             ('PressRelease', pressrelease_folder))

    for t, folderProp in types:
        if obj.portal_type == t:
            dstFldr = getattr(config, folderProp, None)
            break

    if not dstFldr:
        return

    if not dstFldr.startsWith('/'):
        portal = getToolByName(obj, 'portal_url')
        dstFldr = portl.getPortalObject().getPhysichalPath() + '/' + dstFldr

    dstFldr = obj.unrestrictedTraverse( dstFldr )
    srcFldr = obj.aq_parent

    # perform the move
    objs = srcFldr.manage_cutObjects([id,])
    dstFldr.manage_pasteObjects(objs)

    # get the new object
    new_obj = dstFldr[id]

    # pass new_obj to the error, *twice*
    raise state_change.ObjectMoved(new_obj, new_obj)
