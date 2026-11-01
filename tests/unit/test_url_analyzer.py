"""Testes da análise estrutural de URL (TU-URL-001 a 007)."""

from __future__ import annotations

import json
import socket
import urllib.request

import pytest

from odyssey_av.modules.url.analyzer import MAX_URL_LENGTH, analyze_url
from odyssey_av.shared.errors.handlers import InvalidInputError


def test_tu_url_001_decompoe_componentes() -> None:
    analise = analyze_url("https://Exemplo.COM:8443/caminho/x?a=1#frag")

    assert analise.scheme == "https"
    assert analise.host == "exemplo.com"
    assert analise.port == 8443
    assert analise.path == "/caminho/x"
    assert analise.has_query is True
    assert analise.has_fragment is True
    assert analise.normalized == "https://exemplo.com:8443/caminho/x?a=1#frag"


@pytest.mark.parametrize(
    "entrada",
    ["", "   ", "https://", "https://exemplo.com:99999/", "http://exemplo.com:abc/"],
)
def test_tu_url_002_entradas_invalidas_sao_rejeitadas(entrada: str) -> None:
    with pytest.raises(InvalidInputError):
        analyze_url(entrada)


@pytest.mark.parametrize("entrada", ["exemplo.com", "//exemplo.com/x"])
def test_tu_url_005_sem_esquema_e_rejeitada(entrada: str) -> None:
    with pytest.raises(InvalidInputError, match="esquema"):
        analyze_url(entrada)


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("HTTPS://Exemplo.com.:443/a/./b/../c/", "https://exemplo.com/a/c/"),
        ("http://exemplo.com:80", "http://exemplo.com/"),
        ("https://exemplo.com/a//b", "https://exemplo.com/a/b"),
        ("https://exemplo.com/../../x", "https://exemplo.com/x"),
    ],
)
def test_tu_url_003_normalizacao(entrada: str, esperado: str) -> None:
    assert analyze_url(entrada).normalized == esperado


@pytest.mark.parametrize(
    ("entrada", "codigo"),
    [
        ("http://192.168.0.1/", "IP_HOST"),
        ("http://[::1]/", "IP_HOST"),
        ("http://exemplo.com:8080/", "NON_DEFAULT_PORT"),
        ("ftp://exemplo.com/", "SCHEME_NOT_HTTP"),
        ("https://xn--exmplo-9ua.com/", "PUNYCODE_HOST"),
        ("https://p\u0430ypal.com/", "NON_ASCII_HOST"),
        ("https://a.b.c.d.exemplo.com/", "MANY_SUBDOMAINS"),
        ("https://a-b-c-d-e.com/", "MANY_HYPHENS"),
        ("https://usuario:senha@exemplo.com/", "CREDENTIALS_IN_URL"),
    ],
)
def test_tu_url_004_indicadores_de_atencao(entrada: str, codigo: str) -> None:
    codigos = {indicator.code for indicator in analyze_url(entrada).indicators}

    assert codigo in codigos


def test_url_sem_problemas_nao_gera_indicadores() -> None:
    assert analyze_url("https://exemplo.com/caminho").indicators == ()


def test_tu_url_006_caracteres_especiais_sao_preservados() -> None:
    analise = analyze_url("https://exemplo.com/caminho%20com%20espacos?q=a%26b&c=d+e#x%20y")

    assert analise.path == "/caminho%20com%20espacos"
    assert analise.normalized == (
        "https://exemplo.com/caminho%20com%20espacos?q=a%26b&c=d+e#x%20y"
    )


@pytest.mark.parametrize("entrada", ["https://exemplo.com/\x00", "https://exemplo.com/\tx"])
def test_tu_url_006_caracteres_de_controle_sao_rejeitados(entrada: str) -> None:
    with pytest.raises(InvalidInputError, match="controle"):
        analyze_url(entrada)


def test_tu_url_008_credenciais_nao_aparecem_no_resultado() -> None:
    analise = analyze_url("https://usuario:SenhaSecreta123@exemplo.com/?token=abc123")

    assert analise.has_credentials is True
    assert "SenhaSecreta123" not in analise.normalized
    assert "usuario" not in analise.normalized
    assert "SenhaSecreta123" not in json.dumps(analise.to_record())
    assert "abc123" not in json.dumps(analise.to_record())


def test_tu_url_007_analise_nao_faz_requisicoes(monkeypatch: pytest.MonkeyPatch) -> None:
    def proibido(*args, **kwargs):
        raise AssertionError("A análise de URL não deve acessar a rede.")

    monkeypatch.setattr(socket, "socket", proibido)
    monkeypatch.setattr(socket, "getaddrinfo", proibido)
    monkeypatch.setattr(socket, "gethostbyname", proibido)
    monkeypatch.setattr(urllib.request, "urlopen", proibido)

    analise = analyze_url("https://exemplo.com/")

    assert analise.host == "exemplo.com"


def test_url_acima_do_limite_e_rejeitada() -> None:
    with pytest.raises(InvalidInputError, match="muito longa"):
        analyze_url("https://exemplo.com/" + "a" * MAX_URL_LENGTH)


def test_ipv6_com_porta_e_normalizado() -> None:
    analise = analyze_url("http://[::1]:8080/")

    assert analise.host == "::1"
    assert analise.port == 8080
    assert analise.normalized == "http://[::1]:8080/"


def test_registro_contem_apenas_componentes() -> None:
    registro = analyze_url("https://exemplo.com:8443/a?x=1#f").to_record()

    assert set(registro) == {
        "scheme",
        "host",
        "port",
        "path",
        "has_query",
        "has_fragment",
        "has_credentials",
        "indicators",
    }
    assert registro["port"] == 8443
    assert "x=1" not in json.dumps(registro)