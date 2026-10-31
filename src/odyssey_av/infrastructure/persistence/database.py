"""Conexão SQLite e aplicação das migrations do histórico."""

from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

from odyssey_av.shared.errors.handlers import PersistenceError

APP_DIR_NAME = "odyssey-av"
DATABASE_FILENAME = "history.db"
MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def default_database_path() -> Path:
    """Retorna o caminho do histórico, no mesmo diretório de dados do lock."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / APP_DIR_NAME / DATABASE_FILENAME
    return Path.home() / f".{APP_DIR_NAME}" / DATABASE_FILENAME


def connect(path: Path) -> sqlite3.Connection:
    """Abre uma conexão com as chaves estrangeiras habilitadas.

    O SQLite desativa as chaves estrangeiras por padrão, e a ativação vale
    somente para a conexão em que é executada.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        enabled = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    except (OSError, sqlite3.Error) as exc:
        raise PersistenceError("Não foi possível abrir o banco de histórico.") from exc

    if enabled != 1:
        conn.close()
        raise PersistenceError("Não foi possível habilitar as chaves estrangeiras do histórico.")

    return conn


def _migration_files() -> list[tuple[int, Path]]:
    """Lista as migrations ordenadas pelo número do prefixo."""
    migrations = []
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        version = int(path.name.split("_", 1)[0])
        migrations.append((version, path))
    return migrations


def apply_migrations(conn: sqlite3.Connection) -> None:
    """Aplica as migrations ainda não registradas em PRAGMA user_version."""
    current = conn.execute("PRAGMA user_version").fetchone()[0]

    for version, path in _migration_files():
        if version <= current:
            continue
        try:
            conn.executescript(path.read_text(encoding="utf-8"))
        except (OSError, sqlite3.Error) as exc:
            if conn.in_transaction:
                conn.rollback()
            raise PersistenceError(f"Falha ao aplicar a migração {version:03d}.") from exc


def open_database(path: Path | None = None) -> sqlite3.Connection:
    """Abre o histórico e garante que o esquema esteja atualizado.

    Sem argumento, usa o caminho padrão do usuário.
    """
    conn = connect(path if path is not None else default_database_path())
    try:
        apply_migrations(conn)
    except Exception:
        conn.close()
        raise
    return conn