""" Transformers
"""
from Products.EEAContentTypes.transforms import internallink_view
from Products.EEAContentTypes.transforms import translationresolveuid

internallink_view.register()
translationresolveuid.register()
