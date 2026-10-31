"""Ciclo de vida da instância: identificação e bloqueio exclusivo."""

from __future__ import annotations

import uuid
from pathlib import Path

from odyssey_av.infrastructure.platform.instance_lock import InstanceLock


class InstanceService:
    """Controla a identidade e a exclusividade da instância atual.

    O ``instance_id`` é gerado a cada criação do serviço. Ele não depende
    do PID, que pode ser reutilizado pelo sistema operacional.
    """

    def __init__(self, lock_path: Path | None = None) -> None:
        self._instance_id = str(uuid.uuid4())
        self._lock = InstanceLock(lock_path)

    @property
    def instance_id(self) -> str:
        return self._instance_id

    @property
    def is_active(self) -> bool:
        return self._lock.is_held

    def start(self) -> None:
        """Adquire o bloqueio exclusivo.

        Levanta InstanceLockedError se outra instância estiver ativa.
        """
        self._lock.acquire()

    def stop(self) -> None:
        """Libera o bloqueio. Pode ser chamado mais de uma vez."""
        self._lock.release()

    def __enter__(self) -> InstanceService:
        self.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.stop()