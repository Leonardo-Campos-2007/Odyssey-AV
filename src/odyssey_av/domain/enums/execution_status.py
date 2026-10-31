"""Estados de uma execução funcional."""

from enum import StrEnum


class ExecutionStatus(StrEnum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    INTERRUPTED = "INTERRUPTED"