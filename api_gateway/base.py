from typing import Any

from api_gateway.endpoint import Endpoint
from api_gateway.extra import Extra


class KrakenConfig:
    def __init__(
        self,
        extra_config: list[Extra],
        endpoints: list[Endpoint],
        timeout: str = "10s",
        port: int = 8080,
        name: str = "API Gateway",
        version: int = 3,
    ):
        self.version = version
        self.name = name
        self.port = port
        self.timeout = timeout
        self.extra_config = extra_config
        self.endpoints = endpoints

    def dump(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "name": self.name,
            "port": self.port,
            "timeout": self.timeout,
            "extra_config": {extra.name: extra.dump() for extra in self.extra_config},
            "endpoints": [endpoint.dump() for endpoint in self.endpoints],
        }
