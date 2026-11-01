"""Testes do comando odyssey password evaluate (TC-CLI-005, TU-PASS-008)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from odyssey_av.application.services.recovery_service import Session, start_session
from odyssey_av.cli.app import app
from odyssey_av.cli.commands import password as password_cmd
from odyssey_av.domain.enums import OperationalState
from odyssey_av.shared.errors.handlers import InvalidInputError

runner = CliRunner()
SENHA_FORTE = "Tr0ub4dor&3"
SENHA_FRACA = "Senha123"


@pytest.fixture(autouse=True)
def _cwd_isolado(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)


@pytest.fixture(autouse=True)
def _terminal_simulado(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simula um terminal interativo. A leitura real é substituída por teste."""
    monkeypatch.setattr(password_cmd, "_stdin_is_interactive", lambda: True)


@pytest.fixture
def session(tmp_path: Path):
    sessao = start_session("instancia-teste", tmp_path / "h.db")
    yield sessao
    sessao.close()


def _contagem(session: Session) -> int:
    return session.connection.execute("SELECT COUNT(*) FROM analysis_runs").fetchone()[0]


def test_evaluate_texto_mostra_forca_sem_revelar_senha(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(password_cmd, "_read_password", lambda: SENHA_FORTE)

    result = runner.invoke(app, ["password", "evaluate"], obj=session)

    assert result.exit_code == 0
    assert "Força: forte" in result.output
    assert "Histórico: registrado" in result.output
    assert SENHA_FORTE not in result.output


def test_evaluate_json_retorna_indicadores_sem_senha(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(password_cmd, "_read_password", lambda: SENHA_FRACA)

    result = runner.invoke(app, ["--json", "password", "evaluate"], obj=session)

    dados = json.loads(result.stdout)
    assert result.exit_code == 0
    assert dados["result"]["strength"] == "FRACA"
    assert dados["history"]["status"] == "CONFIRMED"
    assert SENHA_FRACA not in result.stdout


def test_sem_terminal_recusa_e_nao_le_a_senha(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(password_cmd, "_stdin_is_interactive", lambda: False)

    def nao_deve_ler() -> str:
        raise AssertionError("A senha não deveria ser lida sem terminal interativo.")

    monkeypatch.setattr(password_cmd, "_read_password", nao_deve_ler)

    result = runner.invoke(app, ["password", "evaluate"], obj=session)

    assert result.exit_code == 2
    assert _contagem(session) == 0


def test_senha_vazia_e_erro_de_entrada_sem_registro(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(password_cmd, "_read_password", lambda: "")

    result = runner.invoke(app, ["password", "evaluate"], obj=session)

    assert isinstance(result.exception, InvalidInputError)
    assert _contagem(session) == 0


def test_evaluate_em_degraded_retorna_codigo_3(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(password_cmd, "_read_password", lambda: SENHA_FRACA)
    sessao = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível.",
    )

    result = runner.invoke(app, ["password", "evaluate"], obj=sessao)

    assert result.exit_code == 3
    assert "Força: fraca" in result.output