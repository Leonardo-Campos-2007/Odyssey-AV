"""Ciclo de uma execução funcional: registro, operação, resultado e situação do histórico.

Regras aplicadas (RN-013, RF-032):
- O resultado funcional e a situação da persistência são tratados separadamente.
- Falha ao registrar RUNNING não impede a operação.
- Em DEGRADED nenhuma gravação é tentada.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from odyssey_av.application.services.recovery_service import Session
from odyssey_av.domain.entities import AnalysisResult, AnalysisRun
from odyssey_av.domain.enums import ExecutionStatus, Module, ResultStatus
from odyssey_av.infrastructure.persistence.repositories.analysis_result_repository import (
    AnalysisResultRepository,
)
from odyssey_av.infrastructure.persistence.repositories.analysis_run_repository import (
    AnalysisRunRepository,
)
from odyssey_av.shared.errors.handlers import ExitCode, OdysseyError, PersistenceError
from odyssey_av.shared.logging.logger import get_logger

log = get_logger("execution")

UNEXPECTED_ERROR_MESSAGE = "Erro inesperado durante a operação."


class PersistenceState(StrEnum):
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class OperationOutput:
    """Saída produzida por uma operação funcional, pronta para ser persistida."""

    result_type: str
    result_status: ResultStatus
    data: dict[str, Any]


@dataclass(frozen=True)
class ExecutionOutcome:
    functional_status: ExecutionStatus
    message: str
    persistence: PersistenceState
    run_id: str | None = None
    output: OperationOutput | None = None


def run_execution(
    session: Session,
    module: Module,
    command: str,
    operation: Callable[[], OperationOutput],
) -> ExecutionOutcome:
    """Executa a operação e registra o resultado no histórico, quando possível."""
    started_at = _utc_now()
    run = AnalysisRun(
        instance_id=session.instance_id,
        module=module,
        command=command,
        started_at=started_at,
    )

    persistence = PersistenceState.UNAVAILABLE
    recorded = False
    conn = session.connection
    if session.history_available and conn is not None:
        recorded = _try_register_start(conn, run)
        persistence = PersistenceState.CONFIRMED if recorded else PersistenceState.FAILED

    output: OperationOutput | None = None
    try:
        output = operation()
        status = ExecutionStatus.SUCCESS
        message = "Operação concluída."
    except OdysseyError as error:
        status = ExecutionStatus.FAILED
        message = error.message
    except Exception as error:
        log.error("Falha inesperada em %s: %s", command, type(error).__name__)
        status = ExecutionStatus.FAILED
        message = UNEXPECTED_ERROR_MESSAGE

    if recorded and conn is not None:
        persistence = _try_finalize(conn, run, status, _utc_now(), message, output)

    return ExecutionOutcome(
        functional_status=status,
        message=message,
        persistence=persistence,
        run_id=run.id if recorded else None,
        output=output,
    )


def exit_code_for(outcome: ExecutionOutcome) -> ExitCode:
    """Aplica a precedência de códigos de saída definida em API.md (seção 6.1)."""
    if outcome.functional_status is ExecutionStatus.FAILED:
        return ExitCode.FUNCTIONAL_FAILURE
    if outcome.persistence is PersistenceState.CONFIRMED:
        return ExitCode.SUCCESS
    return ExitCode.HISTORY_NOT_PERSISTED


def _try_register_start(conn: sqlite3.Connection, run: AnalysisRun) -> bool:
    try:
        AnalysisRunRepository(conn).add(run)
    except PersistenceError:
        log.error("Não foi possível registrar o início da execução no histórico.")
        return False
    return True


def _try_finalize(
    conn: sqlite3.Connection,
    run: AnalysisRun,
    status: ExecutionStatus,
    finished_at: datetime,
    message: str,
    output: OperationOutput | None,
) -> PersistenceState:
    duration_ms = int((finished_at - run.started_at).total_seconds() * 1000)
    try:
        if output is not None:
            AnalysisResultRepository(conn).add(
                AnalysisResult(
                    analysis_run_id=run.id,
                    result_type=output.result_type,
                    status=output.result_status,
                    created_at=finished_at,
                    data=output.data,
                )
            )
        AnalysisRunRepository(conn).update_status(
            run.id, status, finished_at, duration_ms, message
        )
    except PersistenceError:
        log.error("Não foi possível concluir o registro da execução %s.", run.id)
        return PersistenceState.FAILED
    return PersistenceState.CONFIRMED


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)