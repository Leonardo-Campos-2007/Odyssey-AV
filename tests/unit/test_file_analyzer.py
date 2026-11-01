"""Testes da análise de arquivos com cabeçalhos sintéticos (TU-FILE-001 a 020).

Os arquivos são criados em diretório temporário. Nenhum binário real é usado.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from odyssey_av.infrastructure.filesystem.safe_open import OpenedFile
from odyssey_av.modules.file import analyzer
from odyssey_av.modules.file.analyzer import analyze_file
from odyssey_av.modules.file.signatures import FileFormat
from odyssey_av.shared.errors.handlers import InvalidInputError, OdysseyError

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 24
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 60
PDF = b"%PDF-1.7\n" + b"x" * 40
ELF = b"\x7fELF\x02\x01\x01" + b"\x00" * 57
ZIP = b"PK\x03\x04" + b"\x00" * 60
GZIP = b"\x1f\x8b\x08\x00" + b"\x00" * 60
ALEATORIO = bytes(range(200, 256)) * 4


def _pe(e_lfanew: int = 0x80) -> bytes:
    dados = bytearray(0x100)
    dados[0:2] = b"MZ"
    dados[0x3C:0x40] = e_lfanew.to_bytes(4, "little")
    dados[e_lfanew:e_lfanew + 4] = b"PE\x00\x00"
    return bytes(dados)


def _arquivo(tmp_path: Path, nome: str, conteudo: bytes) -> Path:
    caminho = tmp_path / nome
    caminho.write_bytes(conteudo)
    return caminho


def _codigos(analise) -> set[str]:
    return {finding.code for finding in analise.findings}


def test_tu_file_001_metadados(tmp_path: Path) -> None:
    analise = analyze_file(_arquivo(tmp_path, "amostra.pdf", PDF))

    assert analise.name == "amostra.pdf"
    assert analise.extension == ".pdf"
    assert analise.size == len(PDF)


def test_tu_file_002_arquivo_inexistente(tmp_path: Path) -> None:
    with pytest.raises(InvalidInputError, match="não encontrado"):
        analyze_file(tmp_path / "nao_existe.bin")


def test_tu_file_003_caminho_vazio_e_rejeitado() -> None:
    with pytest.raises(InvalidInputError):
        analyze_file(Path(""))


def test_tu_file_004_extensao_incompativel_gera_divergencia(tmp_path: Path) -> None:
    analise = analyze_file(_arquivo(tmp_path, "falso.exe", PDF))

    assert analise.expected_format is FileFormat.PE
    assert analise.detected_format is FileFormat.PDF
    assert "EXTENSION_MISMATCH" in _codigos(analise)


def test_tu_file_005_formato_nao_suportado_nao_gera_divergencia(tmp_path: Path) -> None:
    analise = analyze_file(_arquivo(tmp_path, "dados.bin", ALEATORIO))

    assert analise.detected_format is FileFormat.UNKNOWN
    assert "EXTENSION_MISMATCH" not in _codigos(analise)


def test_tu_file_006_sem_permissao_e_erro_tratado(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    arquivo = _arquivo(tmp_path, "amostra.bin", ALEATORIO)

    def negar(*args, **kwargs):
        raise PermissionError(13, "Permissão negada")

    monkeypatch.setattr(os, "open", negar)

    with pytest.raises(InvalidInputError, match="Não foi possível abrir"):
        analyze_file(arquivo)


def test_tu_file_007_arquivo_vazio_e_resultado_valido(tmp_path: Path) -> None:
    analise = analyze_file(_arquivo(tmp_path, "vazio.bin", b""))

    assert analise.size == 0
    assert analise.detected_format is FileFormat.UNKNOWN
    assert analise.findings == ()


def test_tu_file_008_diretorio_e_recusado(tmp_path: Path) -> None:
    with pytest.raises(InvalidInputError, match="regulares"):
        analyze_file(tmp_path)


@pytest.mark.skipif(sys.platform == "win32", reason="criar links simbólicos exige privilégio no Windows")
def test_tu_file_009_link_simbolico_nao_e_seguido(tmp_path: Path) -> None:
    alvo = _arquivo(tmp_path, "alvo.pdf", PDF)
    link = tmp_path / "link.pdf"
    link.symlink_to(alvo)

    with pytest.raises(InvalidInputError, match="Links simbólicos"):
        analyze_file(link)


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO indisponível nesta plataforma")
def test_tu_file_010_fifo_e_recusado_antes_da_abertura(tmp_path: Path) -> None:
    fifo = tmp_path / "canal"
    os.mkfifo(fifo)

    # Se a rejeição ocorresse depois do open, este teste travaria à espera de escritor.
    with pytest.raises(InvalidInputError, match="regulares"):
        analyze_file(fifo)


def test_tu_file_011_alteracao_durante_leitura_e_detectada(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    arquivo = _arquivo(tmp_path, "amostra.bin", ALEATORIO)
    original = analyzer.open_regular_file

    def tamanho_inflado(caminho):
        aberto = original(caminho)
        return OpenedFile(fd=aberto.fd, size=aberto.size + 1000)

    monkeypatch.setattr(analyzer, "open_regular_file", tamanho_inflado)

    with pytest.raises(OdysseyError, match="alterado durante a leitura"):
        analyze_file(arquivo)


def test_tu_file_012_pe_com_offset_alem_do_fim_e_incompleto(tmp_path: Path) -> None:
    conteudo = _pe(e_lfanew=0x7E)[:0x80]

    analise = analyze_file(_arquivo(tmp_path, "incompleto.exe", conteudo))

    assert analise.detected_format is FileFormat.UNKNOWN
    assert "INCOMPLETE_PE_HEADER" in _codigos(analise)


@pytest.mark.parametrize(
    ("nome", "conteudo", "formato"),
    [
        ("amostra.exe", _pe(), FileFormat.PE),
        ("amostra.elf", ELF, FileFormat.ELF),
        ("amostra.pdf", PDF, FileFormat.PDF),
        ("amostra.png", PNG, FileFormat.PNG),
        ("amostra.jpg", JPEG, FileFormat.JPEG),
        ("amostra.zip", ZIP, FileFormat.ZIP),
        ("amostra.gz", GZIP, FileFormat.GZIP),
    ],
)
def test_tu_file_013_a_019_formato_identificado_sem_divergencia(
    tmp_path: Path, nome: str, conteudo: bytes, formato: FileFormat
) -> None:
    analise = analyze_file(_arquivo(tmp_path, nome, conteudo))

    assert analise.detected_format is formato
    assert analise.diverges is False


def test_tu_file_020_conteudo_desconhecido(tmp_path: Path) -> None:
    analise = analyze_file(_arquivo(tmp_path, "dados.xyz", ALEATORIO))

    assert analise.detected_format is FileFormat.UNKNOWN
    assert analise.findings == ()


def test_mz_sem_assinatura_pe_e_desconhecido(tmp_path: Path) -> None:
    analise = analyze_file(_arquivo(tmp_path, "falso.exe", b"MZ" + b"\x00" * 200))

    assert analise.detected_format is FileFormat.UNKNOWN
    assert {"INCOMPLETE_PE_HEADER", "EXTENSION_MISMATCH"} <= _codigos(analise)


def test_offset_pe_acima_do_limite_e_rejeitado(tmp_path: Path) -> None:
    offset = 0x20000
    dados = bytearray(offset + 8)
    dados[0:2] = b"MZ"
    dados[0x3C:0x40] = offset.to_bytes(4, "little")
    dados[offset:offset + 4] = b"PE\x00\x00"

    analise = analyze_file(_arquivo(tmp_path, "grande.exe", bytes(dados)))

    assert analise.detected_format is FileFormat.UNKNOWN


def test_zip_em_docx_nao_gera_divergencia(tmp_path: Path) -> None:
    analise = analyze_file(_arquivo(tmp_path, "relatorio.docx", ZIP))

    assert analise.detected_format is FileFormat.ZIP
    assert "EXTENSION_MISMATCH" not in _codigos(analise)


def test_pdf_com_conteudo_zip_gera_divergencia(tmp_path: Path) -> None:
    analise = analyze_file(_arquivo(tmp_path, "falso.pdf", ZIP))

    assert "EXTENSION_MISMATCH" in _codigos(analise)


def test_extensao_desconhecida_nao_gera_divergencia(tmp_path: Path) -> None:
    analise = analyze_file(_arquivo(tmp_path, "imagem.dat", PNG))

    assert analise.expected_format is None
    assert analise.detected_format is FileFormat.PNG
    assert analise.findings == ()


def test_extensao_maiuscula_e_normalizada(tmp_path: Path) -> None:
    analise = analyze_file(_arquivo(tmp_path, "AMOSTRA.EXE", PDF))

    assert analise.extension == ".exe"
    assert "EXTENSION_MISMATCH" in _codigos(analise)


def test_registro_nao_contem_o_nome(tmp_path: Path) -> None:
    analise = analyze_file(_arquivo(tmp_path, "minha_conta_bancaria.pdf", PDF))

    assert analise.name == "minha_conta_bancaria.pdf"
    assert "minha_conta_bancaria" not in json.dumps(analise.to_record())