"""Testes dos repositórios e da consistência entre enums e o esquema (TB-001, TB-002, TB-003, TB-007)."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from odyssey_av.domain.entities import AnalysisResult, AnalysisRun
from odyssey_av.domain.enums import ExecutionStatus, Module, ResultStatus
from odyssey_av.infrastructure.persistence.database import open_database
from odyssey_av.infrastructure.persistence.repositories.analysis_result_repository import (
    AnalysisResultRepository,
)
from odyssey_av.infrastructure.persistence.repositories.analysis_run_repository import (
    AnalysisRunRepository,
)
from odyssey_av.shared.errors.handlers import PersistenceError

AGORA = datetime(2026, 10, 31, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def conn(tmp_path: Path):
    connection = open_database(tmp_path / "history.db")
    yield connection
    connection.close()


def _nova_execucao(**kwargs) -> AnalysisRun:
    base = {
        "instance_id": "instancia-1",
        "module": Module.HASH,
        "command": "hash calculate",
        "started_at": AGORA,
    }
    base.update(kwargs)
    return AnalysisRun(**base)


def test_tb_001_execucao_persistida_e_recuperada(conn: sqlite3.Connection) -> None:
    repo = AnalysisRunRepository(conn)
    run = _nova_execucao()

    repo.add(run)
    recuperada = repo.get(run.id)

    assert recuperada is not None
    assert recuperada.id == run.id
    assert recuperada.module is Module.HASH
    assert recuperada.status is ExecutionStatus.RUNNING
    assert recuperada.started_at == AGORA


def test_tb_002_resultado_associado_a_execucao(conn: sqlite3.Connection) -> None:
    run = _nova_execucao()
    AnalysisRunRepository(conn).add(run)
    results = AnalysisResultRepository(conn)

    results.add(
        AnalysisResult(
            analysis_run_id=run.id,
            result_type="hash",
            status=ResultStatus.SUCCESS,
            created_at=AGORA,
            data={"sha256": "ab" * 32},
        )
    )

    encontrados = results.list_by_run(run.id)
    assert len(encontrados) == 1
    assert encontrados[0].data == {"sha256": "ab" * 32}
    assert encontrados[0].analysis_run_id == run.id


def test_tb_003_resultado_sem_execucao_e_recusado(conn: sqlite3.Connection) -> None:
    results = AnalysisResultRepository(conn)

    with pytest.raises(PersistenceError):
        results.add(
            AnalysisResult(
                analysis_run_id="inexistente",
                result_type="hash",
                status=ResultStatus.SUCCESS,
                created_at=AGORA,
            )
        )


def test_atualizacao_registra_estado_final(conn: sqlite3.Connection) -> None:
    repo = AnalysisRunRepository(conn)
    run = _nova_execucao()
    repo.add(run)
    fim = AGORA + timedelta(milliseconds=250)

    repo.update_status(run.id, ExecutionStatus.SUCCESS, fim, 250, "Concluído.")

    atualizada = repo.get(run.id)
    assert atualizada.status is ExecutionStatus.SUCCESS
    assert atualizada.finished_at == fim
    assert atualizada.duration_ms == 250


def test_atualizacao_de_execucao_inexistente_falha(conn: sqlite3.Connection) -> None:
    with pytest.raises(PersistenceError):
        AnalysisRunRepository(conn).update_status(
            "inexistente", ExecutionStatus.FAILED, AGORA, None
        )


def test_apagar_execucao_remove_resultados_em_cascata(conn: sqlite3.Connection) -> None:
    run = _nova_execucao()
    AnalysisRunRepository(conn).add(run)
    results = AnalysisResultRepository(conn)
    results.add(
        AnalysisResult(
            analysis_run_id=run.id,
            result_type="hash",
            status=ResultStatus.INFO,
            created_at=AGORA,
        )
    )

    with conn:
        conn.execute("DELETE FROM analysis_runs WHERE id = ?", (run.id,))

    assert results.list_by_run(run.id) == []


@pytest.mark.parametrize("status", list(ExecutionStatus))
def test_todos_os_estados_de_execucao_sao_aceitos(conn: sqlite3.Connection, status: ExecutionStatus) -> None:
    run = _nova_execucao(status=status)

    AnalysisRunRepository(conn).add(run)

    assert AnalysisRunRepository(conn).get(run.id).status is status


def test_enums_do_dominio_coincidem_com_o_esquema(conn: sqlite3.Connection) -> None:
    """Garante que os valores do código e os CHECK da migration não divergem."""
    sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE name = 'analysis_runs'"
    ).fetchone()[0]

    for enum in (Module, ExecutionStatus):
        for member in enum:
            assert f"'{member.value}'" in sql

    result_sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE name = 'analysis_results'"
    ).fetchone()[0]
    for member in ResultStatus:
        assert f"'{member.value}'" in result_sql