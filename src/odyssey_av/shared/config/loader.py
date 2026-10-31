"""Carregamento da configuração: padrões, TOML opcional e argumentos da CLI."""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from odyssey_av.shared.errors.handlers import ConfigurationError

CONFIG_ENV_VAR = "ODYSSEY_CONFIG"
DEFAULT_CONFIG_FILENAME = "odyssey.toml"

VALID_OUTPUT_FORMATS = ("text", "json")
VALID_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


@dataclass(frozen=True)
class AppConfig:
    """Configuração efetiva após aplicar a precedência."""

    output_format: str = "text"
    log_level: str = "INFO"


_ALLOWED_KEYS = frozenset(AppConfig.__dataclass_fields__)


def load_config(
    cli_overrides: Mapping[str, Any] | None = None,
    config_path: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> AppConfig:
    """Retorna a configuração efetiva.

    Valores ``None`` em ``cli_overrides`` são ignorados, porque indicam
    que o usuário não informou a opção.
    """
    environment = os.environ if env is None else env
    path, required = _resolve_path(config_path, environment)

    config = AppConfig()

    if path is not None:
        file_values = _read_toml(path, required)
        config = replace(config, **_validate(file_values, f"arquivo {path}"))

    explicit = {key: value for key, value in (cli_overrides or {}).items() if value is not None}
    config = replace(config, **_validate(explicit, "argumentos da CLI"))

    return config


def _resolve_path(config_path: Path | None, environment: Mapping[str, str]) -> tuple[Path, bool]:
    """Retorna o caminho a ser lido e se a sua existência é obrigatória."""
    if config_path is not None:
        return config_path, True

    from_env = environment.get(CONFIG_ENV_VAR)
    if from_env:
        return Path(from_env), True

    return Path.cwd() / DEFAULT_CONFIG_FILENAME, False


def _read_toml(path: Path, required: bool) -> dict[str, Any]:
    """Lê o TOML. Ausência é aceita, salvo quando o caminho foi exigido."""
    if not path.is_file():
        if required:
            raise ConfigurationError(f"Arquivo de configuração não encontrado: {path}")
        return {}

    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigurationError(f"Arquivo TOML inválido ({path}): {exc}") from exc
    except OSError as exc:
        raise ConfigurationError(f"Não foi possível ler o arquivo de configuração: {path}") from exc


def _validate(values: Mapping[str, Any], origin: str) -> dict[str, Any]:
    """Valida chaves e valores, retornando apenas os campos aceitos."""
    unknown = set(values) - _ALLOWED_KEYS
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ConfigurationError(f"Chave(s) desconhecida(s) em {origin}: {names}.")

    validated: dict[str, Any] = {}

    if "output_format" in values:
        value = values["output_format"]
        if value not in VALID_OUTPUT_FORMATS:
            allowed = ", ".join(VALID_OUTPUT_FORMATS)
            raise ConfigurationError(f"Valor inválido para output_format em {origin}. Use: {allowed}.")
        validated["output_format"] = value

    if "log_level" in values:
        value = values["log_level"]
        if value not in VALID_LOG_LEVELS:
            allowed = ", ".join(VALID_LOG_LEVELS)
            raise ConfigurationError(f"Valor inválido para log_level em {origin}. Use: {allowed}.")
        validated["log_level"] = value

    return validated