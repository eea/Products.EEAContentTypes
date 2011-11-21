""" Cache
"""
#TODO: redo this stuff with plone.app.caching on plone4 migration

#from Acquisition import aq_parent, aq_inner
from Products.Five.browser import BrowserView
#from Products.CMFCore.utils import getToolByName
#from Products.CMFSquidTool.queue import queue
#from Products.CMFPlone import utils

class InvalidateCache(BrowserView):
    """ Invalidate cache
    """
    def invalidate(self):
        """ Invalidate """

        return "Purged done"

        #context = self.context
        #request = self.request
        #referer =  request.get('HTTP_REFERER','')
        #if referer.endswith('/'):
            #referer = referer[:-1]

        #parent = context
        #if utils.isDefaultPage(context, request):
            #parent  = aq_parent(aq_inner(context))

        #if (context.absolute_url() != referer and
            #parent.absolute_url() != referer):
            #request.response.setStatus(
                #401, 'invalidation not allowed from here')
            #return 'invalidation not allowed from here'

        #if request.get('HTTP_HOST', '') == 'nohost':
            ## browser test
            #res = True
        #else:
            #addr_list = ['127.0.0.1'] #IPs used for local dev

            #pp = getToolByName(context, 'portal_properties', None)
            #if pp:
                #ips_list = getattr(pp, 'eea_internal_ips', None)
                #if ips_list:
                    #addr_list.extend(ips_list.getProperty('allowed_ips', []))

            #addr = request.get('HTTP_X_FORWARDED_FOR','')
            #addr = addr or request.get('REMOTE_ADDR', '')

            #res = [True for ip in addr_list if addr.startswith(ip)]

        #if res:
            #recursive = request.get('recursive_invalidation' , False)
            #if recursive:
                #path = '/'.join(context.getPhysicalPath())
                #cat = getToolByName(context, 'portal_catalog', None)
                #result = cat(path = path)
                #for o in result:
                    #queue.queue(o.getObject())
            #else:
                #queue.queue(context)
                #if context != parent:
                    #queue.queue(parent)

            #return (request.response.redirect( parent.absolute_url() +
                #'?portal_status_message=Request for cache invalidation sent' ))

        #return request.response.redirect( parent.absolute_url() )


