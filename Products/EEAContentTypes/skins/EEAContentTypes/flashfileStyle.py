## Script (Python) "flashfileStyle"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=style for clean flashfile template
##
width = context.getWidth() or 0
height = context.getHeight() or 0

style = "margin: 0 0 0 -%spx;" % int(width/2)

return style
