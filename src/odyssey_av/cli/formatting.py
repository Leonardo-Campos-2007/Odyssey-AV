"""Formatação compartilhada pelos comandos da CLI."""

from __future__ import annotations

from odyssey_av.application.services.execution_service import PersistenceState


def history_label(persistence: PersistenceState, run_id: str | None) -> str:
    if persistence is PersistenceState.CONFIRMED:
        return f"registrado (ID {run_id})"
    if persistence is PersistenceState.FAILED:
        return "não registrado: falha de gravação"
    return "não registrado: histórico indisponível nesta sessão"