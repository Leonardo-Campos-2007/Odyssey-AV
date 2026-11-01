"""Testes do avaliador de senha (TU-PASS-003, TU-PASS-004, TU-PASS-008)."""

from __future__ import annotations

import pytest

from odyssey_av.modules.password.evaluator import (
    Strength,
    _has_repetition,
    assess_password,
)
from odyssey_av.shared.errors.handlers import InvalidInputError
from odyssey_av.modules.password.evaluator import PasswordAssessment


def test_tu_pass_003_senha_vazia_e_rejeitada() -> None:
    with pytest.raises(InvalidInputError, match="vazia"):
        assess_password("")


@pytest.mark.parametrize(
    ("password", "esperado"),
    [
        ("abc", Strength.MUITO_FRACA),
        ("aaaaaaaaaaaaaaaa", Strength.MUITO_FRACA),
        ("Senha123", Strength.FRACA),
        ("correct-horse-battery", Strength.RAZOAVEL),
        ("Xk9#mPq", Strength.RAZOAVEL),
        ("Xk9#mPq2", Strength.FORTE),
        ("Tr0ub4dor&3", Strength.FORTE),
        ("Tr0ub4dor&3xKcd", Strength.FORTE),
    ],
)
def test_tu_pass_004_classificacao_coerente(password: str, esperado: Strength) -> None:
    assert assess_password(password).strength is esperado


@pytest.mark.parametrize(
    ("password", "esperado"),
    [("xyz", True), ("cba", True), ("aaa", True), ("a1b2c3", False)],
)
def test_detecta_repeticoes_e_sequencias(password: str, esperado: bool) -> None:
    assert _has_repetition(password) is esperado


def test_indicadores_nao_contem_a_senha() -> None:
    """TU-PASS-008: o resultado da avaliação não carrega o valor avaliado."""
    assert "password" not in PasswordAssessment.__dataclass_fields__
    assessment = assess_password("Tr0ub4dor&3")

    assert "Tr0ub4dor&3" not in repr(assessment)