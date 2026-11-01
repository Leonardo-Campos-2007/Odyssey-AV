"""Testes da geração de senha no fluxo de execução e no histórico (TU-PASS-006, TI-009, TI-018)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from odyssey_av.application.services.execution_service import PersistenceState, exit_code_for
from odyssey_av.application.services.recovery_service import Session, start_session
from odyssey_av.application.use_cases.generate_password import generate_password
from odyssey_av.domain.enums import ExecutionStatus, OperationalState
from odyssey_av.infrastructure.persistence.repositories.analysis_result_repository import (
    AnalysisResultRepository,
)
from odyssey_av.modules.password.generator import GenerationOptions
from odyssey_av.shared.errors.handlers import ExitCode, InvalidInputError


@pytest.fixture
def session(tmp_path: Path):
    sessao = start_session("instancia-teste", tmp_path / "h.db")
    yield sessao
    sessao.close()


def _todo_o_historico(session: Session) -> str:
    """Concatena todo o conteúdo persistido, para verificar que a senha não aparece."""
    partes: list[str] = []
    for tabela in ("analysis_runs", "analysis_results"):
        for row in session.connection.execute(f"SELECT * FROM {tabela}").fetchall():
            partes.extend(str(valor) for valor in tuple(row))
    return "\n".join(partes)


def test_senha_nao_aparece_no_historico(session: Session) -> None:
    geracao = generate_password(session, GenerationOptions())

    assert geracao.password is not None
    assert geracao.outcome.persistence is PersistenceState.CONFIRMED
    assert geracao.password not in _todo_o_historico(session)


def test_resultado_registra_apenas_metadados(session: Session) -> None:
    geracao = generate_password(session, GenerationOptions(length=20, symbols=False))

    resultados = AnalysisResultRepository(session.connection).list_by_run(geracao.outcome.run_id)
    assert len(resultados) == 1
    assert resultados[0].data == {"length": 20, "sets": ["lower", "upper", "digits"]}
    assert geracao.password not in json.dumps(resultados[0].data)


def test_execucao_e_registrada_como_password(session: Session) -> None:
    geracao = generate_password(session, GenerationOptions())

    assert geracao.outcome.functional_status is ExecutionStatus.SUCCESS
    linha = session.connection.execute(
        "SELECT module, command FROM analysis_runs WHERE id = ?", (geracao.outcome.run_id,)
    ).fetchone()
    assert tuple(linha) == ("PASSWORD", "password generate")
    assert exit_code_for(geracao.outcome) is ExitCode.SUCCESS


def test_comprimento_invalido_nao_gera_registro(session: Session) -> None:
    with pytest.raises(InvalidInputError):
        generate_password(session, GenerationOptions(length=3))

    total = session.connection.execute("SELECT COUNT(*) FROM analysis_runs").fetchone()[0]
    assert total == 0


def test_degraded_gera_senha_sem_gravar() -> None:
    sessao = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível.",
    )

    geracao = generate_password(sessao, GenerationOptions())

    assert geracao.password is not None
    assert geracao.outcome.persistence is PersistenceState.UNAVAILABLE
    assert geracao.outcome.run_id is None
    assert exit_code_for(geracao.outcome) is ExitCode.HISTORY_NOT_PERSISTED