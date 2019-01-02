import sys

sys.path.insert(0, './libs')

__version__ = "0.1"

from .lib import ApiClient, ApiCallError

__all__ = ['ApiClient', 'ApiCallError']
