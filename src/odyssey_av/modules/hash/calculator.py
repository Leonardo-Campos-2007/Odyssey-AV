"""Cálculo e comparação de SHA-256 em blocos (RF-005 a RF-008, RN-002, RN-004).

A abertura do arquivo usa o módulo compartilhado de abertura segura, que verifica
o tipo com lstat antes de abrir e com fstat no descritor aberto (SEGURANCA.md, 4.8).
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path

from odyssey_av.domain.enums import ComparisonStatus
from odyssey_av.infrastructure.filesystem.safe_open import open_regular_file
from odyssey_av.shared.errors.handlers import InvalidInputError, OdysseyError

# Tamanho do bloco de leitura. O limite operacional definitivo ainda está pendente (RNF-015).
CHUNK_SIZE = 1024 * 1024

_SHA256_PATTERN = re.compile(r"[0-9a-fA-F]{64}")
ALTERED_MESSAGE = "O arquivo foi alterado durante a leitura."


@dataclass(frozen=True)
class HashResult:
    path: Path
    sha256: str
    size: int
    comparison: ComparisonStatus
    reference: str | None = None


def calculate_sha256(path: Path, reference: str | None = None) -> HashResult:
    """Calcula o SHA-256 dos bytes do arquivo e, se houver, compara com a referência.

    O arquivo é aberto somente para leitura e processado em blocos. Diretórios,
    dispositivos, sockets, pipes e links simbólicos são recusados antes da abertura.
    """
    normalized = normalize_reference(reference)
    opened = open_regular_file(path)

    digest = hashlib.sha256()
    size = 0
    with os.fdopen(opened.fd, "rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
            size += len(chunk)

    if size != opened.size:
        raise OdysseyError(ALTERED_MESSAGE)

    sha256 = digest.hexdigest()
    return HashResult(
        path=path,
        sha256=sha256,
        size=size,
        comparison=_compare(sha256, normalized),
        reference=normalized,
    )


def normalize_reference(reference: str | None) -> str | None:
    if reference is None:
        return None
    value = reference.strip()
    if not _SHA256_PATTERN.fullmatch(value):
        raise InvalidInputError(
            "Referência SHA-256 inválida: são esperados 64 caracteres hexadecimais."
        )
    return value.lower()


def _compare(sha256: str, reference: str | None) -> ComparisonStatus:
    if reference is None:
        return ComparisonStatus.NO_REFERENCE
    return ComparisonStatus.MATCH if sha256 == reference else ComparisonStatus.MISMATCH