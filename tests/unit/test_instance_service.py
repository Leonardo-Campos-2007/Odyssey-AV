"""Testes do serviço de instância: identidade e bloqueio (TCO-006)."""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from odyssey_av.application.services.instance_service import InstanceService
from odyssey_av.shared.errors.handlers import InstanceLockedError

pytestmark = pytest.mark.security


def test_tco_006_cada_instancia_recebe_uuid_proprio(lock_path: Path) -> None:
    first = InstanceService(lock_path)
    second = InstanceService(lock_path)

    assert first.instance_id != second.instance_id


def test_instance_id_e_um_uuid_valido(lock_path: Path) -> None:
    service = InstanceService(lock_path)

    parsed = uuid.UUID(service.instance_id)

    assert parsed.version == 4


def test_instance_id_nao_muda_durante_o_ciclo_de_vida(lock_path: Path) -> None:
    service = InstanceService(lock_path)
    before = service.instance_id

    service.start()
    service.stop()

    assert service.instance_id == before


def test_start_ativa_e_stop_desativa(lock_path: Path) -> None:
    service = InstanceService(lock_path)

    service.start()
    assert service.is_active

    service.stop()
    assert not service.is_active


def test_segunda_instancia_nao_inicia_enquanto_primeira_estiver_ativa(lock_path: Path) -> None:
    first = InstanceService(lock_path)
    second = InstanceService(lock_path)
    first.start()
    try:
        with pytest.raises(InstanceLockedError):
            second.start()
        assert not second.is_active
    finally:
        first.stop()


def test_segunda_instancia_inicia_apos_stop_da_primeira(lock_path: Path) -> None:
    first = InstanceService(lock_path)
    second = InstanceService(lock_path)
    first.start()
    first.stop()

    second.start()
    assert second.is_active
    second.stop()


def test_contexto_inicia_e_libera_automaticamente(lock_path: Path) -> None:
    with InstanceService(lock_path) as service:
        assert service.is_active

    assert not service.is_active


def test_contexto_libera_mesmo_quando_ocorre_excecao(lock_path: Path) -> None:
    service = InstanceService(lock_path)

    with pytest.raises(RuntimeError):
        with service:
            raise RuntimeError("falha simulada")

    assert not service.is_active


def test_stop_pode_ser_chamado_mais_de_uma_vez(lock_path: Path) -> None:
    service = InstanceService(lock_path)
    service.start()

    service.stop()
    service.stop()  # não deve levantar erro

    assert not service.is_active