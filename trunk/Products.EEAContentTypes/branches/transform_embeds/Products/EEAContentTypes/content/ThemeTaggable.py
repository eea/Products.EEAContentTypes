""" ThemeTaggable """
from eea.themecentre.content.ThemeTaggable import ThemeTaggable
from eea.themecentre.content.ThemeTaggable import ThemeTaggable_schema
from eea.themecentre.content.ThemeTaggable import MaxValuesValidator

import warnings
warnings.warn("ThemeTaggable is deprecated. "
              "Please use eea.themecentre.content.ThemeTaggable instead",
              DeprecationWarning)

__all__ = [
    ThemeTaggable.__name__,
    ThemeTaggable_schema.__name__,
    MaxValuesValidator.__name__,
]
