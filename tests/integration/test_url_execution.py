"""Testes da análise de URL no fluxo de execução e no histórico (TI-019, TR-006)."""

from __future__ import annotations

from pathlib import Path

import pytest

from odyssey_av.application.services.execution_service import PersistenceState, exit_code_for
from odyssey_av.application.services.recovery_service import Session, start_session
from odyssey_av.application.use_cases.analyze_url import run_url_analysis
from odyssey_av.domain.enums import ExecutionStatus, Module, OperationalState, ResultStatus
from odyssey_av.infrastructure.persistence.repositories.analysis_result_repository import (
    AnalysisResultRepository,
)
from odyssey_av.shared.errors.handlers import ExitCode, InvalidInputError

URL_COM_SEGREDOS = "https://usuario:SenhaSecreta123@exemplo.com/?token=abc123"
SEGREDOS = ("SenhaSecreta123", "abc123", "usuario")


@pytest.fixture
def session(tmp_path: Path):
    sessao = start_session("instancia-teste", tmp_path / "h.db")
    yield sessao
    sessao.close()


def _todo_o_historico(session: Session) -> str:
    partes: list[str] = []
    for tabela in ("analysis_runs", "analysis_results"):
        for row in session.connection.execute(f"SELECT * FROM {tabela}").fetchall():
            partes.extend(str(valor) for valor in tuple(row))
    return "\n".join(partes)


def test_registra_execucao_como_url(session: Session) -> None:
    analise = run_url_analysis(session, "https://exemplo.com/")

    assert analise.outcome.functional_status is ExecutionStatus.SUCCESS
    linha = session.connection.execute(
        "SELECT module, command FROM analysis_runs WHERE id = ?", (analise.outcome.run_id,)
    ).fetchone()
    assert tuple(linha) == (Module.URL.value, "url analyze")
    assert exit_code_for(analise.outcome) is ExitCode.SUCCESS


def test_credenciais_e_query_nao_sao_persistidas(session: Session) -> None:
    analise = run_url_analysis(session, URL_COM_SEGREDOS)

    assert analise.outcome.persistence is PersistenceState.CONFIRMED
    historico = _todo_o_historico(session)
    for segredo in SEGREDOS:
        assert segredo not in historico


def test_url_com_indicador_gera_resultado_de_aviso(session: Session) -> None:
    analise = run_url_analysis(session, "http://192.168.0.1/")

    resultados = AnalysisResultRepository(session.connection).list_by_run(analise.outcome.run_id)
    assert resultados[0].status is ResultStatus.WARNING


def test_url_sem_indicador_gera_resultado_informativo(session: Session) -> None:
    analise = run_url_analysis(session, "https://exemplo.com/")

    resultados = AnalysisResultRepository(session.connection).list_by_run(analise.outcome.run_id)
    assert resultados[0].status is ResultStatus.INFO


def test_entrada_invalida_nao_gera_registro(session: Session) -> None:
    with pytest.raises(InvalidInputError):
        run_url_analysis(session, "exemplo.com")

    total = session.connection.execute("SELECT COUNT(*) FROM analysis_runs").fetchone()[0]
    assert total == 0


def test_degraded_analisa_sem_gravar() -> None:
    sessao = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível.",
    )

    analise = run_url_analysis(sessao, "https://exemplo.com/")

    assert analise.outcome.persistence is PersistenceState.UNAVAILABLE
    assert analise.outcome.run_id is None
    assert exit_code_for(analise.outcome) is ExitCode.HISTORY_NOT_PERSISTED