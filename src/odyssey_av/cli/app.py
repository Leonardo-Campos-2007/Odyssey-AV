"""Aplicação de linha de comando (Typer) do Odyssey AV."""

import typer

from odyssey_av.application.services.recovery_service import Session
from odyssey_av.cli import theme
from odyssey_av.cli.commands.file import file_app
from odyssey_av.cli.commands.hash import hash_app
from odyssey_av.cli.commands.history import history_app
from odyssey_av.cli.commands.password import password_app
from odyssey_av.cli.commands.status import status as status_command
from odyssey_av.cli.commands.url import url_app
from odyssey_av.cli.context import AppContext
from odyssey_av.domain.enums import OperationalState
from odyssey_av.shared.config.loader import load_config
from odyssey_av.shared.logging.logger import configure_logging

PANEL_ANALYSIS = f"{theme.SYMBOLS.diamond} Análise de arquivos e URLs"
PANEL_INTEGRITY = f"{theme.SYMBOLS.square} Integridade e senhas"
PANEL_SYSTEM = f"{theme.SYMBOLS.circle} Sistema e histórico"

ROOT_HELP = (
    f"[{theme.PRIMARY}]Odyssey AV[/]: ferramenta de análise e diagnóstico de segurança.\n\n"
    f"{theme.SYMBOLS.square} [{theme.SUCCESS}]Local e somente leitura[/]: nenhum arquivo é "
    "executado ou modificado, e nenhuma URL é acessada.\n"
    f"{theme.SYMBOLS.triangle} [{theme.WARNING}]Indicadores[/] são sinais de atenção, "
    "não confirmação de ameaça."
)

EPILOG = "\n".join(
    [
        f"[{theme.PRIMARY}]Exemplos[/]",
        "",
        theme.example("odyssey status", "estado da sessão"),
        theme.example("odyssey hash calculate arquivo.pdf", "SHA-256 do arquivo"),
        theme.example(
            "odyssey hash compare arquivo.pdf --reference SHA256_ESPERADO",
            "confere com o valor",
        ),
        theme.example("odyssey password evaluate", "senha digitada de forma oculta"),
        theme.example(
            'odyssey url analyze "https://exemplo.com/caminho"',
            "sem acessar o site",
        ),
        theme.example("odyssey file analyze arquivo.exe", "formato pelo cabeçalho"),
        "",
        f"[{theme.MUTED}]Use odyssey COMANDO --help para ver as opções de cada comando.[/]",
    ]
)

app = typer.Typer(
    name="odyssey",
    help=ROOT_HELP,
    epilog=EPILOG,
    add_completion=False,
    pretty_exceptions_enable=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
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


app.command(
    "status",
    help="Estado da sessão, instância e execuções recuperadas.",
    rich_help_panel=PANEL_SYSTEM,
)(status_command)

app.add_typer(file_app, name="file", rich_help_panel=PANEL_ANALYSIS)
app.add_typer(url_app, name="url", rich_help_panel=PANEL_ANALYSIS)
app.add_typer(hash_app, name="hash", rich_help_panel=PANEL_INTEGRITY)
app.add_typer(password_app, name="password", rich_help_panel=PANEL_INTEGRITY)
app.add_typer(history_app, name="history", rich_help_panel=PANEL_SYSTEM)