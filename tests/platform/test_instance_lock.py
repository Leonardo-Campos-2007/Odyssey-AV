"""Testes do bloqueio exclusivo da instância (TCO-001 a TCO-004)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from odyssey_av.infrastructure.platform.instance_lock import InstanceLock
from odyssey_av.shared.errors.handlers import InstanceLockedError

pytestmark = pytest.mark.platform

# Processo filho que adquire o bloqueio e permanece ativo até ser encerrado.
_CHILD_SCRIPT = """
import sys
import time
from pathlib import Path
from odyssey_av.infrastructure.platform.instance_lock import InstanceLock

lock = InstanceLock(Path(sys.argv[1]))
lock.acquire()
print("ready", flush=True)
time.sleep(60)
"""


def test_tco_001_primeira_instancia_adquire_bloqueio(lock_path: Path) -> None:
    lock = InstanceLock(lock_path)

    lock.acquire()
    try:
        assert lock.is_held
    finally:
        lock.release()


def test_tco_002_segunda_instancia_e_bloqueada(lock_path: Path) -> None:
    first = InstanceLock(lock_path)
    first.acquire()
    try:
        second = InstanceLock(lock_path)

        with pytest.raises(InstanceLockedError):
            second.acquire()
        assert not second.is_held
    finally:
        first.release()


def test_tco_003_liberacao_normal_permite_nova_instancia(lock_path: Path) -> None:
    first = InstanceLock(lock_path)
    first.acquire()
    first.release()
    assert not first.is_held

    second = InstanceLock(lock_path)
    second.acquire()
    second.release()


def test_release_pode_ser_chamado_mais_de_uma_vez(lock_path: Path) -> None:
    lock = InstanceLock(lock_path)
    lock.acquire()

    lock.release()
    lock.release()  # não deve levantar erro

    assert not lock.is_held


def test_gerenciador_de_contexto_libera_ao_sair(lock_path: Path) -> None:
    with InstanceLock(lock_path) as lock:
        assert lock.is_held

    assert not lock.is_held

    # Se o bloqueio não foi liberado, esta chamada falharia.
    reopened = InstanceLock(lock_path)
    reopened.acquire()
    reopened.release()


def test_tco_004_encerramento_inesperado_libera_bloqueio(lock_path: Path) -> None:
    child = subprocess.Popen(
        [sys.executable, "-c", _CHILD_SCRIPT, str(lock_path)],
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        # Espera o filho confirmar que adquiriu o bloqueio.
        assert child.stdout.readline().strip() == "ready"

        with pytest.raises(InstanceLockedError):
            InstanceLock(lock_path).acquire()
    finally:
        # Encerramento forçado, simulando uma falha inesperada.
        child.kill()
        child.wait(timeout=10)
        child.stdout.close()

    recovered = InstanceLock(lock_path)
    recovered.acquire()
    recovered.release()