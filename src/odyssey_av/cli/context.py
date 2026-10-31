"""Contexto compartilhado entre a callback principal e os comandos."""

from __future__ import annotations

from dataclasses import dataclass

from odyssey_av.application.services.recovery_service import Session
from odyssey_av.shared.config.loader import AppConfig


@dataclass(frozen=True)
class AppContext:
    """Configuração efetiva e sessão do histórico, disponíveis a todos os comandos."""

    config: AppConfig
    session: Session | None