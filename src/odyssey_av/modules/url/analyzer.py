"""Análise estrutural local de URLs (RF-017 a RF-020, RN-006).

Nenhuma requisição HTTP e nenhuma consulta DNS são feitas. Os indicadores são
sinais de atenção, nunca confirmação de ameaça (RN-003). Credenciais são
detectadas, mas seu valor não entra no resultado (RN-005, RN-010).
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from odyssey_av.shared.errors.handlers import InvalidInputError

ALLOWED_SCHEMES = ("http", "https")
DEFAULT_PORTS: dict[str, int] = {"http": 80, "https": 443}

# Limites provisórios, sujeitos à revisão em D-03.
MAX_URL_LENGTH = 2048
MAX_HOST_LABELS = 4
MAX_HYPHENS_IN_HOST = 3

_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


@dataclass(frozen=True)
class Indicator:
    code: str
    message: str


@dataclass(frozen=True)
class UrlAnalysis:
    scheme: str
    host: str
    port: int | None
    path: str
    has_query: bool
    has_fragment: bool
    has_credentials: bool
    normalized: str
    indicators: tuple[Indicator, ...]

    def to_record(self) -> dict[str, Any]:
        """Componentes persistíveis: sem credenciais, sem valores de query e sem fragmento."""
        return {
            "scheme": self.scheme,
            "host": self.host,
            "port": self.port,
            "path": self.path,
            "has_query": self.has_query,
            "has_fragment": self.has_fragment,
            "has_credentials": self.has_credentials,
            "indicators": [indicator.code for indicator in self.indicators],
        }


def analyze_url(raw: str) -> UrlAnalysis:
    """Decompõe, normaliza e identifica indicadores de atenção. Não acessa o destino."""
    value = _validate_raw(raw)

    try:
        parts = urlsplit(value)
        port = parts.port
    except ValueError as exc:
        raise InvalidInputError(
            "URL malformada: não foi possível interpretar a estrutura informada."
        ) from exc

    scheme = parts.scheme.lower()
    if not scheme:
        raise InvalidInputError("Informe o esquema da URL, por exemplo https://.")

    host = (parts.hostname or "").rstrip(".")
    if not host:
        raise InvalidInputError(
            "URL sem host identificável: somente URLs com host são analisadas."
        )

    path = _normalize_path(parts.path)
    has_credentials = "@" in parts.netloc

    return UrlAnalysis(
        scheme=scheme,
        host=host,
        port=port,
        path=path,
        has_query=bool(parts.query),
        has_fragment=bool(parts.fragment),
        has_credentials=has_credentials,
        normalized=_build(scheme, host, port, path, parts.query, parts.fragment),
        indicators=_find_indicators(scheme, host, port, has_credentials),
    )


def _validate_raw(raw: str) -> str:
    value = raw.strip()
    if not value:
        raise InvalidInputError("Informe uma URL.")
    if len(value) > MAX_URL_LENGTH:
        raise InvalidInputError(
            f"URL muito longa: o limite é de {MAX_URL_LENGTH} caracteres."
        )
    if _CONTROL_CHARS.search(value):
        raise InvalidInputError("A URL contém caracteres de controle e foi rejeitada.")
    return value


def _normalize_path(path: str) -> str:
    """Remove barras repetidas e resolve segmentos '.' e '..' (RFC 3986, seção 5.2.4)."""
    if not path:
        return "/"

    trailing = path.split("/")[-1] in ("", ".", "..")
    segments: list[str] = []
    for segment in path.split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if segments:
                segments.pop()
            continue
        segments.append(segment)

    if not segments:
        return "/"
    result = "/" + "/".join(segments)
    return result + "/" if trailing else result


def _build(
    scheme: str,
    host: str,
    port: int | None,
    path: str,
    query: str,
    fragment: str,
) -> str:
    """Monta a URL normalizada. Credenciais são omitidas; query e fragmento são mantidos."""
    authority = f"[{host}]" if ":" in host else host
    if port is not None and port != DEFAULT_PORTS.get(scheme):
        authority += f":{port}"

    url = f"{scheme}://{authority}{path}"
    if query:
        url += f"?{query}"
    if fragment:
        url += f"#{fragment}"
    return url


def _find_indicators(
    scheme: str,
    host: str,
    port: int | None,
    has_credentials: bool,
) -> tuple[Indicator, ...]:
    found: list[Indicator] = []

    if scheme not in ALLOWED_SCHEMES:
        found.append(
            Indicator("SCHEME_NOT_HTTP", f"Esquema '{scheme}' diferente de http e https.")
        )
    if _is_ip_literal(host):
        found.append(
            Indicator("IP_HOST", "O host é um endereço IP, e não um nome de domínio.")
        )
    if port is not None and port != DEFAULT_PORTS.get(scheme):
        found.append(
            Indicator("NON_DEFAULT_PORT", f"Porta {port} diferente da padrão do esquema.")
        )
    if not host.isascii():
        found.append(
            Indicator(
                "NON_ASCII_HOST",
                "O domínio contém caracteres não ASCII, que podem imitar outros nomes.",
            )
        )

    labels = host.split(".")
    if any(label.startswith("xn--") for label in labels):
        found.append(
            Indicator(
                "PUNYCODE_HOST",
                "O domínio usa codificação internacional (xn--), que pode ocultar caracteres.",
            )
        )
    if len(labels) > MAX_HOST_LABELS:
        found.append(
            Indicator("MANY_SUBDOMAINS", f"O domínio possui {len(labels)} níveis.")
        )
    if host.count("-") > MAX_HYPHENS_IN_HOST:
        found.append(Indicator("MANY_HYPHENS", "O domínio possui muitos hífens."))
    if has_credentials:
        found.append(
            Indicator(
                "CREDENTIALS_IN_URL",
                "A URL contém informações de usuário antes do host. Os valores foram omitidos.",
            )
        )

    return tuple(found)


def _is_ip_literal(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return True