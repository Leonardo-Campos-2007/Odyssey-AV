"""Testes da avaliação de senha no fluxo de execução e no histórico (TU-PASS-007, TI-009, TI-018)."""

from __future__ import annotations

from pathlib import Path

import pytest

from odyssey_av.application.services.execution_service import PersistenceState, exit_code_for
from odyssey_av.application.services.recovery_service import Session, start_session
from odyssey_av.application.use_cases.evaluate_password import evaluate_password
from odyssey_av.domain.enums import ExecutionStatus, Module, OperationalState, ResultStatus
from odyssey_av.infrastructure.persistence.repositories.analysis_result_repository import (
    AnalysisResultRepository,
)
from odyssey_av.shared.errors.handlers import ExitCode, InvalidInputError

SENHA_FORTE = "Tr0ub4dor&3"
SENHA_FRACA = "Senha123"


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


def test_senha_nao_aparece_no_historico(session: Session) -> None:
    avaliacao = evaluate_password(session, SENHA_FORTE)

    assert avaliacao.outcome.persistence is PersistenceState.CONFIRMED
    assert SENHA_FORTE not in _todo_o_historico(session)


def test_resultado_registra_apenas_indicadores(session: Session) -> None:
    avaliacao = evaluate_password(session, SENHA_FORTE)

    resultados = AnalysisResultRepository(session.connection).list_by_run(avaliacao.outcome.run_id)
    assert set(resultados[0].data) == {"length", "sets", "has_repetition", "score", "strength"}
    assert resultados[0].data["strength"] == "FORTE"


def test_execucao_e_registrada_como_password(session: Session) -> None:
    avaliacao = evaluate_password(session, SENHA_FORTE)

    assert avaliacao.outcome.functional_status is ExecutionStatus.SUCCESS
    linha = session.connection.execute(
        "SELECT module, command FROM analysis_runs WHERE id = ?", (avaliacao.outcome.run_id,)
    ).fetchone()
    assert tuple(linha) == (Module.PASSWORD.value, "password evaluate")
    assert exit_code_for(avaliacao.outcome) is ExitCode.SUCCESS


def test_senha_fraca_gera_resultado_de_aviso(session: Session) -> None:
    avaliacao = evaluate_password(session, SENHA_FRACA)

    resultados = AnalysisResultRepository(session.connection).list_by_run(avaliacao.outcome.run_id)
    assert resultados[0].status is ResultStatus.WARNING


def test_senha_forte_gera_resultado_informativo(session: Session) -> None:
    avaliacao = evaluate_password(session, SENHA_FORTE)

    resultados = AnalysisResultRepository(session.connection).list_by_run(avaliacao.outcome.run_id)
    assert resultados[0].status is ResultStatus.INFO


def test_senha_vazia_nao_gera_registro(session: Session) -> None:
    with pytest.raises(InvalidInputError):
        evaluate_password(session, "")

    total = session.connection.execute("SELECT COUNT(*) FROM analysis_runs").fetchone()[0]
    assert total == 0


def test_degraded_avalia_sem_gravar() -> None:
    sessao = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível.",
    )

    avaliacao = evaluate_password(sessao, SENHA_FORTE)

    assert avaliacao.outcome.persistence is PersistenceState.UNAVAILABLE
    assert avaliacao.outcome.run_id is None
    assert exit_code_for(avaliacao.outcome) is ExitCode.HISTORY_NOT_PERSISTED