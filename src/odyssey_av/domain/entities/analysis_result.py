"""Representação de um resultado produzido por uma execução."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from odyssey_av.domain.enums import ResultStatus


@dataclass
class AnalysisResult:
    analysis_run_id: str
    result_type: str
    status: ResultStatus
    created_at: datetime
    data: dict[str, Any] | None = None
    message: str | None = None
    id: str = field(default="")

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.analysis_run_id:
            raise ValueError("Todo resultado deve pertencer a uma execução.")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at deve possuir fuso horário (UTC).")