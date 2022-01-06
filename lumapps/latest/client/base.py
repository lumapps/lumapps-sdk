from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class Request:
    # The HTTP method, usually GET, POST, PUT or PATCH
    method: str
    # The requested URL
    url: str
    # The query parameters (?key=value)
    params: Mapping[str, str] = field(default_factory=dict)
    # The extra headers required to process the request
    headers: Mapping[str, str] = field(default_factory=dict)
    # The JSON content of the request
    json: Any = None


@dataclass(frozen=True)
class Response:
    status_code: int
    headers: Mapping[str, str]
    json: Any


class IClient(ABC):
    """
    The generic HTTP client for LumApps
    The implementation must handle authentification and specifics if necessary
    """

    @abstractmethod
    def request(self, request: Request, **kwargs: Any) -> Response:  # pragma: no cover
        """
        kwargs should be used for very niche behavior and not relied on extensively
        Most, if not all, implementations should NOT need to use it
        """
        pass
