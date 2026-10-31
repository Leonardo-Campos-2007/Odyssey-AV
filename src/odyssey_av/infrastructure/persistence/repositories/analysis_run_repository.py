"""Persistência de AnalysisRun no SQLite."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from odyssey_av.domain.entities import AnalysisRun
from odyssey_av.domain.enums import ExecutionStatus, Module
from odyssey_av.shared.errors.handlers import PersistenceError


class AnalysisRunRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, run: AnalysisRun) -> None:
        """Insere uma execução. Cada chamada é uma transação própria."""
        try:
            with self._conn:
                self._conn.execute(
                    "INSERT INTO analysis_runs "
                    "(id, instance_id, module, command, status, started_at, "
                    "finished_at, duration_ms, summary) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        run.id,
                        run.instance_id,
                        run.module.value,
                        run.command,
                        run.status.value,
                        _to_iso(run.started_at),
                        _to_iso(run.finished_at),
                        run.duration_ms,
                        run.summary,
                    ),
                )
        except sqlite3.Error as exc:
            raise PersistenceError("Não foi possível registrar a execução no histórico.") from exc

    def update_status(
        self,
        run_id: str,
        status: ExecutionStatus,
        finished_at: datetime,
        duration_ms: int | None,
        summary: str | None = None,
    ) -> None:
        """Atualiza o estado final de uma execução existente."""
        try:
            with self._conn:
                cursor = self._conn.execute(
                    "UPDATE analysis_runs "
                    "SET status = ?, finished_at = ?, duration_ms = ?, summary = ? "
                    "WHERE id = ?",
                    (status.value, _to_iso(finished_at), duration_ms, summary, run_id),
                )
        except sqlite3.Error as exc:
            raise PersistenceError("Não foi possível atualizar a execução no histórico.") from exc

        if cursor.rowcount == 0:
            raise PersistenceError("Execução não encontrada no histórico.")

    def get(self, run_id: str) -> AnalysisRun | None:
        try:
            row = self._conn.execute(
                "SELECT * FROM analysis_runs WHERE id = ?", (run_id,)
            ).fetchone()
        except sqlite3.Error as exc:
            raise PersistenceError("Não foi possível consultar o histórico.") from exc

        return _to_entity(row) if row is not None else None
    
    def interrupt_runs_from_other_instances(
        self,
        current_instance_id: str,
        finished_at: datetime,
        summary: str,
    ) -> int:
        """Marca como INTERRUPTED as execuções RUNNING de outras instâncias.

        A instrução é única, portanto atômica: em caso de falha, nenhuma
        linha é alterada.
        """
        try:
            with self._conn:
                cursor = self._conn.execute(
                    "UPDATE analysis_runs "
                    "SET status = ?, finished_at = ?, summary = ? "
                    "WHERE status = ? AND instance_id != ?",
                    (
                        ExecutionStatus.INTERRUPTED.value,
                        _to_iso(finished_at),
                        summary,
                        ExecutionStatus.RUNNING.value,
                        current_instance_id,
                    ),
                )
        except sqlite3.Error as exc:
            raise PersistenceError("Não foi possível recuperar as execuções interrompidas.") from exc

        return cursor.rowcount   


def _to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat()


def _from_iso(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value)


def _to_entity(row: sqlite3.Row) -> AnalysisRun:
    run = AnalysisRun(
        instance_id=row["instance_id"],
        module=Module(row["module"]),
        command=row["command"],
        started_at=_from_iso(row["started_at"]),
        status=ExecutionStatus(row["status"]),
        id=row["id"],
        finished_at=_from_iso(row["finished_at"]),
        duration_ms=row["duration_ms"],
        summary=row["summary"],
    )
    return run