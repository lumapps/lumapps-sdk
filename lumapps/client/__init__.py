import warnings

from lumapps.api import ApiClient  # noqa

warnings.filterwarnings("default", category=DeprecationWarning)
warnings.warn(
    "Importing from lumapps.client is deprecated. It will soon be removed. Update your "
    "code to import from lumapps or lumapps.api",
    DeprecationWarning,
    stacklevel=2,
)
