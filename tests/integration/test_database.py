"""Testes da conexão SQLite e das migrations do histórico."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from odyssey_av.infrastructure.persistence.database import connect, open_database
from odyssey_av.shared.errors.handlers import PersistenceError


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "history.db"


def test_chaves_estrangeiras_estao_habilitadas(db_path: Path) -> None:
    conn = open_database(db_path)
    try:
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        conn.close()


def test_migration_inicial_aplicada(db_path: Path) -> None:
    conn = open_database(db_path)
    try:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 1

        tabelas = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        assert {"analysis_runs", "analysis_results"} <= tabelas
    finally:
        conn.close()


def test_reabrir_nao_reaplica_migration(db_path: Path) -> None:
    open_database(db_path).close()

    conn = open_database(db_path)
    try:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 1
    finally:
        conn.close()


def test_resultado_sem_execucao_e_rejeitado(db_path: Path) -> None:
    """Integridade referencial: AnalysisResult precisa de AnalysisRun existente (TB-003)."""
    conn = open_database(db_path)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO analysis_results "
                "(id, analysis_run_id, result_type, status, created_at) "
                "VALUES ('r1', 'inexistente', 'hash', 'SUCCESS', '2026-01-01T00:00:00Z')"
            )
    finally:
        conn.close()


def test_modulo_invalido_e_rejeitado_pelo_banco(db_path: Path) -> None:
    conn = open_database(db_path)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO analysis_runs "
                "(id, instance_id, module, command, status, started_at) "
                "VALUES ('a1', 'i1', 'INVALIDO', 'x', 'RUNNING', '2026-01-01T00:00:00Z')"
            )
    finally:
        conn.close()


def test_caminho_sem_permissao_gera_persistence_error(tmp_path: Path) -> None:
    arquivo = tmp_path / "bloqueado"
    arquivo.write_text("não é um diretório", encoding="utf-8")

    with pytest.raises(PersistenceError):
        connect(arquivo / "history.db")