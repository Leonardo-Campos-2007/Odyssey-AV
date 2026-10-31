"""Testes do fluxo de execução do HASH: registro, resultado e situação do histórico."""

from __future__ import annotations

from pathlib import Path

import pytest

from odyssey_av.application.services.execution_service import (
    PersistenceState,
    exit_code_for,
)
from odyssey_av.application.services.recovery_service import Session, start_session
from odyssey_av.application.use_cases.calculate_hash import calculate_hash
from odyssey_av.domain.enums import (
    ComparisonStatus,
    ExecutionStatus,
    OperationalState,
    ResultStatus,
)
from odyssey_av.infrastructure.persistence.repositories.analysis_result_repository import (
    AnalysisResultRepository,
)
from odyssey_av.shared.errors.handlers import ExitCode, InvalidInputError

SHA256_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


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


def _status_das_execucoes(session: Session) -> list[str]:
    rows = session.connection.execute("SELECT status FROM analysis_runs").fetchall()
    return [row[0] for row in rows]


def test_sucesso_registra_execucao_e_resultado(session: Session, arquivo: Path) -> None:
    calculo = calculate_hash(session, arquivo)

    assert calculo.outcome.functional_status is ExecutionStatus.SUCCESS
    assert calculo.outcome.persistence is PersistenceState.CONFIRMED
    assert calculo.sha256 == SHA256_ABC
    assert _status_das_execucoes(session) == ["SUCCESS"]

    resultados = AnalysisResultRepository(session.connection).list_by_run(calculo.outcome.run_id)
    assert len(resultados) == 1
    assert resultados[0].status is ResultStatus.SUCCESS
    assert resultados[0].data["sha256"] == SHA256_ABC
    assert exit_code_for(calculo.outcome) is ExitCode.SUCCESS


def test_divergencia_gera_resultado_de_aviso(session: Session, arquivo: Path) -> None:
    calculo = calculate_hash(session, arquivo, reference="0" * 64)

    assert calculo.comparison is ComparisonStatus.MISMATCH
    resultados = AnalysisResultRepository(session.connection).list_by_run(calculo.outcome.run_id)
    assert resultados[0].status is ResultStatus.WARNING
    assert _status_das_execucoes(session) == ["SUCCESS"]
    assert exit_code_for(calculo.outcome) is ExitCode.SUCCESS


def test_arquivo_inexistente_registra_falha(session: Session, tmp_path: Path) -> None:
    calculo = calculate_hash(session, tmp_path / "nao_existe.bin")

    assert calculo.outcome.functional_status is ExecutionStatus.FAILED
    assert calculo.outcome.persistence is PersistenceState.CONFIRMED
    assert _status_das_execucoes(session) == ["FAILED"]
    assert AnalysisResultRepository(session.connection).list_by_run(calculo.outcome.run_id) == []
    assert exit_code_for(calculo.outcome) is ExitCode.FUNCTIONAL_FAILURE


def test_referencia_malformada_nao_gera_registro(session: Session, arquivo: Path) -> None:
    with pytest.raises(InvalidInputError):
        calculate_hash(session, arquivo, reference="xyz")

    assert _status_das_execucoes(session) == []


def test_sessao_degradada_executa_sem_gravar(arquivo: Path) -> None:
    sessao = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível.",
    )

    calculo = calculate_hash(sessao, arquivo)

    assert calculo.outcome.functional_status is ExecutionStatus.SUCCESS
    assert calculo.outcome.persistence is PersistenceState.UNAVAILABLE
    assert calculo.outcome.run_id is None
    assert calculo.sha256 == SHA256_ABC
    assert exit_code_for(calculo.outcome) is ExitCode.HISTORY_NOT_PERSISTED


def test_falha_de_gravacao_inicial_nao_impede_operacao(session: Session, arquivo: Path) -> None:
    session.connection.execute(
        "CREATE TRIGGER falha_insercao BEFORE INSERT ON analysis_runs "
        "BEGIN SELECT RAISE(ABORT, 'falha simulada'); END"
    )

    calculo = calculate_hash(session, arquivo)

    assert calculo.outcome.functional_status is ExecutionStatus.SUCCESS
    assert calculo.outcome.persistence is PersistenceState.FAILED
    assert calculo.sha256 == SHA256_ABC
    assert _status_das_execucoes(session) == []
    assert exit_code_for(calculo.outcome) is ExitCode.HISTORY_NOT_PERSISTED


def test_falha_funcional_prevalece_sobre_falha_de_persistencia(
    session: Session, tmp_path: Path
) -> None:
    session.connection.execute(
        "CREATE TRIGGER falha_insercao BEFORE INSERT ON analysis_runs "
        "BEGIN SELECT RAISE(ABORT, 'falha simulada'); END"
    )

    calculo = calculate_hash(session, tmp_path / "nao_existe.bin")

    assert calculo.outcome.functional_status is ExecutionStatus.FAILED
    assert calculo.outcome.persistence is PersistenceState.FAILED
    assert exit_code_for(calculo.outcome) is ExitCode.FUNCTIONAL_FAILURE