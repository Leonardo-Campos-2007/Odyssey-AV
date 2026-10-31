"""Módulos funcionais do Odyssey AV."""

from enum import StrEnum


class Module(StrEnum):
    FILE = "FILE"
    HASH = "HASH"
    NETWORK = "NETWORK"
    PASSWORD = "PASSWORD"
    URL = "URL"
    PROCESS = "PROCESS"
    HISTORY = "HISTORY"