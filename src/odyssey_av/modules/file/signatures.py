"""Assinaturas dos formatos suportados e mapa de extensões (RF-002, D-17, D-18)."""

from __future__ import annotations

from enum import StrEnum


class FileFormat(StrEnum):
    PE = "PE"
    ELF = "ELF"
    PDF = "PDF"
    PNG = "PNG"
    JPEG = "JPEG"
    ZIP = "ZIP"
    GZIP = "GZIP"
    UNKNOWN = "UNKNOWN"


FORMAT_LABELS: dict[FileFormat, str] = {
    FileFormat.PE: "PE (executável Windows)",
    FileFormat.ELF: "ELF (executável Linux)",
    FileFormat.PDF: "PDF",
    FileFormat.PNG: "PNG",
    FileFormat.JPEG: "JPEG",
    FileFormat.ZIP: "ZIP",
    FileFormat.GZIP: "GZIP",
    FileFormat.UNKNOWN: "desconhecido",
}

# Limites provisórios, sujeitos à revisão em D-03.
HEADER_READ_LIMIT = 4096
PE_OFFSET_FIELD = 0x3C
PE_OFFSET_LIMIT = 0x10000

MZ_MAGIC = b"MZ"
PE_SIGNATURE = b"PE\x00\x00"

_SIGNATURES: tuple[tuple[bytes, FileFormat], ...] = (
    (b"\x7fELF", FileFormat.ELF),
    (b"%PDF-", FileFormat.PDF),
    (b"\x89PNG\r\n\x1a\n", FileFormat.PNG),
    (b"\xff\xd8\xff", FileFormat.JPEG),
    (b"PK\x03\x04", FileFormat.ZIP),
    (b"PK\x05\x06", FileFormat.ZIP),
    (b"\x1f\x8b", FileFormat.GZIP),
)

# Extensões com família conhecida. Extensão fora desta lista não gera divergência (D-18).
EXTENSION_FAMILIES: dict[str, FileFormat] = {
    ".exe": FileFormat.PE,
    ".dll": FileFormat.PE,
    ".sys": FileFormat.PE,
    ".scr": FileFormat.PE,
    ".so": FileFormat.ELF,
    ".o": FileFormat.ELF,
    ".elf": FileFormat.ELF,
    ".pdf": FileFormat.PDF,
    ".png": FileFormat.PNG,
    ".jpg": FileFormat.JPEG,
    ".jpeg": FileFormat.JPEG,
    ".zip": FileFormat.ZIP,
    ".jar": FileFormat.ZIP,
    ".docx": FileFormat.ZIP,
    ".xlsx": FileFormat.ZIP,
    ".pptx": FileFormat.ZIP,
    ".gz": FileFormat.GZIP,
    ".tgz": FileFormat.GZIP,
}


def match_signature(header: bytes) -> FileFormat:
    """Identifica o formato pelo início do arquivo. MZ é tratado pelo analisador."""
    for magic, fmt in _SIGNATURES:
        if header.startswith(magic):
            return fmt
    return FileFormat.UNKNOWN


def pe_offset(header: bytes) -> int | None:
    """Lê o offset do cabeçalho PE (campo e_lfanew, em 0x3C)."""
    if len(header) < PE_OFFSET_FIELD + 4:
        return None
    return int.from_bytes(header[PE_OFFSET_FIELD:PE_OFFSET_FIELD + 4], "little")