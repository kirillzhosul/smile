from typing import Dict, Any, List, Union
from smile.types import Scope
from smile.routing import parse_args_from_scope


class URL:
    path: str
    query_args: Dict[str, Any]

    def __init__(self, scope: Scope) -> None:
        self.path = scope.get("root_path", "") + scope["path"]
        self.query_args = parse_args_from_scope(scope=scope)


class Request:
    """
    Request information for endpoint.
    """

    url: URL
    headers: Dict[str, Any]

    def __init__(self, scope: Scope):
        self.scope = scope

    @property
    def method(self) -> str:
        return self.scope["method"]

    @property
    def app(self) -> Any:
        return self.scope["app"]

    @property
    def cookies(self) -> Dict[str, str]:
        if not hasattr(self, "_cookies"):
            self._cookies = self.headers.get("cookie").split("; ")
        return self._cookies

    @property
    def state(self) -> Dict[str, Any]:
        if not hasattr(self, "_state"):
            self._state = self.scope["state"]
        return self._state

    @property
    def url(self) -> URL:
        if not hasattr(self, "_url"):
            self._url = URL(scope=self.scope)
        return self._url

    @property
    def headers(self) -> URL:
        if not hasattr(self, "_headers"):
            self._headers = _build_headers_dict(raw_headers=self.scope["headers"])
        return self._headers


def _build_headers_dict(raw_headers: List[Union[bytes, bytes]]) -> Dict[str, Any]:
    headers_dict = dict()
    for header_name, header_value in raw_headers:
        headers_dict[header_name.decode("utf-8")] = header_value.decode("utf-8")
    return headers_dict
