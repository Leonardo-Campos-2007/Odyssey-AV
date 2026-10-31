"""Resultado da comparação entre o hash calculado e uma referência (RN-004)."""

from enum import StrEnum


class ComparisonStatus(StrEnum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    NO_REFERENCE = "NO_REFERENCE"