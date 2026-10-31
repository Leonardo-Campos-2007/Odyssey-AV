"""Aplicação de linha de comando (Typer) do Odyssey AV."""

import typer

from odyssey_av.shared.config.loader import load_config
from odyssey_av.shared.logging.logger import configure_logging

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

    ctx.obj = config

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)