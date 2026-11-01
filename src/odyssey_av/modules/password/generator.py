"""Geração de senhas com fonte criptográfica (RF-013, RF-014, RN-005)."""

from __future__ import annotations

import secrets
import string
from dataclasses import dataclass

from odyssey_av.shared.errors.handlers import InvalidInputError

DEFAULT_LENGTH = 16
MIN_LENGTH = 8  # provisório, sujeito à revisão em D-03
MAX_LENGTH = 128  # provisório, sujeito à revisão em D-03

LOWERCASE = string.ascii_lowercase
UPPERCASE = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = string.punctuation

_ALPHABETS = {
    "lower": LOWERCASE,
    "upper": UPPERCASE,
    "digits": DIGITS,
    "symbols": SYMBOLS,
}

SET_LABELS = {
    "lower": "minúsculas",
    "upper": "maiúsculas",
    "digits": "dígitos",
    "symbols": "símbolos",
}


@dataclass(frozen=True)
class GenerationOptions:
    length: int = DEFAULT_LENGTH
    upper: bool = True
    digits: bool = True
    symbols: bool = True

    @property
    def set_names(self) -> tuple[str, ...]:
        """Conjuntos habilitados. Minúsculas são sempre incluídas."""
        names = ["lower"]
        if self.upper:
            names.append("upper")
        if self.digits:
            names.append("digits")
        if self.symbols:
            names.append("symbols")
        return tuple(names)


def validate_options(options: GenerationOptions) -> None:
    if not MIN_LENGTH <= options.length <= MAX_LENGTH:
        raise InvalidInputError(
            f"Comprimento inválido: informe um valor entre {MIN_LENGTH} e {MAX_LENGTH}."
        )


def create_password(options: GenerationOptions) -> str:
    """Gera a senha. Cada conjunto habilitado aparece pelo menos uma vez."""
    validate_options(options)

    names = options.set_names
    alphabet = "".join(_ALPHABETS[name] for name in names)

    chars = [secrets.choice(_ALPHABETS[name]) for name in names]
    chars += [secrets.choice(alphabet) for _ in range(options.length - len(chars))]
    secrets.SystemRandom().shuffle(chars)

    return "".join(chars)