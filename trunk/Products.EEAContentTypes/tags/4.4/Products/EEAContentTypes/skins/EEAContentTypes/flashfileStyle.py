## Script (Python) "flashfileStyle"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=style for clean flashfile templat
##
width = context.getWidth()
height = context.getHeight()

style = "margin: 0 0 0 -%spx;" % int(width/2)

return style
