"""Comandos odyssey password. A senha aparece apenas na saída do usuário."""

from __future__ import annotations

import getpass
import json
import sys
from typing import Any

import typer

from odyssey_av.application.services.execution_service import exit_code_for
from odyssey_av.application.use_cases.evaluate_password import (
    PasswordEvaluation,
    evaluate_password,
)
from odyssey_av.application.use_cases.generate_password import (
    PasswordGeneration,
    generate_password,
)
from odyssey_av.cli.context import AppContext
from odyssey_av.cli.formatting import history_label
from odyssey_av.modules.password.evaluator import STRENGTH_LABELS
from odyssey_av.modules.password.generator import (
    DEFAULT_LENGTH,
    MAX_LENGTH,
    MIN_LENGTH,
    SET_LABELS,
    GenerationOptions,
)
from odyssey_av.shared.errors.handlers import ExitCode

password_app = typer.Typer(help="Geração e avaliação de senhas.", add_completion=False)


@password_app.command("generate")
def generate(
    ctx: typer.Context,
    length: int = typer.Option(
        DEFAULT_LENGTH,
        "--length",
        help=f"Comprimento da senha, entre {MIN_LENGTH} e {MAX_LENGTH}.",
    ),
    no_upper: bool = typer.Option(False, "--no-upper", help="Remove letras maiúsculas."),
    no_digits: bool = typer.Option(False, "--no-digits", help="Remove dígitos."),
    no_symbols: bool = typer.Option(False, "--no-symbols", help="Remove símbolos."),
) -> None:
    """Gera uma senha com fonte criptográfica. Ela não é armazenada pelo Odyssey AV."""
    app_ctx: AppContext = ctx.obj
    options = GenerationOptions(
        length=length,
        upper=not no_upper,
        digits=not no_digits,
        symbols=not no_symbols,
    )
    generation = generate_password(app_ctx.session, options)

    if app_ctx.config.output_format == "json":
        typer.echo(json.dumps(_generation_dict(generation), ensure_ascii=False, indent=2))
        typer.echo("Aviso: a senha não é armazenada pelo Odyssey AV.", err=True)
    else:
        for line in _generation_lines(generation):
            typer.echo(line)

    code = exit_code_for(generation.outcome)
    if code != ExitCode.SUCCESS:
        raise typer.Exit(code=int(code))


@password_app.command("evaluate")
def evaluate(ctx: typer.Context) -> None:
    """Avalia uma senha digitada de forma oculta. A senha não é armazenada."""
    if not _stdin_is_interactive():
        typer.echo(
            "Erro: password evaluate exige um terminal interativo. "
            "A senha não é lida de pipes nem de arquivos.",
            err=True,
        )
        raise typer.Exit(code=int(ExitCode.INVALID_USAGE))

    app_ctx: AppContext = ctx.obj
    evaluation = evaluate_password(app_ctx.session, _read_password())

    if app_ctx.config.output_format == "json":
        typer.echo(json.dumps(_evaluation_dict(evaluation), ensure_ascii=False, indent=2))
    else:
        for line in _evaluation_lines(evaluation):
            typer.echo(line)

    code = exit_code_for(evaluation.outcome)
    if code != ExitCode.SUCCESS:
        raise typer.Exit(code=int(code))


def _stdin_is_interactive() -> bool:
    return sys.stdin is not None and sys.stdin.isatty()


def _read_password() -> str:
    return getpass.getpass("Senha: ")


def _generation_lines(generation: PasswordGeneration) -> list[str]:
    outcome = generation.outcome
    if generation.password is None:
        lines = ["Operação: falhou", f"Motivo: {outcome.message}"]
    else:
        lines = [
            "Operação: concluída",
            f"Senha: {generation.password}",
            f"Comprimento: {generation.length}",
            f"Conjuntos: {_set_labels(generation.sets)}",
        ]
    lines.append(f"Histórico: {history_label(outcome.persistence, outcome.run_id)}")
    return lines


def _generation_dict(generation: PasswordGeneration) -> dict[str, Any]:
    outcome = generation.outcome
    result = None
    if generation.password is not None:
        result = {
            "password": generation.password,
            "length": generation.length,
            "sets": list(generation.sets),
        }
    return {
        "operation": {"status": outcome.functional_status.value, "message": outcome.message},
        "result": result,
        "history": {"status": outcome.persistence.value, "run_id": outcome.run_id},
    }


def _evaluation_lines(evaluation: PasswordEvaluation) -> list[str]:
    outcome = evaluation.outcome
    assessment = evaluation.assessment
    return [
        "Operação: concluída",
        f"Força: {STRENGTH_LABELS[assessment.strength]}",
        f"Pontuação: {assessment.score}",
        f"Comprimento: {assessment.length}",
        f"Conjuntos: {_set_labels(assessment.sets)}",
        f"Repetições ou sequências: {'sim' if assessment.has_repetition else 'não'}",
        "Aviso: esta avaliação não garante segurança absoluta. A senha não foi armazenada.",
        f"Histórico: {history_label(outcome.persistence, outcome.run_id)}",
    ]


def _evaluation_dict(evaluation: PasswordEvaluation) -> dict[str, Any]:
    outcome = evaluation.outcome
    assessment = evaluation.assessment
    return {
        "operation": {"status": outcome.functional_status.value, "message": outcome.message},
        "result": {
            "strength": assessment.strength.value,
            "score": assessment.score,
            "length": assessment.length,
            "sets": list(assessment.sets),
            "has_repetition": assessment.has_repetition,
        },
        "history": {"status": outcome.persistence.value, "run_id": outcome.run_id},
    }


def _set_labels(sets: tuple[str, ...]) -> str:
    return ", ".join(SET_LABELS[name] for name in sets)