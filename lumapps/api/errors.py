from httpx import HTTPStatusError


def get_http_err_content(e: HTTPStatusError) -> str:
    try:
        return e.response.content.decode()  # type: ignore
    except AttributeError:
        return ""


class BaseClientError(Exception):  # pragma: no cover
    """ Base error of the BaseClient """


class BadCallError(BaseClientError):  # pragma: no cover
    """ Retrocompatiblity """


class LumAppsClientError(BaseClientError):  # pragma: no cover
    def __init__(self, code, message=None):
        super().__init__(message)
        self.code = code


class LumAppsClientConfError(BaseClientError):  # pragma: no cover
    def __init__(self, message=None):
        super().__init__(message)


class MissingMetadataError(LumAppsClientError):  # pragma: no cover
    def __init__(self, message):
        super().__init__("MISSING_METADATA", message)


class FileUploadError(LumAppsClientError):  # pragma: no cover
    def __init__(self, message):
        super().__init__("FILE_UPLOAD", message)


class FolderCreationError(LumAppsClientError):  # pragma: no cover
    def __init__(self, message):
        super().__init__("FILE_UPLOAD", message)


class FileDownloadError(LumAppsClientError):  # pragma: no cover
    def __init__(self, message):
        super().__init__("FILE_DOWNLOAD", message)


class NonIdpGroupInCommunityError(LumAppsClientError):  # pragma: no cover
    def __init__(self, message):
        super().__init__("NON_IDP_GROUP_IN_COMMUNITY", message)


class FeedsRequiredError(LumAppsClientError):  # pragma: no cover
    def __init__(self, message):
        super().__init__("FEEDS_REQUIRED", message)


class UrlAlreadyExistsError(LumAppsClientError):  # pragma: no cover
    def __init__(self, message):
        super().__init__("URL_ALREADY_EXISTS", message)


class GetTokenError(LumAppsClientError):  # pragma: no cover
    def __init__(self, message):
        super().__init__("GET_TOKEN", message)


class UserCannotSaveError(LumAppsClientError):  # pragma: no cover
    def __init__(self, message):
        super().__init__("USER_CANNOT_SAVE", message)


class LumAppsError(Exception):  # pragma: no cover
    pass


##
#  Jwt Errors
##


class LumAppsJWTError(LumAppsError):  # pragma: no cover
    pass


class LumAppsJWTClaimsError(LumAppsJWTError):  # pragma: no cover
    pass


class LumAppsJwtTokenExpiredError(LumAppsJWTError):  # pragma: no cover
    def __init__(self, message):
        super().__init__("TOKEN_EXPIRED", message)


class LumAppsJwtInvalidClaimError(LumAppsJWTError):  # pragma: no cover
    def __init__(self, message):
        super().__init__("INVALID_CLAIMS", message)


class LumAppsJwtCustomError(LumAppsJWTError):  # pragma: no cover
    def __init__(self, message):
        super().__init__("CUSTOM_ERROR", message)


class LumAppsJwtHeaderError(LumAppsJWTError):  # pragma: no cover
    def __init__(self, message):
        super().__init__("INVALID_HEADER", message)
