"""django-agentweb — make Django sites first-class citizens of the agentic web.

See PEP 386 (https://peps.python.org/pep-0386/).
"""

__version__ = "0.1.0"
__version_info__ = tuple(
    int(i) if i.isdigit() else i for i in __version__.split(".")
)
__license__ = "MIT"
__title__ = "django-agentweb"

__author__ = "DLRSP"
__copyright__ = "Copyright 2010-present DLRSP"

# Version synonym
VERSION = __version_info__
