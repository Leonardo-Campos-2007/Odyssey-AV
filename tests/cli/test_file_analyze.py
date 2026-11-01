"""Testes do comando odyssey file analyze (TC-CLI-001 e caminhos protegidos)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from odyssey_av.application.services.recovery_service import Session, start_session
from odyssey_av.cli.app import app
from odyssey_av.domain.enums import OperationalState
from odyssey_av.infrastructure.persistence.database import default_database_path
from odyssey_av.shared.errors.handlers import InvalidInputError

runner = CliRunner()
PDF = b"%PDF-1.7\n" + b"x" * 40


@pytest.fixture(autouse=True)
def _cwd_isolado(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def session(tmp_path: Path):
    sessao = start_session("instancia-teste", tmp_path / "h.db")
    yield sessao
    sessao.close()


def _contagem(session: Session) -> int:
    return session.connection.execute("SELECT COUNT(*) FROM analysis_runs").fetchone()[0]


def test_analyze_texto_mostra_formato_e_aviso(session: Session, tmp_path: Path) -> None:
    (tmp_path / "amostra.pdf").write_bytes(PDF)

    result = runner.invoke(app, ["file", "analyze", "amostra.pdf"], obj=session)

    assert result.exit_code == 0
    assert "Formato identificado: PDF" in result.output
    assert "não foi executado nem modificado" in result.output
    assert "Histórico: registrado" in result.output


def test_divergencia_aparece_como_indicador_com_codigo_zero(session: Session, tmp_path: Path) -> None:
    (tmp_path / "falso.exe").write_bytes(PDF)

    result = runner.invoke(app, ["file", "analyze", "falso.exe"], obj=session)

    assert result.exit_code == 0
    assert "A extensão .exe indica" in result.output


def test_arquivo_ausente_retorna_codigo_um(session: Session) -> None:
    result = runner.invoke(app, ["file", "analyze", "nao_existe.bin"], obj=session)

    assert result.exit_code == 1
    assert "Motivo: Arquivo não encontrado." in result.output


def test_json_retorna_campos_estruturados(session: Session, tmp_path: Path) -> None:
    (tmp_path / "amostra.pdf").write_bytes(PDF)

    result = runner.invoke(app, ["--json", "file", "analyze", "amostra.pdf"], obj=session)

    dados = json.loads(result.stdout)
    assert result.exit_code == 0
    assert dados["result"]["name"] == "amostra.pdf"
    assert dados["result"]["detected_format"] == "PDF"
    assert dados["history"]["status"] == "CONFIRMED"


def test_arquivo_do_banco_de_historico_e_recusado(session: Session) -> None:
    result = runner.invoke(app, ["file", "analyze", str(default_database_path())], obj=session)

    assert isinstance(result.exception, InvalidInputError)
    assert _contagem(session) == 0


def test_analyze_em_degraded_retorna_codigo_3(tmp_path: Path) -> None:
    (tmp_path / "amostra.pdf").write_bytes(PDF)
    sessao = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível.",
    )

    result = runner.invoke(app, ["file", "analyze", "amostra.pdf"], obj=sessao)

    assert result.exit_code == 3
    assert "Formato identificado: PDF" in result.output