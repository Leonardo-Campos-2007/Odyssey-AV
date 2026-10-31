"""Casos de uso do HASH: calcular SHA-256 e comparar com uma referência."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from odyssey_av.application.services.execution_service import (
    ExecutionOutcome,
    OperationOutput,
    run_execution,
)
from odyssey_av.application.services.recovery_service import Session
from odyssey_av.domain.enums import ComparisonStatus, Module, ResultStatus
from odyssey_av.modules.hash.calculator import calculate_sha256, normalize_reference
from odyssey_av.shared.errors.handlers import InvalidInputError


@dataclass(frozen=True)
class HashCalculation:
    outcome: ExecutionOutcome
    sha256: str | None = None
    size: int | None = None
    comparison: ComparisonStatus | None = None


def calculate_hash(session: Session, path: Path, reference: str | None = None) -> HashCalculation:
    """Calcula o SHA-256. Com referência, compara; sem ela, o resultado é NO_REFERENCE."""
    return _run(session, path, normalize_reference(reference), verb="calculate")


def compare_hash(session: Session, path: Path, reference: str) -> HashCalculation:
    """Compara o SHA-256 do arquivo com uma referência obrigatória."""
    normalized = normalize_reference(reference)
    if normalized is None:
        raise InvalidInputError("Informe a referência SHA-256 com --reference.")
    return _run(session, path, normalized, verb="compare")


def _run(session: Session, path: Path, reference: str | None, verb: str) -> HashCalculation:
    command = f"hash {verb} {path.name}"

    def operation() -> OperationOutput:
        result = calculate_sha256(path, reference)
        status = (
            ResultStatus.WARNING
            if result.comparison is ComparisonStatus.MISMATCH
            else ResultStatus.SUCCESS
        )
        return OperationOutput(
            result_type="sha256",
            result_status=status,
            data={
                "sha256": result.sha256,
                "size": result.size,
                "comparison": result.comparison.value,
            },
        )

    outcome = run_execution(session, Module.HASH, command, operation)
    if outcome.output is None:
        return HashCalculation(outcome=outcome)

    data = outcome.output.data
    return HashCalculation(
        outcome=outcome,
        sha256=data["sha256"],
        size=data["size"],
        comparison=ComparisonStatus(data["comparison"]),
    )