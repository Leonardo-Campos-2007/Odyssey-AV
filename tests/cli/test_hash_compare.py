"""Testes do comando odyssey hash compare (decisão D-09, opção A)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from odyssey_av.application.services.recovery_service import Session, start_session
from odyssey_av.cli.app import app
from odyssey_av.domain.enums import OperationalState
from odyssey_av.shared.errors.handlers import InvalidInputError

runner = CliRunner()
SHA256_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
DIVERGENTE = "0" * 64


@pytest.fixture(autouse=True)
def _cwd_isolado(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def arquivo(tmp_path: Path) -> Path:
    caminho = tmp_path / "abc.txt"
    caminho.write_bytes(b"abc")
    return caminho


@pytest.fixture
def session(tmp_path: Path):
    sessao = start_session("instancia-teste", tmp_path / "h.db")
    yield sessao
    sessao.close()


def _contagem(session: Session, tabela: str) -> int:
    return session.connection.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]


def test_referencia_confere_retorna_zero(session: Session, arquivo: Path) -> None:
    result = runner.invoke(app, ["hash", "compare", str(arquivo), "--reference", SHA256_ABC], obj=session)

    assert result.exit_code == 0
    assert "Comparação: MATCH" in result.output
    assert "Histórico: registrado" in result.output


def test_divergencia_retorna_um_e_registra_aviso(session: Session, arquivo: Path) -> None:
    result = runner.invoke(app, ["hash", "compare", str(arquivo), "--reference", DIVERGENTE], obj=session)

    assert result.exit_code == 1
    assert "Comparação: MISMATCH" in result.output
    assert "não confere" in result.output
    assert _contagem(session, "analysis_runs") == 1
    status = session.connection.execute("SELECT status FROM analysis_runs").fetchone()[0]
    assert status == "SUCCESS"


def test_referencia_ausente_e_erro_de_uso_sem_registro(session: Session, arquivo: Path) -> None:
    result = runner.invoke(app, ["hash", "compare", str(arquivo)], obj=session)

    assert result.exit_code == 2
    assert _contagem(session, "analysis_runs") == 0


def test_referencia_malformada_nao_gera_registro(session: Session, arquivo: Path) -> None:
    result = runner.invoke(app, ["hash", "compare", str(arquivo), "--reference", "xyz"], obj=session)

    assert isinstance(result.exception, InvalidInputError)
    assert _contagem(session, "analysis_runs") == 0


def test_json_divergente_informa_comparacao_e_codigo(session: Session, arquivo: Path) -> None:
    result = runner.invoke(
        app, ["--json", "hash", "compare", str(arquivo), "--reference", DIVERGENTE], obj=session
    )

    dados = json.loads(result.output)
    assert result.exit_code == 1
    assert dados["operation"]["status"] == "SUCCESS"
    assert dados["result"]["comparison"] == "MISMATCH"
    assert dados["history"]["status"] == "CONFIRMED"


def test_degraded_com_referencia_correta_retorna_codigo_3(arquivo: Path) -> None:
    sessao = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível nesta sessão.",
    )

    result = runner.invoke(app, ["hash", "compare", str(arquivo), "--reference", SHA256_ABC], obj=sessao)

    assert result.exit_code == 3
    assert "Comparação: MATCH" in result.output


def test_degraded_com_divergencia_retorna_codigo_1(arquivo: Path) -> None:
    sessao = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível nesta sessão.",
    )

    result = runner.invoke(app, ["hash", "compare", str(arquivo), "--reference", DIVERGENTE], obj=sessao)

    assert result.exit_code == 1