"""Caso de uso: analisar URL localmente. Credenciais e query não são gravadas."""

from __future__ import annotations

from dataclasses import dataclass

from odyssey_av.application.services.execution_service import (
    ExecutionOutcome,
    OperationOutput,
    run_execution,
)
from odyssey_av.application.services.recovery_service import Session
from odyssey_av.domain.enums import Module, ResultStatus
from odyssey_av.modules.url.analyzer import UrlAnalysis, analyze_url


@dataclass(frozen=True)
class UrlAnalysisResult:
    outcome: ExecutionOutcome
    analysis: UrlAnalysis


def run_url_analysis(session: Session, raw_url: str) -> UrlAnalysisResult:
    # Entrada inválida é rejeitada antes do registro (código 2, sem AnalysisRun).
    analysis = analyze_url(raw_url)

    def operation() -> OperationOutput:
        return OperationOutput(
            result_type="url_analysis",
            result_status=ResultStatus.WARNING if analysis.indicators else ResultStatus.INFO,
            data=analysis.to_record(),
        )

    outcome = run_execution(session, Module.URL, "url analyze", operation)
    return UrlAnalysisResult(outcome=outcome, analysis=analysis)