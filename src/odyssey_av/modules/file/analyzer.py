"""Análise estrutural de arquivos (RF-001 a RF-004, RF-029; D-17 a D-19).

A leitura é restrita ao cabeçalho e feita somente para leitura. O conteúdo nunca é
executado, modificado ou excluído (SEGURANCA.md, seção 4.8). Os indicadores são
sinais de atenção, não confirmação de segurança (RN-003).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO

from odyssey_av.infrastructure.filesystem.safe_open import open_regular_file
from odyssey_av.modules.file.signatures import (
    EXTENSION_FAMILIES,
    FORMAT_LABELS,
    HEADER_READ_LIMIT,
    MZ_MAGIC,
    PE_OFFSET_LIMIT,
    PE_SIGNATURE,
    FileFormat,
    match_signature,
    pe_offset,
)
from odyssey_av.shared.errors.handlers import OdysseyError

ALTERED_MESSAGE = "O arquivo foi alterado durante a leitura."


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


@dataclass(frozen=True)
class FileAnalysis:
    name: str
    extension: str
    size: int
    detected_format: FileFormat
    expected_format: FileFormat | None
    findings: tuple[Finding, ...]

    @property
    def diverges(self) -> bool:
        return any(finding.code == "EXTENSION_MISMATCH" for finding in self.findings)

    def to_record(self) -> dict[str, Any]:
        """Dados persistíveis (D-19): sem o nome do arquivo."""
        return {
            "extension": self.extension,
            "size": self.size,
            "detected_format": self.detected_format.value,
            "expected_format": self.expected_format.value if self.expected_format else None,
            "diverges": self.diverges,
            "findings": [finding.code for finding in self.findings],
        }


def analyze_file(path: Path) -> FileAnalysis:
    """Identifica o formato pelo cabeçalho e compara com a extensão. Não executa nem altera o arquivo."""
    opened = open_regular_file(path)

    with os.fdopen(opened.fd, "rb") as handle:
        expected_bytes = min(opened.size, HEADER_READ_LIMIT)
        header = handle.read(HEADER_READ_LIMIT)
        if len(header) < expected_bytes:
            raise OdysseyError(ALTERED_MESSAGE)
        detected, findings = _identify(handle, header, opened.size)

    extension = path.suffix.lower()
    expected = EXTENSION_FAMILIES.get(extension)
    if expected is not None and detected is not expected:
        findings.append(_mismatch(extension, expected, detected))

    return FileAnalysis(
        name=path.name,
        extension=extension,
        size=opened.size,
        detected_format=detected,
        expected_format=expected,
        findings=tuple(findings),
    )


def _identify(handle: BinaryIO, header: bytes, size: int) -> tuple[FileFormat, list[Finding]]:
    if header.startswith(MZ_MAGIC):
        if _has_pe_signature(handle, header, size):
            return FileFormat.PE, []
        return FileFormat.UNKNOWN, [
            Finding("INCOMPLETE_PE_HEADER", "Cabeçalho MZ sem assinatura PE válida.")
        ]
    return match_signature(header), []


def _has_pe_signature(handle: BinaryIO, header: bytes, size: int) -> bool:
    offset = pe_offset(header)
    if offset is None or offset > PE_OFFSET_LIMIT or offset + len(PE_SIGNATURE) > size:
        return False
    handle.seek(offset)
    return handle.read(len(PE_SIGNATURE)) == PE_SIGNATURE


def _mismatch(extension: str, expected: FileFormat, detected: FileFormat) -> Finding:
    return Finding(
        "EXTENSION_MISMATCH",
        f"A extensão {extension} indica {FORMAT_LABELS[expected]}, "
        f"mas o formato identificado é {FORMAT_LABELS[detected]}.",
    )