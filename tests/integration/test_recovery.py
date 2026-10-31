"""Testes da recuperação de execuções e do estado operacional (TI-014, TI-022, TI-025, TR-007, TR-008)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from odyssey_av.application.services.recovery_service import (
    recover_interrupted_runs,
    start_session,
)
from odyssey_av.domain.entities import AnalysisRun
from odyssey_av.domain.enums import ExecutionStatus, Module, OperationalState
from odyssey_av.infrastructure.persistence.database import open_database
from odyssey_av.infrastructure.persistence.repositories.analysis_run_repository import (
    AnalysisRunRepository,
)

AGORA = datetime(2026, 10, 31, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "history.db"


def _run(instance_id: str, status: ExecutionStatus = ExecutionStatus.RUNNING) -> AnalysisRun:
    return AnalysisRun(
        instance_id=instance_id,
        module=Module.HASH,
        command="hash calculate",
        started_at=AGORA,
        status=status,
    )


def _semear(db_path: Path, *runs: AnalysisRun) -> list[str]:
    conn = open_database(db_path)
    try:
        repo = AnalysisRunRepository(conn)
        for run in runs:
            repo.add(run)
    finally:
        conn.close()
    return [run.id for run in runs]


def _status(db_path: Path, run_id: str) -> ExecutionStatus:
    conn = open_database(db_path)
    try:
        return AnalysisRunRepository(conn).get(run_id).status
    finally:
        conn.close()


def _instalar_falha(db_path: Path) -> None:
    """Trigger que faz o UPDATE da recuperação falhar ao atingir a instância 'antiga-b'."""
    conn = open_database(db_path)
    try:
        conn.execute(
            "CREATE TRIGGER falha_recuperacao BEFORE UPDATE ON analysis_runs "
            "WHEN NEW.instance_id = 'antiga-b' "
            "BEGIN SELECT RAISE(ABORT, 'falha simulada'); END"
        )
    finally:
        conn.close()


def _remover_falha(db_path: Path) -> None:
    conn = open_database(db_path)
    try:
        conn.execute("DROP TRIGGER falha_recuperacao")
    finally:
        conn.close()


def test_execucoes_de_instancia_anterior_sao_interrompidas(db_path: Path) -> None:
    """Somente RUNNING de outra instância muda. Estados finalizados permanecem."""
    interrompida, concluida = _semear(
        db_path,
        _run("antiga"),
        _run("antiga", ExecutionStatus.SUCCESS),
    )

    session = start_session("nova", db_path)
    try:
        assert session.state is OperationalState.NORMAL
        assert session.history_available
        assert session.recovered_count == 1

        repo = AnalysisRunRepository(session.connection)
        marcada = repo.get(interrompida)
        assert marcada.status is ExecutionStatus.INTERRUPTED
        assert marcada.finished_at is not None
        assert repo.get(concluida).status is ExecutionStatus.SUCCESS
    finally:
        session.close()


def test_execucao_da_propria_instancia_nao_e_alterada(db_path: Path) -> None:
    (propria,) = _semear(db_path, _run("atual"))

    conn = open_database(db_path)
    try:
        assert recover_interrupted_runs(conn, "atual") == 0
        assert AnalysisRunRepository(conn).get(propria).status is ExecutionStatus.RUNNING
    finally:
        conn.close()


def test_falha_na_recuperacao_entra_em_degraded_sem_alteracao_parcial(db_path: Path) -> None:
    a, b = _semear(db_path, _run("antiga-a"), _run("antiga-b"))
    _instalar_falha(db_path)

    session = start_session("nova", db_path)

    assert session.state is OperationalState.DEGRADED
    assert not session.history_available
    assert session.connection is None
    assert session.message
    # O UPDATE falhou como um todo: nenhum dos dois registros foi alterado.
    assert _status(db_path, a) is ExecutionStatus.RUNNING
    assert _status(db_path, b) is ExecutionStatus.RUNNING


def test_proxima_inicializacao_recupera_registros_pendentes(db_path: Path) -> None:
    a, b = _semear(db_path, _run("antiga-a"), _run("antiga-b"))
    _instalar_falha(db_path)
    start_session("nova", db_path).close()
    _remover_falha(db_path)

    session = start_session("nova-2", db_path)
    try:
        assert session.state is OperationalState.NORMAL
        assert session.recovered_count == 2
        assert _status(db_path, a) is ExecutionStatus.INTERRUPTED
        assert _status(db_path, b) is ExecutionStatus.INTERRUPTED
    finally:
        session.close()


def test_banco_indisponivel_entra_em_degraded(tmp_path: Path) -> None:
    """Caminho impossível de criar: o diretório pai é um arquivo comum."""
    bloqueio = tmp_path / "arquivo"
    bloqueio.write_text("não é um diretório", encoding="utf-8")

    session = start_session("nova", bloqueio / "history.db")

    assert session.state is OperationalState.DEGRADED
    assert session.connection is None
    assert not session.history_available