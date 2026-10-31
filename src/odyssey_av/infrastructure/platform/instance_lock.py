"""Bloqueio exclusivo da instância, compatível com Windows e Linux."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from odyssey_av.shared.errors.handlers import InstanceLockedError

APP_DIR_NAME = "odyssey-av"
LOCK_FILENAME = "instance.lock"


def default_lock_path() -> Path:
    """Retorna o diretório de dados do usuário onde o lock é criado."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / APP_DIR_NAME / LOCK_FILENAME
    return Path.home() / f".{APP_DIR_NAME}" / LOCK_FILENAME


if sys.platform == "win32":
    import msvcrt

    def _lock_nonblocking(fd: int) -> None:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)

    def _unlock(fd: int) -> None:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)

else:
    import fcntl

    def _lock_nonblocking(fd: int) -> None:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock(fd: int) -> None:
        fcntl.flock(fd, fcntl.LOCK_UN)


class InstanceLock:
    """Bloqueio exclusivo não bloqueante.

    Pode ser usado como gerenciador de contexto:

        with InstanceLock():
            ...
    """

    def __init__(self, path: Path | None = None) -> None:
        self._path = path if path is not None else default_lock_path()
        self._fd: int | None = None

    @property
    def path(self) -> Path:
        return self._path

    @property
    def is_held(self) -> bool:
        return self._fd is not None

    def acquire(self) -> None:
        """Adquire o bloqueio ou levanta InstanceLockedError se já estiver em uso."""
        if self._fd is not None:
            return

        self._path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self._path, os.O_RDWR | os.O_CREAT, 0o600)

        try:
            _lock_nonblocking(fd)
        except OSError as exc:
            os.close(fd)
            raise InstanceLockedError(
                "Outra instância do Odyssey AV já está em execução."
            ) from exc

        self._fd = fd

    def release(self) -> None:
        """Libera o bloqueio. Pode ser chamado mais de uma vez sem erro."""
        if self._fd is None:
            return

        try:
            _unlock(self._fd)
        finally:
            os.close(self._fd)
            self._fd = None

    def __enter__(self) -> InstanceLock:
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.release()