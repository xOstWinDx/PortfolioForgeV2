from typing import Literal, Any

from api_gateway.extra import Extra


class Backend:
    def __init__(
        self, url_pattern: str, host: list[str], disable_host_sanitize: bool = True
    ) -> None:
        self.url_pattern = url_pattern
        self.host = host
        self.disable_host_sanitize = disable_host_sanitize

    def dump(self) -> dict[str, Any]:
        return {
            "url_pattern": self.url_pattern,
            "host": self.host,
            "disable_host_sanitize": self.disable_host_sanitize,
        }


class Endpoint:
    def __init__(
        self,
        endpoint: str,
        method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
        output_encoding: Literal["json", "no-op"],
        input_headers: list[str],
        input_query_strings: list[str],
        extra_config: list[Extra],
        backend: list[Backend],
    ) -> None:
        self.endpoint = endpoint
        self.method = method
        self.output_encoding = output_encoding
        self.input_headers = input_headers
        self.extra_config = extra_config
        self.backend = backend
        self.input_query_strings = input_query_strings

    def dump(self) -> dict[str, Any]:
        return {
            "endpoint": self.endpoint,
            "method": self.method,
            "output_encoding": self.output_encoding,
            "input_headers": self.input_headers,
            "extra_config": {extra.name: extra.dump() for extra in self.extra_config},
            "backend": [back.dump() for back in self.backend],
            "input_query_strings": self.input_query_strings,
        }

