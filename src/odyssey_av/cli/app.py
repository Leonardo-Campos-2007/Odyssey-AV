"""Aplicação de linha de comando (Typer) do Odyssey AV."""

import typer

from odyssey_av.application.services.recovery_service import Session
from odyssey_av.cli.commands.status import status as status_command
from odyssey_av.cli.context import AppContext
from odyssey_av.domain.enums import OperationalState
from odyssey_av.shared.config.loader import load_config
from odyssey_av.shared.logging.logger import configure_logging
from odyssey_av.cli.commands.hash import hash_app
from odyssey_av.cli.commands.history import history_app

app = typer.Typer(
    name="odyssey",
    help="Ferramenta modular de diagnóstico e análise de segurança.",
    add_completion=False,
    pretty_exceptions_enable=False,
)


@app.callback(invoke_without_command=True)
def root(
    ctx: typer.Context,
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Apresenta a saída em formato JSON.",
    ),
    log_level: str | None = typer.Option(
        None,
        "--log-level",
        help="Nível de log: DEBUG, INFO, WARNING ou ERROR.",
    ),
) -> None:
    """Configura a aplicação antes da execução de qualquer comando."""
    overrides = {
        "output_format": "json" if json_output else None,
        "log_level": log_level.upper() if log_level else None,
    }

    config = load_config(overrides)
    configure_logging(config.log_level)

    session = ctx.obj if isinstance(ctx.obj, Session) else None
    ctx.obj = AppContext(config=config, session=session)

    if session is not None and session.state is OperationalState.DEGRADED:
        typer.echo(f"Aviso: {session.message}", err=True)

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


app.command("status")(status_command)
app.add_typer(hash_app, name="hash")
app.add_typer(history_app, name="history")