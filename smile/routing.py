from typing import Dict
from smile.types import Scope


def parse_args_from_scope(scope: Scope) -> Dict[str, str]:
    query_args = scope.get("query_string", b"").decode("utf-8").split("&")
    parsed_args = dict()
    for query_arg in query_args:
        if not query_arg:
            continue
        query_args_name, query_arg_value = query_arg.split("=")
        parsed_args[query_args_name] = query_arg_value
    return parsed_args
