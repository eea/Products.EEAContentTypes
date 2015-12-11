##bind context=context
##title=used in gis_view for full screen mode

# return the remote url striped by the flash file.
from Products.PythonScripts.standard import html_quote
request = container.REQUEST
RESPONSE =  request.RESPONSE

gisurl = context.remoteUrl
gisurlroot = ''
query = ''

#strip query if present
idx = gisurl.find('?')
if idx>0:
        query = gisurl[idx:]
        gisurl = gisurl[:idx]

#strip flash file
idx = gisurl.rfind('/')

if idx:
    gisurlroot = gisurl[:idx]

gisurlroot = gisurlroot + query

return gisurlroot
