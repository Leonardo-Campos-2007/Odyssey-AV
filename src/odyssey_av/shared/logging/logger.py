"""Logger centralizado com sanitização de dados sensíveis."""

from __future__ import annotations

import logging
import re
import sys
from typing import TextIO

LOGGER_NAME = "odyssey_av"
REDACTED = "[REDACTED]"

# Padrões de chave=valor que indicam segredos (senhas, tokens, chaves).
_SECRET_PATTERN = re.compile(
    r"(?i)\b(password|senha|passwd|pwd|token|secret|segredo|api[_-]?key)\b(\s*[=:]\s*)(\S+)"
)


class SanitizingFilter(logging.Filter):
    """Remove segredos da mensagem final antes de sua emissão.

    Atua sobre a mensagem já formatada, cobrindo também argumentos
    passados via ``%s``.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        record.msg = _SECRET_PATTERN.sub(rf"\1\2{REDACTED}", message)
        record.args = ()
        return True


def get_logger(name: str | None = None) -> logging.Logger:
    """Retorna um logger filho do logger principal da aplicação."""
    if name is None:
        return logging.getLogger(LOGGER_NAME)
    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def configure_logging(level: str = "INFO", stream: TextIO | None = None) -> logging.Logger:
    """Configura o logger principal. Pode ser chamada mais de uma vez.

    Handlers anteriores são removidos, para evitar mensagens duplicadas.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level.upper())
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    handler = logging.StreamHandler(stream if stream is not None else sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )
    handler.addFilter(SanitizingFilter())
    logger.addHandler(handler)

    return logger