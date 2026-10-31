"""Persistência de AnalysisResult no SQLite."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from odyssey_av.domain.entities import AnalysisResult
from odyssey_av.domain.enums import ResultStatus
from odyssey_av.shared.errors.handlers import PersistenceError


class AnalysisResultRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, result: AnalysisResult) -> None:
        """Insere um resultado. Falha se a execução associada não existir."""
        try:
            with self._conn:
                self._conn.execute(
                    "INSERT INTO analysis_results "
                    "(id, analysis_run_id, result_type, status, data, message, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        result.id,
                        result.analysis_run_id,
                        result.result_type,
                        result.status.value,
                        json.dumps(result.data, ensure_ascii=False) if result.data is not None else None,
                        result.message,
                        result.created_at.astimezone(timezone.utc).isoformat(),
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise PersistenceError("Resultado não pertence a uma execução registrada.") from exc
        except sqlite3.Error as exc:
            raise PersistenceError("Não foi possível registrar o resultado no histórico.") from exc

    def list_by_run(self, run_id: str) -> list[AnalysisResult]:
        try:
            rows = self._conn.execute(
                "SELECT * FROM analysis_results WHERE analysis_run_id = ? ORDER BY created_at",
                (run_id,),
            ).fetchall()
        except sqlite3.Error as exc:
            raise PersistenceError("Não foi possível consultar os resultados.") from exc

        return [_to_entity(row) for row in rows]


def _to_entity(row: sqlite3.Row) -> AnalysisResult:
    return AnalysisResult(
        id=row["id"],
        analysis_run_id=row["analysis_run_id"],
        result_type=row["result_type"],
        status=ResultStatus(row["status"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        data=json.loads(row["data"]) if row["data"] is not None else None,
        message=row["message"],
    )