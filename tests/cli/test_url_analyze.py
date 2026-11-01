"""Testes do comando odyssey url analyze (TC-CLI-006)."""

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


def test_analyze_texto_mostra_url_normalizada(session: Session) -> None:
    result = runner.invoke(app, ["url", "analyze", "HTTPS://Exemplo.com:443/a/./b"], obj=session)

    assert result.exit_code == 0
    assert "URL normalizada: https://exemplo.com/a/b" in result.output
    assert "Histórico: registrado" in result.output


def test_analyze_json_retorna_componentes_e_indicadores(session: Session) -> None:
    result = runner.invoke(app, ["--json", "url", "analyze", "http://192.168.0.1/"], obj=session)

    dados = json.loads(result.stdout)
    assert result.exit_code == 0
    assert dados["result"]["host"] == "192.168.0.1"
    assert [i["code"] for i in dados["result"]["indicators"]] == ["IP_HOST"]
    assert dados["history"]["status"] == "CONFIRMED"


def test_indicador_aparece_na_saida_com_aviso(session: Session) -> None:
    result = runner.invoke(app, ["url", "analyze", "http://192.168.0.1/"], obj=session)

    assert result.exit_code == 0
    assert "endereço IP" in result.output
    assert "não confirmação de ameaça" in result.output


def test_credenciais_nao_aparecem_na_saida(session: Session) -> None:
    result = runner.invoke(
        app, ["url", "analyze", "https://usuario:SenhaSecreta123@exemplo.com/"], obj=session
    )

    assert result.exit_code == 0
    assert "Credenciais: presentes" in result.output
    assert "SenhaSecreta123" not in result.output


def test_entrada_invalida_e_erro_sem_registro(session: Session) -> None:
    result = runner.invoke(app, ["url", "analyze", "exemplo.com"], obj=session)

    assert isinstance(result.exception, InvalidInputError)
    assert _contagem(session) == 0


def test_analyze_em_degraded_retorna_codigo_3() -> None:
    sessao = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível.",
    )

    result = runner.invoke(app, ["url", "analyze", "https://exemplo.com/"], obj=sessao)

    assert result.exit_code == 3
    assert "indisponível" in result.output