from typing import Any, Callable, List, Optional, Tuple, Dict, Union
from inspect import iscoroutinefunction, signature
from inspect import Parameter as SignatureParameter
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

    def _build_endpoint_func_args(
        self, endpoint_func: Callable, parsed_args: Dict[str, Any]
    ) -> Union[Dict[str, Any], BaseResponse]:
        endpoint_func_signature = signature(endpoint_func)
        endpoint_kwargs = dict()

        for param in endpoint_func_signature.parameters.values():
            param_type = param.annotation
            param_kind = param.kind
            if param_kind == SignatureParameter.POSITIONAL_ONLY:
                return PlainResponse(
                    f"Validation error! {param.name} is positional only, which is not supported currently by framework!",
                    status_code=400,
                )
            if param_kind in (
                SignatureParameter.VAR_POSITIONAL,
                SignatureParameter.VAR_KEYWORD,
            ):
                return PlainResponse(
                    f"Validation error! Has nothing to do with *args or **kwargs params, currently (or forever) is not supported by framework!",
                    status_code=400,
                )
            if param_type == SignatureParameter.empty:
                return PlainResponse(
                    f"Validation error! {param.name} has unknown-type to parse!",
                    status_code=400,
                )
            param_is_missing = False
            try:
                parsed_param_value = parsed_args[param.name]
            except KeyError:
                param_is_missing = True
                if param.default == SignatureParameter.empty:
                    return PlainResponse(
                        f"Validation error! {param.name} is missing!", status_code=400
                    )
            if param_is_missing:
                param_value = param.default
            else:
                try:
                    param_value = param_type(parsed_param_value)
                except ValueError:
                    return PlainResponse(
                        f"Validation error! {param.name} has invalid value!",
                        status_code=400,
                    )
            endpoint_kwargs[param.name] = param_value
        return endpoint_kwargs

    def _parse_args_from_scope(self, scope: Scope) -> Dict[str, str]:
        query_args = scope.get("query_string", b"").decode("utf-8").split("&")
        parsed_args = dict()
        for query_arg in query_args:
            if not query_arg:
                continue
            query_args_name, query_arg_value = query_arg.split("=")
            parsed_args[query_args_name] = query_arg_value
        return parsed_args

    async def _handle_request_to_endpoint(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        """
        Handles request and returns Response.
        """
        requested_path = scope.get("path", "/")
        for route_path, route_endpoint_func in self.routes.items():
            if route_path == requested_path:
                endpoint_kwargs = self._build_endpoint_func_args(
                    endpoint_func=route_endpoint_func,
                    parsed_args=self._parse_args_from_scope(scope=scope),
                )
                if isinstance(endpoint_kwargs, BaseResponse):
                    return await endpoint_kwargs(scope, receive, send)
                if iscoroutinefunction(route_endpoint_func):
                    response = await route_endpoint_func(**endpoint_kwargs)
                else:
                    response = route_endpoint_func(**endpoint_kwargs)
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
