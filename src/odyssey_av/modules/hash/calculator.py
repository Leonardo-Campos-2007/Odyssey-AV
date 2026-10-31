"""Cálculo e comparação de SHA-256 em blocos (RF-005 a RF-008, RN-002, RN-004)."""

from __future__ import annotations

import errno
import hashlib
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path

from odyssey_av.domain.enums import ComparisonStatus
from odyssey_av.shared.errors.handlers import InvalidInputError, OdysseyError

# Tamanho do bloco de leitura. O limite operacional definitivo ainda está pendente (RNF-015).
CHUNK_SIZE = 1024 * 1024

_SHA256_PATTERN = re.compile(r"[0-9a-fA-F]{64}")
_O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_O_BINARY = getattr(os, "O_BINARY", 0)


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
    dispositivos, sockets, pipes e links simbólicos são recusados.
    """
    normalized = _normalize_reference(reference)
    fd = _open_for_reading(path)

    digest = hashlib.sha256()
    size = 0
    with os.fdopen(fd, "rb") as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise InvalidInputError("Somente arquivos regulares podem ser analisados.")

        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
            size += len(chunk)

    if size != info.st_size:
        raise OdysseyError("O arquivo foi alterado durante a leitura.")

    sha256 = digest.hexdigest()
    return HashResult(
        path=path,
        sha256=sha256,
        size=size,
        comparison=_compare(sha256, normalized),
        reference=normalized,
    )


def _open_for_reading(path: Path) -> int:
    try:
        return os.open(path, os.O_RDONLY | _O_NOFOLLOW | _O_BINARY)
    except FileNotFoundError as exc:
        raise InvalidInputError("Arquivo não encontrado.") from exc
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise InvalidInputError("Links simbólicos não são seguidos automaticamente.") from exc
        raise InvalidInputError(
            "Não foi possível abrir o arquivo. Verifique o caminho e as permissões."
        ) from exc


def _normalize_reference(reference: str | None) -> str | None:
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