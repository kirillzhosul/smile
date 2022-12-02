from typing import Any, Optional, Mapping, List, Tuple
from smile.types import Scope, Receive, Send


class BaseResponse:
    http_status_code: int = 200
    http_headers: List[Tuple[bytes, bytes]] = []
    http_body: bytes = b""
    http_body_encoding_charset = "utf-8"
    http_media_type: Optional[str] = None

    def __init__(
        self,
        content: Any,
        status_code: int,
        headers: Optional[Mapping[str, str]] = None,
        media_type: Optional[str] = None,
    ):
        """
        :param content: Response body data.
        :param status_code: HTTP status code.
        :param headers: Headers mapping.
        :param media_type: By default should not overriden as declared by response classes.
        """
        if media_type is not None:
            self.http_media_type = media_type
        self.http_status_code = status_code

        self.http_body = self._render_body_to_content(content=content)
        self.http_headers = self._convert_headers(headers)

    def _convert_headers(
        self, headers: Optional[Mapping[str, str]] = None
    ) -> List[Tuple[bytes, bytes]]:
        """
        Convert headers in to the bytes.
        """
        if headers is None:
            return []

        # Add required content type header if not specified.
        if self.http_media_type is not None and "content-type" not in headers:
            content_type_header = self.http_media_type
            if content_type_header.startswith("text/"):
                content_type_header += f"; charset={self.http_body_encoding_charset}"
            headers["content-type"] = content_type_header

        return [
            (k.lower().encode("latin-1"), v.encode("latin-1"))
            for k, v in headers.items()
        ]

    def _render_body_to_content(
        self, content: Any, *, _override_body_encoding_charset: Optional[str] = None
    ) -> bytes:
        """
        Converts content to bytes with encoding.
        """
        if content is None:
            return b""
        if isinstance(content, bytes):
            return content
        encoding_charset = (
            _override_body_encoding_charset
            if _override_body_encoding_charset is not None
            else self.http_body_encoding_charset
        )
        return content.encode(encoding_charset)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handles response processing.
        """
        await send(
            {
                "type": "http.response.start",
                "status": self.http_status_code,
                "headers": self.http_headers,
            }
        )
        await send({"type": "http.response.body", "body": self.http_body})


class PlainResponse(BaseResponse):
    """
    Response with just plain text.
    """

    http_media_type: Optional[str] = "text/plain"


class HTMLResponse(BaseResponse):
    """
    Response with HTML (Markup).
    """

    http_media_type: Optional[str] = "text/html"
