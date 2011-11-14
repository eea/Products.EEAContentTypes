##title=Retrieve a list of recently published items
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

results = context.queryCatalog()
return context.kupuInfoForBrains(results)
