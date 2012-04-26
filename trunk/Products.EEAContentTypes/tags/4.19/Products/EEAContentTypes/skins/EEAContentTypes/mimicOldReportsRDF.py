## Script (Python) "computeBackRelatedItems"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=exclude_series='',include_series='',replang='',theme=''
##title=mimic old reports.rdf script 
##

from DateTime import DateTime

catalog = context.portal_catalog
result = []
query = {'object_provides' : 'eea.reports.interfaces.IReportContainerEnhanced',
         'review_state' : 'published',
         'sort_on' : 'effective',
         'sort_order' : 'reverse',
         'effectiveRange' : DateTime()}

if replang:
    query['Language'] = replang

if theme:
    query['getThemes'] = theme
    
if exclude_series:
    series = exclude_series.split(',')
    for b in catalog(query):
        if b.serial_title[0] not in series:
            result.append(b)
else:
    if include_series:
        series = include_series.split(',')
        query['serial_title'] = series
    result = catalog(query)

return result
