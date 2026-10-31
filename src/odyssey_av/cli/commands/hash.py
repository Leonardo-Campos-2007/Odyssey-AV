"""Comando odyssey hash: cálculo e comparação de SHA-256."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

from odyssey_av.application.services.execution_service import (
    PersistenceState,
    exit_code_for,
)
from odyssey_av.application.use_cases.calculate_hash import HashCalculation, calculate_hash
from odyssey_av.cli.context import AppContext
from odyssey_av.domain.enums import ExecutionStatus

hash_app = typer.Typer(help="Cálculo e comparação de SHA-256.", add_completion=False)


@hash_app.command("calculate")
def calculate(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="Caminho do arquivo a analisar."),
    reference: str | None = typer.Option(
        None,
        "--reference",
        help="SHA-256 esperado, para comparação.",
    ),
) -> None:
    """Calcula o SHA-256 do arquivo e, se informado, compara com a referência."""
    app_ctx: AppContext = ctx.obj
    calculation = calculate_hash(app_ctx.session, path, reference)

    if app_ctx.config.output_format == "json":
        typer.echo(json.dumps(_as_dict(calculation), ensure_ascii=False, indent=2))
    else:
        for line in _as_lines(calculation):
            typer.echo(line)

    code = exit_code_for(calculation.outcome)
    if code != 0:
        raise typer.Exit(code=int(code))


def _as_lines(calculation: HashCalculation) -> list[str]:
    outcome = calculation.outcome
    if outcome.functional_status is ExecutionStatus.FAILED:
        lines = ["Operação: falhou", f"Motivo: {outcome.message}"]
    else:
        lines = [
            "Operação: concluída",
            f"SHA-256: {calculation.sha256}",
            f"Tamanho: {calculation.size} bytes",
            f"Comparação: {calculation.comparison.value}",
        ]
    lines.append(f"Histórico: {_history_label(outcome.persistence, outcome.run_id)}")
    return lines


def _history_label(persistence: PersistenceState, run_id: str | None) -> str:
    if persistence is PersistenceState.CONFIRMED:
        return f"registrado (ID {run_id})"
    if persistence is PersistenceState.FAILED:
        return "não registrado: falha de gravação"
    return "não registrado: histórico indisponível nesta sessão"


def _as_dict(calculation: HashCalculation) -> dict[str, Any]:
    outcome = calculation.outcome
    result = None
    if calculation.sha256 is not None:
        result = {
            "sha256": calculation.sha256,
            "size": calculation.size,
            "comparison": calculation.comparison.value,
        }
    return {
        "operation": {"status": outcome.functional_status.value, "message": outcome.message},
        "result": result,
        "history": {"status": outcome.persistence.value, "run_id": outcome.run_id},
    }