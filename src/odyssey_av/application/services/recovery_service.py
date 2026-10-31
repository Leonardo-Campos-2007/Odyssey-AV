"""Recuperação de execuções interrompidas e definição do estado operacional."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from odyssey_av.domain.enums import OperationalState
from odyssey_av.infrastructure.persistence.database import open_database
from odyssey_av.infrastructure.persistence.repositories.analysis_run_repository import (
    AnalysisRunRepository,
)
from odyssey_av.shared.errors.handlers import PersistenceError

INTERRUPTED_SUMMARY = "Execução interrompida: a instância anterior encerrou antes da conclusão."
DEGRADED_MESSAGE = (
    "Histórico indisponível nesta sessão: a recuperação falhou. "
    "Os resultados das operações não serão armazenados."
)


@dataclass
class Session:
    """Estado da sessão atual e, quando disponível, a conexão com o histórico."""

    instance_id: str
    state: OperationalState
    recovered_count: int = 0
    message: str = ""
    connection: sqlite3.Connection | None = None

    @property
    def history_available(self) -> bool:
        """Indica se gravações e consultas HISTORY são permitidas nesta sessão."""
        return self.state is OperationalState.NORMAL and self.connection is not None

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None


def recover_interrupted_runs(conn: sqlite3.Connection, current_instance_id: str) -> int:
    """Marca como INTERRUPTED as execuções RUNNING de instâncias anteriores.

    Retorna a quantidade de execuções recuperadas.
    """
    repo = AnalysisRunRepository(conn)
    return repo.interrupt_runs_from_other_instances(
        current_instance_id,
        finished_at=datetime.now(timezone.utc),
        summary=INTERRUPTED_SUMMARY,
    )


def start_session(instance_id: str, database_path: Path | None = None) -> Session:
    """Abre o histórico, executa a recuperação e define o estado operacional.

    Falha ao abrir o banco ou ao recuperar resulta em DEGRADED. Nesse estado,
    nenhuma conexão é mantida, portanto nenhuma gravação ou consulta é possível.

    Deve ser chamada somente depois da aquisição do bloqueio exclusivo.
    """
    try:
        conn = open_database(database_path)
    except PersistenceError:
        return _degraded(instance_id)

    try:
        recovered = recover_interrupted_runs(conn, instance_id)
    except PersistenceError:
        conn.close()
        return _degraded(instance_id)

    return Session(
        instance_id=instance_id,
        state=OperationalState.NORMAL,
        recovered_count=recovered,
        connection=conn,
    )


def _degraded(instance_id: str) -> Session:
    return Session(
        instance_id=instance_id,
        state=OperationalState.DEGRADED,
        message=DEGRADED_MESSAGE,
    )