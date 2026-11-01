"""Comandos odyssey password. A senha aparece apenas na saída do usuário."""

from __future__ import annotations

import json
from typing import Any

import typer

from odyssey_av.application.services.execution_service import exit_code_for
from odyssey_av.application.use_cases.generate_password import (
    PasswordGeneration,
    generate_password,
)
from odyssey_av.cli.context import AppContext
from odyssey_av.cli.formatting import history_label
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
        typer.echo(json.dumps(_as_dict(generation), ensure_ascii=False, indent=2))
        typer.echo("Aviso: a senha não é armazenada pelo Odyssey AV.", err=True)
    else:
        for line in _as_lines(generation):
            typer.echo(line)

    code = exit_code_for(generation.outcome)
    if code != ExitCode.SUCCESS:
        raise typer.Exit(code=int(code))


def _as_lines(generation: PasswordGeneration) -> list[str]:
    outcome = generation.outcome
    if generation.password is None:
        lines = ["Operação: falhou", f"Motivo: {outcome.message}"]
    else:
        lines = [
            "Operação: concluída",
            f"Senha: {generation.password}",
            f"Comprimento: {generation.length}",
            f"Conjuntos: {_labels(generation.sets)}",
        ]
    lines.append(f"Histórico: {history_label(outcome.persistence, outcome.run_id)}")
    return lines


def _as_dict(generation: PasswordGeneration) -> dict[str, Any]:
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


def _labels(sets: tuple[str, ...]) -> str:
    return ", ".join(SET_LABELS[name] for name in sets)