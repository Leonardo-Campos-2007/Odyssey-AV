"""Testes do comando status e da integração da CLI com a sessão."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from odyssey_av.application.services.recovery_service import Session, start_session
from odyssey_av.cli.app import app
from odyssey_av.domain.enums import OperationalState

runner = CliRunner()


@pytest.fixture(autouse=True)
def _cwd_isolado(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Evita ler um odyssey.toml do diretório real durante os testes."""
    monkeypatch.chdir(tmp_path)


def test_status_em_normal_mostra_estado_e_historico_disponivel(tmp_path: Path) -> None:
    session = start_session("instancia-teste", tmp_path / "h.db")
    try:
        result = runner.invoke(app, ["status"], obj=session)
    finally:
        session.close()

    assert result.exit_code == 0
    assert "Estado: NORMAL" in result.output
    assert "Instância: instancia-teste" in result.output
    assert "Execuções recuperadas: 0" in result.output
    assert "Histórico: disponível" in result.output


def test_status_em_degraded_informa_historico_indisponivel_e_aviso() -> None:
    session = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível nesta sessão.",
    )

    result = runner.invoke(app, ["status"], obj=session)

    assert result.exit_code == 0
    assert "Estado: DEGRADED" in result.output
    assert "Histórico: indisponível" in result.output
    assert "Aviso: Histórico indisponível nesta sessão." in result.output


def test_status_em_json_retorna_campos_estruturados(tmp_path: Path) -> None:
    session = start_session("instancia-teste", tmp_path / "h.db")
    try:
        result = runner.invoke(app, ["--json", "status"], obj=session)
    finally:
        session.close()

    dados = json.loads(result.output)
    assert dados["state"] == "NORMAL"
    assert dados["instance_id"] == "instancia-teste"
    assert dados["history_available"] is True


def test_status_sem_sessao_informa_nao_iniciada() -> None:
    result = runner.invoke(app, ["status"])

    assert result.exit_code == 0
    assert "Estado: NAO_INICIADA" in result.output