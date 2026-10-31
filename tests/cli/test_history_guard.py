"""Testes da guarda de HISTORY em DEGRADED (TI-021, TU-HIST-016, TC-CLI-016)."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from odyssey_av.application.services.recovery_service import Session, start_session
from odyssey_av.cli.app import app
from odyssey_av.domain.enums import OperationalState

runner = CliRunner()


@pytest.fixture(autouse=True)
def _cwd_isolado(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)


def test_history_recusado_em_degraded(tmp_path: Path) -> None:
    sessao = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível.",
    )

    result = runner.invoke(app, ["history", "list"], obj=sessao)

    assert result.exit_code == 1
    assert "HISTORY são recusadas" in result.output


def test_history_nao_cria_execucao_em_degraded(tmp_path: Path) -> None:
    sessao = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível.",
    )

    runner.invoke(app, ["history", "list"], obj=sessao)

    assert sessao.connection is None


def test_history_normal_nao_cria_analysis_run(tmp_path: Path) -> None:
    sessao = start_session("instancia-teste", tmp_path / "h.db")
    try:
        runner.invoke(app, ["history", "list"], obj=sessao)

        total = sessao.connection.execute("SELECT COUNT(*) FROM analysis_runs").fetchone()[0]
        assert total == 0
    finally:
        sessao.close()


def test_history_sem_sessao_e_recusado() -> None:
    result = runner.invoke(app, ["history", "list"])

    assert result.exit_code == 1