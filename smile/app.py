from typing import Any, Callable, Optional, Tuple, Dict
from inspect import iscoroutinefunction
from smile.responses import BaseResponse, PlainResponse, JSONResponse
from smile.types import Scope, Receive, Send


class Smile:
    """
    Smile ASGI framework application.
    """

    def __init__(self):
        self.routes = dict()  # TODO: Rework routes system.

    def _alter_scope_on_call(self, scope: Scope) -> None:
        """
        Alters scope on call with required values.
        """
        scope["app"] = self

    def add_route(self, path: str, endpoint_func: Callable) -> None:
        # TODO: Rework routes system.
        self.routes[path] = endpoint_func

    def route(self, path: str) -> Callable:
        """
        Route decorator for endpoing function.

        Use example:
        @app.route("/path")
        def route():
            return BaseResponse("Hello world!")
        """

        def wrapper(route_func: Callable) -> Callable:
            self.add_route(path=path, endpoint_func=route_func)
            return route_func

        return wrapper

    def _wrap_response_in_response_class(self, response: Any) -> Optional[BaseResponse]:
        """
        Wraps response any in to the response class or returns None if dissalow type.
        """
        status_code = 200
        if isinstance(response, Tuple) and len(response) >= 2:
            content, status_code, *_ = response
            if isinstance(content, (str, Dict)):
                response = content
        if isinstance(response, str):
            response = PlainResponse(content=response, status_code=status_code)
        if isinstance(response, Dict):
            response = JSONResponse(content=response, status_code=status_code)
        if not isinstance(response, BaseResponse):
            return None
        return response

    async def _handle_request_to_endpoint(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        """
        Handles request and returns Response.
        """
        requested_path = scope.get("path", "/")
        for route_path, route_endpoint_func in self.routes.items():
            if route_path == requested_path:
                if iscoroutinefunction(route_endpoint_func):
                    response = await route_endpoint_func()
                else:
                    response = route_endpoint_func()
                response = self._wrap_response_in_response_class(response)
                if isinstance(response, BaseResponse):
                    return await response(scope, receive, send)
                await send({"type": "http.response.start", "status": 500})
                await send(
                    {
                        "type": "http.response.body",
                        "body": "Internal Server Error".encode("utf-8"),
                    }
                )
        await send({"type": "http.response.start", "status": 404})
        await send({"type": "http.response.body", "body": "Not Found".encode("utf-8")})

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        ASGI server request handler.
        """
        if scope["type"] != "http":
            # For now, do not process non-http requests events.
            return

        self._alter_scope_on_call(scope)
        await self._handle_request_to_endpoint(scope, receive, send)
