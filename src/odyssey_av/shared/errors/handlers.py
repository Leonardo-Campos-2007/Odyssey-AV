"""Erros da aplicação, códigos de saída e tratamento centralizado."""

from __future__ import annotations

import sys
from enum import IntEnum
from typing import TextIO


class ExitCode(IntEnum):
    """Códigos de saída definidos em API.md (seção 6)."""

    SUCCESS = 0
    FUNCTIONAL_FAILURE = 1
    INVALID_USAGE = 2
    HISTORY_NOT_PERSISTED = 3
    PARTIAL_RESULT = 4


class OdysseyError(Exception):
    """Base para erros esperados da aplicação.

    A mensagem deve ser segura para exibição: não pode conter senhas,
    conteúdo de arquivos nem outros dados sensíveis.
    """

    exit_code: ExitCode = ExitCode.FUNCTIONAL_FAILURE

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidInputError(OdysseyError):
    """Argumento ou entrada rejeitada antes da execução funcional."""

    exit_code = ExitCode.INVALID_USAGE


class ConfigurationError(OdysseyError):
    """Arquivo de configuração inválido ou valor incompatível."""

    exit_code = ExitCode.INVALID_USAGE


class InstanceLockedError(OdysseyError):
    """Outra instância do Odyssey AV já está ativa."""

    exit_code = ExitCode.FUNCTIONAL_FAILURE


def report_error(error: BaseException, stream: TextIO | None = None) -> ExitCode:
    """Exibe o erro de forma segura e retorna o código de saída.

    Erros esperados exibem sua mensagem. Erros inesperados exibem uma
    mensagem genérica, pois a mensagem de uma exceção não tratada pode
    conter dados sensíveis.
    """
    output = stream if stream is not None else sys.stderr

    if isinstance(error, OdysseyError):
        print(f"Erro: {error.message}", file=output)
        return error.exit_code

    print("Erro inesperado. A operação foi interrompida.", file=output)
    return ExitCode.FUNCTIONAL_FAILURE