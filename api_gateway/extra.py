from abc import ABC, abstractmethod
from typing import Any, Literal


class Extra(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def dump(self) -> dict[str, Any]:
        raise NotImplementedError


class ExtraRouter(Extra):
    def __init__(self, disable_access_log: bool = False) -> None:
        self.disable_access_log = disable_access_log

    @property
    def name(self) -> str:
        return "router"

    def dump(self) -> dict[str, Any]:
        return {"disable_access_log": self.disable_access_log}


class ExtraHttp(Extra):
    def __init__(self, return_error_details: dict[str, Any] | None = None) -> None:
        if return_error_details is None:
            return_error_details = {
                "backend": {
                    "status_code": 502,
                    "message": "Internal server error from backend",
                }
            }
        self.return_error_details = return_error_details

    @property
    def name(self) -> str:
        return "http/client"

    def dump(self) -> dict[str, Any]:
        return {"return_error_details": self.return_error_details}


class ExtraSecurityCors(Extra):
    def __init__(
        self,
        allow_origins: list[str],
        allow_methods: list[Literal["GET", "HEAD", "POST", "PATCH", "OPTIONS"]],
        expose_headers: list[str],
        allow_headers: list[str],
        max_age: str = "12h",
        allow_credentials: bool = False,
        debug: bool = False,
    ) -> None:
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.expose_headers = expose_headers
        self.allow_headers = allow_headers
        self.max_age = max_age
        self.allow_credentials = allow_credentials
        self.debug = debug

    @property
    def name(self) -> str:
        return "security/cors"

    def dump(self) -> dict[str, Any]:
        return {
            "allow_origins": self.allow_origins,
            "allow_methods": self.allow_methods,
            "expose_headers": self.expose_headers,
            "allow_headers": self.allow_headers,
            "max_age": self.max_age,
            "allow_credentials": self.allow_credentials,
            "debug": self.debug,
        }


class ExtraTelemetryLogging(Extra):
    def __init__(
        self,
        level: Literal["DEBUG", "INFO", "WARNING", "ERROR"],
        prefix: str = "[KRAKEND]",
        stdout: bool = True,
        syslog: bool = False,
    ) -> None:
        self.level = level
        self.prefix = prefix
        self.stdout = stdout
        self.syslog = syslog

    @property
    def name(self) -> str:
        return "telemetry/logging"

    def dump(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "prefix": self.prefix,
            "stdout": self.stdout,
            "syslog": self.syslog,
        }


class ExtraRateLimitRouter(Extra):
    def __init__(
        self,
        max_rate: int = 50,
        every: str = "1s",
        client_max_rate: int = 5,
        strategy: str = "ip",
        capacity: int = 50,
        client_capacity: int = 5,
    ):
        self.max_rate = max_rate
        self.every = every
        self.client_max_rate = client_max_rate
        self.strategy = strategy
        self.capacity = capacity
        self.client_capacity = client_capacity

    @property
    def name(self) -> str:
        return "qos/ratelimit/router"

    def dump(self) -> dict[str, Any]:
        return {
            "max_rate": self.max_rate,
            "every": self.every,
            "client_max_rate": self.client_max_rate,
            "strategy": self.strategy,
            "capacity": self.capacity,
            "client_capacity": self.client_capacity,
        }


class ExtraAuthorizeValidator(Extra):
    def __init__(
        self,
        jwk_url: str,
        propagate_claims: list[tuple[str, str]],
        cache: bool = True,
        operation_debug: bool = True,
        disable_jwk_security: bool = True,
        alg: str = "RS256",
    ):
        self.jwk_url = jwk_url
        self.propagate_claims = propagate_claims
        self.cache = cache
        self.operation_debug = operation_debug
        self.disable_jwk_security = disable_jwk_security
        self.alg = alg

    @property
    def name(self) -> str:
        return "auth/validator"

    def dump(self) -> dict[str, Any]:
        return {
            "jwk_url": self.jwk_url,
            "propagate_claims": self.propagate_claims,
            "cache": self.cache,
            "operation_debug": self.operation_debug,
            "disable_jwk_security": self.disable_jwk_security,
            "alg": self.alg,
        }
