"""Comandos odyssey history. Consultas e exportações nunca criam AnalysisRun (RF-025)."""

from __future__ import annotations

import typer

from odyssey_av.cli.context import AppContext
from odyssey_av.domain.enums import OperationalState
from odyssey_av.shared.errors.handlers import ExitCode

history_app = typer.Typer(help="Consulta e exportação do histórico.", add_completion=False)

DEGRADED_HISTORY_MESSAGE = (
    "Histórico indisponível nesta sessão: a recuperação falhou, "
    "e consultas HISTORY são recusadas."
)
NOT_IMPLEMENTED_MESSAGE = "Consulta do histórico ainda não implementada."


@history_app.command("list")
def list_history(ctx: typer.Context) -> None:
    """Lista execuções registradas. Recusada quando o histórico está indisponível."""
    app_ctx: AppContext = ctx.obj
    session = app_ctx.session

    if session is None or session.state is OperationalState.DEGRADED:
        typer.echo(f"Erro: {DEGRADED_HISTORY_MESSAGE}", err=True)
        raise typer.Exit(code=int(ExitCode.FUNCTIONAL_FAILURE))

    typer.echo(NOT_IMPLEMENTED_MESSAGE, err=True)
    raise typer.Exit(code=int(ExitCode.FUNCTIONAL_FAILURE))