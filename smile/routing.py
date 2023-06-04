from typing import Dict, Callable

from smile.types import Scope


class Router:
    """
    Router class for route registration without app (includes at top layer).
    """

    def __init__(self):
        self.routes = dict()  # TODO: Rework routes system.

    def add_route(
        self, path: str, endpoint_func: Callable, methods: list[str] | None = None
    ) -> None:
        # TODO: Rework routes system.
        if methods is None:
            methods = ["GET"]
        self.routes[path] = endpoint_func, methods

    def route(self, path: str, methods: list[str] | None = None) -> Callable:
        """
        Route decorator for endpoing function.

        Use example:
        @app.route("/path")
        def route():
            return BaseResponse("Hello world!")
        """

        def wrapper(route_func: Callable) -> Callable:
            self.add_route(path=path, endpoint_func=route_func, methods=methods)
            return route_func

        return wrapper


def parse_args_from_scope(scope: Scope) -> Dict[str, str]:
    query_args = scope.get("query_string", b"").decode("utf-8").split("&")
    parsed_args = dict()
    for query_arg in query_args:
        if not query_arg:
            continue
        query_args_name, query_arg_value = query_arg.split("=")
        parsed_args[query_args_name] = query_arg_value
    return parsed_args
