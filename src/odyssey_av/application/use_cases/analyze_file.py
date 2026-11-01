"""Caso de uso: analisar arquivo (somente leitura).

Registra extensão, tamanho e formato, sem o nome do arquivo (D-19).
Caminhos protegidos são recusados antes de qualquer leitura e antes do registro (ST-028).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from odyssey_av.application.services.execution_service import (
    ExecutionOutcome,
    OperationOutput,
    run_execution,
)
from odyssey_av.application.services.recovery_service import Session
from odyssey_av.domain.enums import Module, ResultStatus
from odyssey_av.modules.file.analyzer import FileAnalysis, analyze_file
from odyssey_av.shared.validation.validators import ensure_outside_protected_dirs

COMMAND = "file analyze"


@dataclass(frozen=True)
class FileAnalysisResult:
    outcome: ExecutionOutcome
    analysis: FileAnalysis | None


def run_file_analysis(
    session: Session,
    path: Path,
    protected_dirs: Iterable[Path],
) -> FileAnalysisResult:
    ensure_outside_protected_dirs(path, protected_dirs)

    produced: dict[str, FileAnalysis] = {}

    def operation() -> OperationOutput:
        analysis = analyze_file(path)
        produced["analysis"] = analysis
        return OperationOutput(
            result_type="file_analysis",
            result_status=ResultStatus.WARNING if analysis.findings else ResultStatus.INFO,
            data=analysis.to_record(),
        )

    outcome = run_execution(session, Module.FILE, COMMAND, operation)
    return FileAnalysisResult(outcome=outcome, analysis=produced.get("analysis"))