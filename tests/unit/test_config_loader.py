"""Testes da configuração: padrões, TOML opcional e precedência (TU-CONFIG-001 a 007)."""

from __future__ import annotations

from pathlib import Path

import pytest

from odyssey_av.shared.config.loader import AppConfig, load_config
from odyssey_av.shared.errors.handlers import ConfigurationError


@pytest.fixture
def isolated_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Muda o diretório atual para uma pasta vazia, sem odyssey.toml."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_tu_config_001_sem_arquivo_usa_padroes(isolated_cwd: Path) -> None:
    config = load_config(env={})

    assert config == AppConfig()


def test_tu_config_002_carrega_toml_valido(config_file: Path) -> None:
    config_file.write_text('output_format = "json"\nlog_level = "DEBUG"\n', encoding="utf-8")

    config = load_config(config_path=config_file, env={})

    assert config.output_format == "json"
    assert config.log_level == "DEBUG"


def test_tu_config_003_toml_invalido_gera_erro_claro(config_file: Path) -> None:
    config_file.write_text('output_format = "json\n', encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Arquivo TOML inválido"):
        load_config(config_path=config_file, env={})


def test_tu_config_004_toml_prevalece_sobre_padrao(config_file: Path) -> None:
    config_file.write_text('output_format = "json"\n', encoding="utf-8")
    assert AppConfig().output_format == "text"

    config = load_config(config_path=config_file, env={})

    assert config.output_format == "json"


def test_tu_config_005_argumento_cli_prevalece_sobre_toml(config_file: Path) -> None:
    config_file.write_text('log_level = "DEBUG"\n', encoding="utf-8")

    config = load_config({"log_level": "ERROR"}, config_path=config_file, env={})

    assert config.log_level == "ERROR"


def test_tu_config_006_argumento_none_nao_sobrescreve_toml(config_file: Path) -> None:
    config_file.write_text('log_level = "DEBUG"\n', encoding="utf-8")

    config = load_config({"log_level": None}, config_path=config_file, env={})

    assert config.log_level == "DEBUG"


@pytest.mark.parametrize("valor", [123, True, ["json"]])
def test_tu_config_007_tipo_incompativel_e_rejeitado(config_file: Path, valor: object) -> None:
    config_file.write_text(f"output_format = {_toml_literal(valor)}\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="output_format"):
        load_config(config_path=config_file, env={})


def test_caminho_explicito_inexistente_gera_erro(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="não encontrado"):
        load_config(config_path=tmp_path / "nao_existe.toml", env={})


def test_chave_desconhecida_no_toml_e_rejeitada(config_file: Path) -> None:
    config_file.write_text('formato = "json"\n', encoding="utf-8")

    with pytest.raises(ConfigurationError, match="desconhecida"):
        load_config(config_path=config_file, env={})


def _toml_literal(valor: object) -> str:
    """Converte um valor Python para a sintaxe TOML equivalente."""
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, str):
        return f'"{valor}"'
    if isinstance(valor, list):
        return "[" + ", ".join(f'"{item}"' for item in valor) + "]"
    return str(valor)