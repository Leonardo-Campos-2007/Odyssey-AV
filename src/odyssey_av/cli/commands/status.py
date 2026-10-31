"""Comando odyssey status: informa o estado da sessão. Não cria registros de execução."""

from __future__ import annotations

import json
from typing import Any

import typer

from odyssey_av.cli.context import AppContext


def status(ctx: typer.Context) -> None:
    """Mostra o estado operacional, o instance_id e as execuções recuperadas."""
    app_ctx: AppContext = ctx.obj
    data = _snapshot(app_ctx)

    if app_ctx.config.output_format == "json":
        typer.echo(json.dumps(data, ensure_ascii=False, indent=2))
        return

    typer.echo(f"Estado: {data['state']}")
    typer.echo(f"Instância: {data['instance_id'] or '-'}")
    typer.echo(f"Execuções recuperadas: {data['recovered_runs']}")
    typer.echo(f"Histórico: {'disponível' if data['history_available'] else 'indisponível'}")


def _snapshot(app_ctx: AppContext) -> dict[str, Any]:
    session = app_ctx.session
    if session is None:
        return {
            "state": "NAO_INICIADA",
            "instance_id": None,
            "recovered_runs": 0,
            "history_available": False,
            "message": "Sessão não iniciada.",
        }
    return {
        "state": session.state.value,
        "instance_id": session.instance_id,
        "recovered_runs": session.recovered_count,
        "history_available": session.history_available,
        "message": session.message,
    }