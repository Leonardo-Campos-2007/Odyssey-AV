"""Testes do gerador de senhas (TU-PASS-001, 002, 005)."""

from __future__ import annotations

import secrets

import pytest

from odyssey_av.modules.password.generator import (
    DEFAULT_LENGTH,
    DIGITS,
    LOWERCASE,
    MAX_LENGTH,
    MIN_LENGTH,
    SYMBOLS,
    UPPERCASE,
    GenerationOptions,
    create_password,
    validate_options,
)
from odyssey_av.shared.errors.handlers import InvalidInputError


def test_tu_pass_001_comprimento_padrao() -> None:
    assert len(create_password(GenerationOptions())) == DEFAULT_LENGTH


def test_tu_pass_001_comprimento_configuravel() -> None:
    assert len(create_password(GenerationOptions(length=32))) == 32


@pytest.mark.parametrize("length", [MIN_LENGTH - 1, MAX_LENGTH + 1])
def test_tu_pass_002_comprimento_fora_do_intervalo_e_rejeitado(length: int) -> None:
    with pytest.raises(InvalidInputError):
        validate_options(GenerationOptions(length=length))


@pytest.mark.parametrize("length", [MIN_LENGTH, MAX_LENGTH])
def test_limites_do_intervalo_sao_aceitos(length: int) -> None:
    assert len(create_password(GenerationOptions(length=length))) == length


def test_todos_os_conjuntos_presentes_por_padrao() -> None:
    senha = create_password(GenerationOptions(length=16))

    assert any(c in LOWERCASE for c in senha)
    assert any(c in UPPERCASE for c in senha)
    assert any(c in DIGITS for c in senha)
    assert any(c in SYMBOLS for c in senha)


def test_no_upper_remove_maiusculas() -> None:
    senha = create_password(GenerationOptions(length=128, upper=False))

    assert not any(c in UPPERCASE for c in senha)


def test_no_digits_remove_digitos() -> None:
    senha = create_password(GenerationOptions(length=128, digits=False))

    assert not any(c in DIGITS for c in senha)


def test_no_symbols_remove_simbolos() -> None:
    senha = create_password(GenerationOptions(length=128, symbols=False))

    assert not any(c in SYMBOLS for c in senha)


def test_apenas_minusculas_quando_todos_os_conjuntos_sao_removidos() -> None:
    senha = create_password(GenerationOptions(length=32, upper=False, digits=False, symbols=False))

    assert set(senha) <= set(LOWERCASE)


def test_duas_geracoes_produzem_senhas_diferentes() -> None:
    assert create_password(GenerationOptions()) != create_password(GenerationOptions())


def test_tu_pass_005_geracao_usa_modulo_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    chamadas: list[object] = []
    original = secrets.choice

    def espiao(sequencia):
        chamadas.append(sequencia)
        return original(sequencia)

    monkeypatch.setattr(secrets, "choice", espiao)

    create_password(GenerationOptions(length=8))

    assert len(chamadas) >= 8