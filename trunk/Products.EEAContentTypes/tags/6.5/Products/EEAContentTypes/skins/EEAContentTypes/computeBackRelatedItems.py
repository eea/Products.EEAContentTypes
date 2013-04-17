## Script (Python) "computeBackRelatedItems"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=find related items for an object
##

from AccessControl import Unauthorized

if hasattr(context, 'getRelatedItems'):
    incoming = context.getBRefs('relatesTo') 
    res = []
    mtool = context.portal_membership
    
    for d in range(len(incoming)):
        try:
            obj = incoming[d]
	except Unauthorized:
            continue
        if obj not in res:
            if mtool.checkPermission('View', obj):
                res.append(obj)
    
    return res





