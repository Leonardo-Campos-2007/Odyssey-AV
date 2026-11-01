"""Comando odyssey file analyze: análise somente leitura de arquivos."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

from odyssey_av.application.services.execution_service import exit_code_for
from odyssey_av.application.use_cases.analyze_file import FileAnalysisResult, run_file_analysis
from odyssey_av.cli.context import AppContext
from odyssey_av.cli.formatting import history_label
from odyssey_av.infrastructure.persistence.database import default_database_path
from odyssey_av.infrastructure.platform.instance_lock import default_lock_path
from odyssey_av.modules.file.signatures import FORMAT_LABELS
from odyssey_av.shared.errors.handlers import ExitCode

file_app = typer.Typer(help="Análise de arquivos (somente leitura).", add_completion=False)

NOTICE = (
    "Aviso: indicadores são sinais de atenção, não confirmação de segurança. "
    "O arquivo não foi executado nem modificado."
)


@file_app.command("analyze")
def analyze(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="Caminho do arquivo a analisar."),
) -> None:
    """Identifica o formato pelo cabeçalho e compara com a extensão."""
    app_ctx: AppContext = ctx.obj
    result = run_file_analysis(app_ctx.session, path, _protected_dirs())

    if app_ctx.config.output_format == "json":
        typer.echo(json.dumps(_as_dict(result), ensure_ascii=False, indent=2))
    else:
        for line in _as_lines(result):
            typer.echo(line)

    code = exit_code_for(result.outcome)
    if code != ExitCode.SUCCESS:
        raise typer.Exit(code=int(code))


def _protected_dirs() -> tuple[Path, ...]:
    """Diretórios de dados do aplicativo: banco de histórico e arquivo de bloqueio."""
    return (default_database_path().parent, default_lock_path().parent)


def _as_lines(result: FileAnalysisResult) -> list[str]:
    outcome = result.outcome
    analysis = result.analysis
    if analysis is None:
        lines = ["Operação: falhou", f"Motivo: {outcome.message}"]
    else:
        lines = [
            "Operação: concluída",
            f"Arquivo: {analysis.name}",
            f"Extensão: {analysis.extension or 'ausente'}",
            f"Tamanho: {analysis.size} bytes",
            f"Formato identificado: {FORMAT_LABELS[analysis.detected_format]}",
            f"Formato esperado pela extensão: {_expected_label(analysis.expected_format)}",
        ]
        if analysis.findings:
            lines.append("Indicadores de atenção:")
            lines.extend(f"- {finding.message}" for finding in analysis.findings)
        else:
            lines.append("Indicadores de atenção: nenhum")
        lines.append(NOTICE)
    lines.append(f"Histórico: {history_label(outcome.persistence, outcome.run_id)}")
    return lines


def _as_dict(result: FileAnalysisResult) -> dict[str, Any]:
    outcome = result.outcome
    analysis = result.analysis
    data = None
    if analysis is not None:
        data = {"name": analysis.name, **analysis.to_record()}
    return {
        "operation": {"status": outcome.functional_status.value, "message": outcome.message},
        "result": data,
        "history": {"status": outcome.persistence.value, "run_id": outcome.run_id},
    }


def _expected_label(expected: Any) -> str:
    if expected is None:
        return "não verificado (extensão não reconhecida)"
    return FORMAT_LABELS[expected]