"""Caso de uso: avaliar senha. O valor avaliado nunca entra no resultado registrado."""

from __future__ import annotations

from dataclasses import dataclass

from odyssey_av.application.services.execution_service import (
    ExecutionOutcome,
    OperationOutput,
    run_execution,
)
from odyssey_av.application.services.recovery_service import Session
from odyssey_av.domain.enums import Module, ResultStatus
from odyssey_av.modules.password.evaluator import (
    PasswordAssessment,
    Strength,
    assess_password,
)


@dataclass(frozen=True)
class PasswordEvaluation:
    outcome: ExecutionOutcome
    assessment: PasswordAssessment


def evaluate_password(session: Session, password: str) -> PasswordEvaluation:
    # Senha vazia é rejeitada antes do registro (código 2, sem AnalysisRun).
    assessment = assess_password(password)
    weak = assessment.strength in (Strength.MUITO_FRACA, Strength.FRACA)

    def operation() -> OperationOutput:
        # Somente indicadores entram no histórico. A senha não é referenciada aqui.
        return OperationOutput(
            result_type="password_evaluation",
            result_status=ResultStatus.WARNING if weak else ResultStatus.INFO,
            data={
                "length": assessment.length,
                "sets": list(assessment.sets),
                "has_repetition": assessment.has_repetition,
                "score": assessment.score,
                "strength": assessment.strength.value,
            },
        )

    outcome = run_execution(session, Module.PASSWORD, "password evaluate", operation)
    return PasswordEvaluation(outcome=outcome, assessment=assessment)