import logging
from logging import NullHandler

from lumapps.client import LumAppsApiClient  # noqa

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(NullHandler())
