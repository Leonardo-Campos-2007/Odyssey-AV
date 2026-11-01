"""Caso de uso: gerar senha. A senha vai só para a saída do usuário, nunca para o histórico."""

from __future__ import annotations

from dataclasses import dataclass

from odyssey_av.application.services.execution_service import (
    ExecutionOutcome,
    OperationOutput,
    run_execution,
)
from odyssey_av.application.services.recovery_service import Session
from odyssey_av.domain.enums import Module, ResultStatus
from odyssey_av.modules.password.generator import (
    GenerationOptions,
    create_password,
    validate_options,
)


@dataclass(frozen=True)
class PasswordGeneration:
    outcome: ExecutionOutcome
    password: str | None = None
    length: int | None = None
    sets: tuple[str, ...] = ()


def generate_password(session: Session, options: GenerationOptions) -> PasswordGeneration:
    # Entrada inválida é rejeitada antes do registro (código 2, sem AnalysisRun).
    validate_options(options)
    produced: dict[str, str] = {}

    def operation() -> OperationOutput:
        produced["password"] = create_password(options)
        # Apenas metadados entram no histórico: comprimento e conjuntos usados.
        return OperationOutput(
            result_type="password_generation",
            result_status=ResultStatus.INFO,
            data={"length": options.length, "sets": list(options.set_names)},
        )

    outcome = run_execution(session, Module.PASSWORD, "password generate", operation)
    if outcome.output is None:
        return PasswordGeneration(outcome=outcome)

    return PasswordGeneration(
        outcome=outcome,
        password=produced["password"],
        length=options.length,
        sets=options.set_names,
    )