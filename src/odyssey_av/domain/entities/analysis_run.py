"""Representação de uma execução funcional."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from odyssey_av.domain.enums import ExecutionStatus, Module


@dataclass
class AnalysisRun:
    instance_id: str
    module: Module
    command: str
    started_at: datetime
    status: ExecutionStatus = ExecutionStatus.RUNNING
    id: str = ""
    finished_at: datetime | None = None
    duration_ms: int | None = None
    summary: str | None = None

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.started_at.tzinfo is None:
            raise ValueError("started_at deve possuir fuso horário (UTC).")