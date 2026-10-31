"""Testes do cálculo e da comparação de SHA-256 (TU-HASH-001 a 008)."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

from odyssey_av.domain.enums import ComparisonStatus
from odyssey_av.modules.hash import calculator
from odyssey_av.modules.hash.calculator import calculate_sha256
from odyssey_av.shared.errors.handlers import InvalidInputError

SHA256_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
SHA256_VAZIO = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_tu_hash_001_calcula_sha256_conhecido(tmp_path: Path) -> None:
    arquivo = tmp_path / "abc.txt"
    arquivo.write_bytes(b"abc")

    resultado = calculate_sha256(arquivo)

    assert resultado.sha256 == SHA256_ABC
    assert resultado.size == 3


def test_tu_hash_002_arquivo_vazio(tmp_path: Path) -> None:
    arquivo = tmp_path / "vazio.bin"
    arquivo.write_bytes(b"")

    resultado = calculate_sha256(arquivo)

    assert resultado.sha256 == SHA256_VAZIO
    assert resultado.size == 0


def test_tu_hash_003_referencia_igual_gera_match(tmp_path: Path) -> None:
    arquivo = tmp_path / "abc.txt"
    arquivo.write_bytes(b"abc")

    resultado = calculate_sha256(arquivo, reference=SHA256_ABC.upper())

    assert resultado.comparison is ComparisonStatus.MATCH


def test_tu_hash_004_referencia_diferente_gera_mismatch(tmp_path: Path) -> None:
    arquivo = tmp_path / "abc.txt"
    arquivo.write_bytes(b"abc")

    resultado = calculate_sha256(arquivo, reference="0" * 64)

    assert resultado.comparison is ComparisonStatus.MISMATCH


def test_tu_hash_005_sem_referencia_gera_no_reference(tmp_path: Path) -> None:
    arquivo = tmp_path / "abc.txt"
    arquivo.write_bytes(b"abc")

    resultado = calculate_sha256(arquivo)

    assert resultado.comparison is ComparisonStatus.NO_REFERENCE
    assert resultado.reference is None


def test_tu_hash_006_referencia_malformada_e_rejeitada(tmp_path: Path) -> None:
    arquivo = tmp_path / "abc.txt"
    arquivo.write_bytes(b"abc")

    with pytest.raises(InvalidInputError, match="Referência SHA-256 inválida"):
        calculate_sha256(arquivo, reference="xyz")


def test_tu_hash_007_leitura_em_blocos_equivale_ao_calculo_integral(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    conteudo = bytes(range(256)) * 50
    arquivo = tmp_path / "grande.bin"
    arquivo.write_bytes(conteudo)
    monkeypatch.setattr(calculator, "CHUNK_SIZE", 7)

    resultado = calculate_sha256(arquivo)

    assert resultado.sha256 == hashlib.sha256(conteudo).hexdigest()
    assert resultado.size == len(conteudo)


def test_tu_hash_008_arquivo_inexistente_gera_erro_tratado(tmp_path: Path) -> None:
    with pytest.raises(InvalidInputError, match="não encontrado"):
        calculate_sha256(tmp_path / "nao_existe.bin")


def test_diretorio_e_recusado(tmp_path: Path) -> None:
    with pytest.raises(InvalidInputError):
        calculate_sha256(tmp_path)


@pytest.mark.skipif(sys.platform == "win32", reason="criar links simbólicos exige privilégio no Windows")
def test_link_simbolico_nao_e_seguido(tmp_path: Path) -> None:
    alvo = tmp_path / "alvo.txt"
    alvo.write_bytes(b"abc")
    link = tmp_path / "link.txt"
    link.symlink_to(alvo)

    with pytest.raises(InvalidInputError, match="Links simbólicos"):
        calculate_sha256(link)