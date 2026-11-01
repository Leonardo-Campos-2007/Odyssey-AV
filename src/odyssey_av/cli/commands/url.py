"""Comando odyssey url analyze: análise estrutural local, sem acesso ao destino."""

from __future__ import annotations

import json
from typing import Any

import typer

from odyssey_av.application.services.execution_service import exit_code_for
from odyssey_av.application.use_cases.analyze_url import UrlAnalysisResult, run_url_analysis
from odyssey_av.cli.context import AppContext
from odyssey_av.cli.formatting import history_label
from odyssey_av.shared.errors.handlers import ExitCode

url_app = typer.Typer(help="Análise estrutural de URLs.", add_completion=False)

NOTICE = (
    "Aviso: indicadores são sinais de atenção, não confirmação de ameaça. "
    "Nenhuma requisição foi feita ao destino."
)


@url_app.command("analyze")
def analyze(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="URL com esquema, por exemplo https://exemplo.com."),
) -> None:
    """Analisa a estrutura da URL e aponta indicadores de atenção."""
    app_ctx: AppContext = ctx.obj
    result = run_url_analysis(app_ctx.session, url)

    if app_ctx.config.output_format == "json":
        typer.echo(json.dumps(_as_dict(result), ensure_ascii=False, indent=2))
    else:
        for line in _as_lines(result):
            typer.echo(line)

    code = exit_code_for(result.outcome)
    if code != ExitCode.SUCCESS:
        raise typer.Exit(code=int(code))


def _as_lines(result: UrlAnalysisResult) -> list[str]:
    analysis = result.analysis
    lines = [
        "Operação: concluída",
        f"URL normalizada: {analysis.normalized}",
        f"Esquema: {analysis.scheme}",
        f"Host: {analysis.host}",
        f"Porta: {analysis.port if analysis.port is not None else 'padrão'}",
        f"Caminho: {analysis.path}",
        f"Query: {'presente' if analysis.has_query else 'ausente'}",
        f"Fragmento: {'presente' if analysis.has_fragment else 'ausente'}",
        (
            "Credenciais: presentes (valores omitidos)"
            if analysis.has_credentials
            else "Credenciais: ausentes"
        ),
    ]
    if analysis.indicators:
        lines.append("Indicadores de atenção:")
        lines.extend(f"- {indicator.message}" for indicator in analysis.indicators)
    else:
        lines.append("Indicadores de atenção: nenhum")

    lines.append(NOTICE)
    lines.append(f"Histórico: {history_label(result.outcome.persistence, result.outcome.run_id)}")
    return lines


def _as_dict(result: UrlAnalysisResult) -> dict[str, Any]:
    outcome = result.outcome
    analysis = result.analysis
    return {
        "operation": {"status": outcome.functional_status.value, "message": outcome.message},
        "result": {
            "normalized": analysis.normalized,
            "scheme": analysis.scheme,
            "host": analysis.host,
            "port": analysis.port,
            "path": analysis.path,
            "has_query": analysis.has_query,
            "has_fragment": analysis.has_fragment,
            "has_credentials": analysis.has_credentials,
            "indicators": [
                {"code": indicator.code, "message": indicator.message}
                for indicator in analysis.indicators
            ],
        },
        "history": {"status": outcome.persistence.value, "run_id": outcome.run_id},
    }