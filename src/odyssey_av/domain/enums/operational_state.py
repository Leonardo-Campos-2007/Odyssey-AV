"""Estado operacional da aplicação, separado dos estados de execução."""

from enum import StrEnum


class OperationalState(StrEnum):
    NORMAL = "NORMAL"
    DEGRADED = "DEGRADED"