"""Fixtures compartilhadas pelos testes do Odyssey AV."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path

import pytest

from odyssey_av.shared.logging.logger import LOGGER_NAME


@pytest.fixture
def lock_path(tmp_path: Path) -> Path:
    """Caminho de lock isolado, para não usar o lock real do usuário."""
    return tmp_path / "locks" / "instance.lock"


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    """Caminho de um arquivo TOML de teste. O arquivo não é criado automaticamente."""
    return tmp_path / "odyssey.toml"


@pytest.fixture(autouse=True)
def _isolate_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove variáveis de ambiente que alterariam a configuração dos testes."""
    monkeypatch.delenv("ODYSSEY_CONFIG", raising=False)


@pytest.fixture(autouse=True)
def _reset_logger() -> Iterator[None]:
    """Remove os handlers do logger principal após cada teste."""
    yield
    logger = logging.getLogger(LOGGER_NAME)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    logger.setLevel(logging.NOTSET)
    logger.propagate = True