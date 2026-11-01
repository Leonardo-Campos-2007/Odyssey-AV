"""Validações reutilizáveis de caminhos (SEGURANCA.md, seção 4.8; RN-001)."""

from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path

from odyssey_av.shared.errors.handlers import InvalidInputError

PROTECTED_PATH_MESSAGE = (
    "Este caminho pertence aos dados internos do Odyssey AV e não pode ser analisado."
)


def ensure_outside_protected_dirs(path: Path, protected_dirs: Iterable[Path]) -> None:
    """Recusa caminhos localizados dentro de qualquer diretório protegido.

    O caminho é resolvido antes da comparação, então um link simbólico apontando
    para dentro do diretório protegido também é recusado. A comparação ignora
    diferenças de maiúsculas no Windows e não confunde prefixos parecidos, como
    `odyssey-av` e `odyssey-av-backup`.

    Esta função é genérica: quem chama informa os diretórios protegidos. O caso
    de uso do FILE passará o diretório de dados obtido da infraestrutura.
    """
    target = _comparable(path)
    for directory in protected_dirs:
        if target.is_relative_to(_comparable(directory)):
            raise InvalidInputError(PROTECTED_PATH_MESSAGE)


def _comparable(path: Path) -> Path:
    return Path(os.path.normcase(str(path.resolve())))