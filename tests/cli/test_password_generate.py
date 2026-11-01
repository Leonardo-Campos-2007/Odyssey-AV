"""Testes do comando odyssey password generate (TC-CLI-004)."""

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


@pytest.fixture(autouse=True)
def _cwd_isolado(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def session(tmp_path: Path):
    sessao = start_session("instancia-teste", tmp_path / "h.db")
    yield sessao
    sessao.close()


def _senha(saida: str) -> str:
    for linha in saida.splitlines():
        if linha.startswith("Senha: "):
            return linha[len("Senha: "):]
    raise AssertionError("Linha de senha não encontrada na saída.")


def test_generate_texto_mostra_senha_com_comprimento_padrao(session: Session) -> None:
    result = runner.invoke(app, ["password", "generate"], obj=session)

    assert result.exit_code == 0
    assert len(_senha(result.output)) == 16
    assert "Histórico: registrado" in result.output


def test_generate_json_retorna_senha_e_aviso_no_stderr(session: Session) -> None:
    result = runner.invoke(app, ["--json", "password", "generate", "--length", "24"], obj=session)

    dados = json.loads(result.stdout)
    assert result.exit_code == 0
    assert len(dados["result"]["password"]) == 24
    assert dados["history"]["status"] == "CONFIRMED"
    assert "não é armazenada" in result.output


def test_no_symbols_remove_simbolos_da_saida(session: Session) -> None:
    result = runner.invoke(app, ["password", "generate", "--length", "64", "--no-symbols"], obj=session)

    senha = _senha(result.output)
    assert not any(not c.isalnum() for c in senha)


def test_comprimento_invalido_e_erro_de_uso(session: Session) -> None:
    result = runner.invoke(app, ["password", "generate", "--length", "3"], obj=session)

    assert isinstance(result.exception, InvalidInputError)


def test_generate_em_degraded_retorna_codigo_3() -> None:
    sessao = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível.",
    )

    result = runner.invoke(app, ["password", "generate"], obj=sessao)

    assert result.exit_code == 3
    assert len(_senha(result.output)) == 16