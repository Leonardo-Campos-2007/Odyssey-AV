"""Abertura segura de arquivos regulares para leitura (SEGURANCA.md, seção 4.8).

Ordem das verificações:
1. lstat: rejeita links simbólicos e qualquer tipo que não seja arquivo regular,
   antes de abrir. Abrir um FIFO ou dispositivo pode bloquear o processo.
2. open somente leitura, com O_NOFOLLOW quando a plataforma oferece.
3. fstat no descritor aberto: confirma o tipo real do alvo aberto.
"""

from __future__ import annotations

import errno
import os
import stat
from dataclasses import dataclass
from pathlib import Path

from odyssey_av.shared.errors.handlers import InvalidInputError

_O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_O_BINARY = getattr(os, "O_BINARY", 0)

NOT_REGULAR_MESSAGE = "Somente arquivos regulares podem ser analisados."
SYMLINK_MESSAGE = "Links simbólicos não são seguidos automaticamente."


@dataclass(frozen=True)
class OpenedFile:
    fd: int
    size: int


def open_regular_file(path: Path) -> OpenedFile:
    """Abre o arquivo somente para leitura. O descritor deve ser fechado pelo chamador."""
    try:
        link_info = os.lstat(path)
    except FileNotFoundError as exc:
        raise InvalidInputError("Arquivo não encontrado.") from exc
    except OSError as exc:
        raise InvalidInputError("Não foi possível acessar o caminho informado.") from exc

    if stat.S_ISLNK(link_info.st_mode):
        raise InvalidInputError(SYMLINK_MESSAGE)
    if not stat.S_ISREG(link_info.st_mode):
        raise InvalidInputError(NOT_REGULAR_MESSAGE)

    try:
        fd = os.open(path, os.O_RDONLY | _O_NOFOLLOW | _O_BINARY)
    except FileNotFoundError as exc:
        raise InvalidInputError("Arquivo não encontrado.") from exc
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise InvalidInputError(SYMLINK_MESSAGE) from exc
        raise InvalidInputError(
            "Não foi possível abrir o arquivo. Verifique o caminho e as permissões."
        ) from exc

    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise InvalidInputError(NOT_REGULAR_MESSAGE)
    except BaseException:
        os.close(fd)
        raise

    return OpenedFile(fd=fd, size=info.st_size)