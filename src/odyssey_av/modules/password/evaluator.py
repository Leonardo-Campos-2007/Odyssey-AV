"""Avaliação local de senha (RF-015, RN-005).

O resultado descreve a senha por indicadores e nunca a contém. Os critérios
seguem a proposta aprovada em D-14.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from odyssey_av.modules.password.generator import DIGITS, LOWERCASE, SYMBOLS, UPPERCASE
from odyssey_av.shared.errors.handlers import InvalidInputError


class Strength(StrEnum):
    MUITO_FRACA = "MUITO_FRACA"
    FRACA = "FRACA"
    RAZOAVEL = "RAZOAVEL"
    FORTE = "FORTE"


STRENGTH_LABELS = {
    Strength.MUITO_FRACA: "muito fraca",
    Strength.FRACA: "fraca",
    Strength.RAZOAVEL: "razoável",
    Strength.FORTE: "forte",
}

_CHARACTER_SETS = (
    ("lower", LOWERCASE),
    ("upper", UPPERCASE),
    ("digits", DIGITS),
    ("symbols", SYMBOLS),
)


@dataclass(frozen=True)
class PasswordAssessment:
    """Indicadores de uma senha. Não contém o valor avaliado."""

    length: int
    sets: tuple[str, ...]
    has_repetition: bool
    score: int
    strength: Strength


def assess_password(password: str) -> PasswordAssessment:
    """Avalia a senha. Pontuação: comprimento (0 a 2) + conjuntos (0 a 4) - repetição (1)."""
    if not password:
        raise InvalidInputError("A senha não pode estar vazia.")

    sets = tuple(
        name for name, alphabet in _CHARACTER_SETS if any(c in alphabet for c in password)
    )
    repetition = _has_repetition(password)
    score = max(_length_points(len(password)) + len(sets) - (1 if repetition else 0), 0)

    return PasswordAssessment(
        length=len(password),
        sets=sets,
        has_repetition=repetition,
        score=score,
        strength=_classify(score),
    )


def _length_points(length: int) -> int:
    if length < 8:
        return 0
    if length < 12:
        return 1
    return 2


def _classify(score: int) -> Strength:
    if score <= 2:
        return Strength.MUITO_FRACA
    if score == 3:
        return Strength.FRACA
    if score == 4:
        return Strength.RAZOAVEL
    return Strength.FORTE


def _has_repetition(password: str) -> bool:
    """Detecta três caracteres iguais seguidos ou sequências ASCII de três (abc, 321)."""
    text = password.lower()
    for i in range(len(text) - 2):
        first, second, third = text[i], text[i + 1], text[i + 2]
        if first == second == third:
            return True
        step = ord(second) - ord(first)
        if abs(step) == 1 and ord(third) - ord(second) == step:
            return True
    return False