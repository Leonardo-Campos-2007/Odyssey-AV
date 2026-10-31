"""Testes do comando odyssey hash na CLI (TC-CLI-002, TC-CLI-013, TC-CLI-016)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from odyssey_av.application.services.recovery_service import Session, start_session
from odyssey_av.cli.app import app
from odyssey_av.domain.enums import OperationalState
from odyssey_av.shared.errors.handlers import InvalidInputError

runner = CliRunner()
SHA256_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


@pytest.fixture(autouse=True)
def _cwd_isolado(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def arquivo(tmp_path: Path) -> Path:
    caminho = tmp_path / "abc.txt"
    caminho.write_bytes(b"abc")
    return caminho


@pytest.fixture
def session(tmp_path: Path):
    sessao = start_session("instancia-teste", tmp_path / "h.db")
    yield sessao
    sessao.close()


def test_hash_calculate_texto_mostra_sha256_e_registro(session: Session, arquivo: Path) -> None:
    result = runner.invoke(app, ["hash", "calculate", str(arquivo)], obj=session)

    assert result.exit_code == 0
    assert f"SHA-256: {SHA256_ABC}" in result.output
    assert "Comparação: NO_REFERENCE" in result.output
    assert "Histórico: registrado" in result.output


def test_hash_calculate_json_retorna_campos_estruturados(session: Session, arquivo: Path) -> None:
    result = runner.invoke(app, ["--json", "hash", "calculate", str(arquivo)], obj=session)

    dados = json.loads(result.output)
    assert result.exit_code == 0
    assert dados["operation"]["status"] == "SUCCESS"
    assert dados["result"]["sha256"] == SHA256_ABC
    assert dados["history"]["status"] == "CONFIRMED"


def test_hash_em_degraded_retorna_codigo_3(arquivo: Path) -> None:
    sessao = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível nesta sessão.",
    )

    result = runner.invoke(app, ["hash", "calculate", str(arquivo)], obj=sessao)

    assert result.exit_code == 3
    assert "histórico indisponível" in result.output


def test_arquivo_ausente_retorna_codigo_1(session: Session, tmp_path: Path) -> None:
    result = runner.invoke(app, ["hash", "calculate", str(tmp_path / "nao_existe.bin")], obj=session)

    assert result.exit_code == 1
    assert "Motivo: Arquivo não encontrado." in result.output


def test_referencia_invalida_e_entrada_invalida(session: Session, arquivo: Path) -> None:
    result = runner.invoke(
        app, ["hash", "calculate", str(arquivo), "--reference", "xyz"], obj=session
    )

    assert isinstance(result.exception, InvalidInputError)