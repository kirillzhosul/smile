from typing import Any, Callable, MutableMapping, Optional, Tuple, Dict, Type, Union
from inspect import iscoroutinefunction, signature
from inspect import Parameter as SignatureParameter
from smile.responses import BaseResponse, HTMLResponse, PlainResponse, JSONResponse
from smile.types import Scope, Receive, Send
from smile.routing import parse_args_from_scope
from smile.requests import Request

try:
    import jinja2

    jinja_is_installed = True
except ImportError:
    jinja_is_installed = False


class Smile:
    """
    Smile ASGI framework application.
    """

    def __init__(self):
        self.routes = dict()  # TODO: Rework routes system.
        self.error_handlers = dict()
        self._jinja_env = None

    def _alter_scope_on_call(self, scope: Scope) -> None:
        """
        Alters scope on call with required values.
        """
        scope["app"] = self
        scope["state"] = dict()

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

    def setup_jinja_environment(self, env) -> None:
        if not jinja_is_installed:
            raise ImportError("Jinja is installed, install by `pip install jinja2`!")
        if not isinstance(env, jinja2.Environment):
            raise TypeError(
                "Expected Jinja enviroment to be Jinja environment, not any other type!"
            )
        self._jinja_env = env

    async def jinja_template(
        self,
        name: str,
        globals: MutableMapping[str, Any] | None = None,
        parent: str | None = None,
        **context,
    ) -> str:
        if self._jinja_env is None:
            raise Exception(
                "Jinja environment is not installed! Please call `setup_jinja_environment`!"
            )
        if globals is None:
            globals = dict()
        return self._jinja_env.get_template(
            name=name, parent=parent, globals=globals | context
        )

    def add_error_handler(self, status_code: int, error_handler: Callable) -> None:
        self.error_handlers[status_code] = error_handler

    async def _wrap_response_in_response_class(
        self, response: Any
    ) -> Optional[BaseResponse]:
        """
        Wraps response any in to the response class or returns None if dissalow type.
        """
        status_code = 200
        if self._jinja_env is not None and jinja_is_installed:
            if isinstance(response, jinja2.Template):
                return HTMLResponse(
                    content=await response.render_async(), status_code=status_code
                )
        if isinstance(response, Tuple) and len(response) >= 2:
            content, status_code, *_ = response
            if isinstance(content, (str, Dict)):
                response = content
            if self._jinja_env is not None and jinja_is_installed:
                if isinstance(content, jinja2.Template):
                    return HTMLResponse(
                        content=await response.render_async(), status_code=status_code
                    )
        if isinstance(response, str):
            response = PlainResponse(content=response, status_code=status_code)
        if isinstance(response, Dict):
            response = JSONResponse(content=response, status_code=status_code)
        if not isinstance(response, BaseResponse):
            return None

        return response

    def _build_endpoint_func_args(
        self, endpoint_func: Callable, parsed_args: Dict[str, Any], scope: Scope
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
            param_is_internal = param_type in (Request, Smile)
            try:
                parsed_param_value = parsed_args[param.name]
            except KeyError:
                param_is_missing = True
                if param_is_internal:
                    if param_type == Request:
                        param_is_missing = False
                        parsed_param_value = Request(scope=scope)
                    elif param_type == Smile:
                        param_is_missing = False
                        parsed_param_value = self
                elif param.default == SignatureParameter.empty:
                    return PlainResponse(
                        f"Validation error! {param.name} is missing!", status_code=400
                    )
            if param_is_missing:
                param_value = param.default
            else:
                try:
                    param_value = (
                        parsed_param_value
                        if param_is_internal
                        else param_type(parsed_param_value)
                    )
                except TypeError:
                    return PlainResponse(
                        f"Validation error! {param.name} has invalid type (signature)!",
                        status_code=400,
                    )
                except ValueError:
                    return PlainResponse(
                        f"Validation error! {param.name} has invalid value!",
                        status_code=400,
                    )
            endpoint_kwargs[param.name] = param_value
        return endpoint_kwargs

    async def _process_with_error_handlers(self, response: BaseResponse):
        for target_status_code, error_handler in self.error_handlers.items():
            if response.http_status_code == target_status_code:
                error_handler_response = await self._wrap_response_in_response_class(
                    error_handler()
                )
                if not isinstance(error_handler_response, BaseResponse):
                    return PlainResponse("Internal Server Error!", status_code=500)

                return error_handler_response
        return response

    async def _handle_request_to_endpoint(
        self, scope: Scope, receive: Receive, send: Send
    ) -> BaseResponse:
        """
        Handles request and returns Response.
        """
        requested_path = scope.get("path", "/")
        for route_path, route_endpoint_func in self.routes.items():
            if route_path == requested_path:
                endpoint_kwargs = self._build_endpoint_func_args(
                    endpoint_func=route_endpoint_func,
                    parsed_args=parse_args_from_scope(scope=scope),
                    scope=scope,
                )
                if isinstance(endpoint_kwargs, BaseResponse):
                    return endpoint_kwargs
                try:
                    if iscoroutinefunction(route_endpoint_func):
                        response = await route_endpoint_func(**endpoint_kwargs)
                    else:
                        response = route_endpoint_func(**endpoint_kwargs)
                    response = await self._wrap_response_in_response_class(response)

                except BaseException as _route_handle_exception:
                    response = await self._process_with_error_handlers(
                        response=PlainResponse(
                            content="Internal Server Error!", status_code=500
                        )
                    )
                    await response.__call__(scope, receive, send)
                    raise _route_handle_exception
                if isinstance(response, BaseResponse):
                    return response
                return PlainResponse(content="Internal Server Error!", status_code=500)
        return PlainResponse(content="Not Found!", status_code=404)

    async def _on_lifespan_event(self) -> None:
        """
        Handles ASGI lifespan event.
        """
        pass

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        ASGI server request handler.
        """
        event_type = scope["type"]
        if event_type != "http":
            # Do not process non-http requests events as endpoint.

            if event_type == "lifespan":
                await self._on_lifespan_event()
            return

        self._alter_scope_on_call(scope)
        raw_response = await self._handle_request_to_endpoint(scope, receive, send)
        response = await self._process_with_error_handlers(response=raw_response)
        await response.__call__(scope, receive, send)
