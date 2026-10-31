"""Estados de um resultado individual produzido por uma execução."""

from enum import StrEnum


class ResultStatus(StrEnum):
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    INFO = "INFO"