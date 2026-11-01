"""Testes da análise de arquivos no fluxo de execução e no histórico (TI-015, TR-006, D-19)."""

from __future__ import annotations

from pathlib import Path

import pytest

from odyssey_av.application.services.execution_service import PersistenceState, exit_code_for
from odyssey_av.application.services.recovery_service import Session, start_session
from odyssey_av.application.use_cases.analyze_file import run_file_analysis
from odyssey_av.domain.enums import ExecutionStatus, Module, OperationalState, ResultStatus
from odyssey_av.infrastructure.filesystem.safe_open import OpenedFile
from odyssey_av.infrastructure.persistence.repositories.analysis_result_repository import (
    AnalysisResultRepository,
)
from odyssey_av.modules.file import analyzer
from odyssey_av.shared.errors.handlers import ExitCode, InvalidInputError

PDF = b"%PDF-1.7\n" + b"x" * 40
ALEATORIO = bytes(range(200, 256)) * 4
NOME_SENSIVEL = "minha_conta_bancaria.exe"


@pytest.fixture
def session(tmp_path: Path):
    sessao = start_session("instancia-teste", tmp_path / "h.db")
    yield sessao
    sessao.close()


def _arquivo(tmp_path: Path, nome: str, conteudo: bytes) -> Path:
    caminho = tmp_path / nome
    caminho.write_bytes(conteudo)
    return caminho


def _todo_o_historico(session: Session) -> str:
    partes: list[str] = []
    for tabela in ("analysis_runs", "analysis_results"):
        for row in session.connection.execute(f"SELECT * FROM {tabela}").fetchall():
            partes.extend(str(valor) for valor in tuple(row))
    return "\n".join(partes)


def test_registra_como_file_analyze(session: Session, tmp_path: Path) -> None:
    arquivo = _arquivo(tmp_path, "amostra.pdf", PDF)

    resultado = run_file_analysis(session, arquivo, [])

    assert resultado.outcome.functional_status is ExecutionStatus.SUCCESS
    linha = session.connection.execute(
        "SELECT module, command FROM analysis_runs WHERE id = ?", (resultado.outcome.run_id,)
    ).fetchone()
    assert tuple(linha) == (Module.FILE.value, "file analyze")
    assert exit_code_for(resultado.outcome) is ExitCode.SUCCESS


def test_nome_do_arquivo_nao_e_persistido(session: Session, tmp_path: Path) -> None:
    run_file_analysis(session, _arquivo(tmp_path, NOME_SENSIVEL, PDF), [])

    assert "minha_conta_bancaria" not in _todo_o_historico(session)


def test_divergencia_gera_resultado_de_aviso(session: Session, tmp_path: Path) -> None:
    resultado = run_file_analysis(session, _arquivo(tmp_path, "falso.exe", PDF), [])

    registros = AnalysisResultRepository(session.connection).list_by_run(resultado.outcome.run_id)
    assert registros[0].status is ResultStatus.WARNING
    assert exit_code_for(resultado.outcome) is ExitCode.SUCCESS


def test_arquivo_inexistente_registra_falha(session: Session, tmp_path: Path) -> None:
    resultado = run_file_analysis(session, tmp_path / "nao_existe.bin", [])

    assert resultado.outcome.functional_status is ExecutionStatus.FAILED
    assert resultado.analysis is None
    assert resultado.outcome.persistence is PersistenceState.CONFIRMED
    assert exit_code_for(resultado.outcome) is ExitCode.FUNCTIONAL_FAILURE


def test_caminho_protegido_nao_gera_registro(session: Session, tmp_path: Path) -> None:
    arquivo = _arquivo(tmp_path, "amostra.pdf", PDF)

    with pytest.raises(InvalidInputError):
        run_file_analysis(session, arquivo, [tmp_path])

    total = session.connection.execute("SELECT COUNT(*) FROM analysis_runs").fetchone()[0]
    assert total == 0


def test_alteracao_durante_leitura_registra_falha(
    session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    arquivo = _arquivo(tmp_path, "amostra.bin", ALEATORIO)
    original = analyzer.open_regular_file

    def tamanho_inflado(caminho):
        aberto = original(caminho)
        return OpenedFile(fd=aberto.fd, size=aberto.size + 1000)

    monkeypatch.setattr(analyzer, "open_regular_file", tamanho_inflado)

    resultado = run_file_analysis(session, arquivo, [])

    assert resultado.outcome.functional_status is ExecutionStatus.FAILED
    assert "alterado durante a leitura" in resultado.outcome.message


def test_degraded_analisa_sem_gravar(tmp_path: Path) -> None:
    sessao = Session(
        instance_id="instancia-teste",
        state=OperationalState.DEGRADED,
        message="Histórico indisponível.",
    )

    resultado = run_file_analysis(sessao, _arquivo(tmp_path, "amostra.pdf", PDF), [])

    assert resultado.analysis is not None
    assert resultado.outcome.persistence is PersistenceState.UNAVAILABLE
    assert resultado.outcome.run_id is None
    assert exit_code_for(resultado.outcome) is ExitCode.HISTORY_NOT_PERSISTED