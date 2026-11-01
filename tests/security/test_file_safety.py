"""Testes de segurança contra alteração e exclusão de arquivos (SEGURANCA.md, seção 4.8).

ST-026: operações de leitura não alteram o arquivo analisado.
ST-027: o pacote de análise não contém chamadas de exclusão nem de escrita.
ST-028: caminhos do diretório de dados do aplicativo são recusados.
"""

from __future__ import annotations

import ast
import hashlib
import sys
from pathlib import Path

import pytest

import odyssey_av.modules
from odyssey_av.modules.hash.calculator import calculate_sha256
from odyssey_av.shared.errors.handlers import InvalidInputError
from odyssey_av.shared.validation.validators import ensure_outside_protected_dirs

pytestmark = pytest.mark.security

MODULES_DIR = Path(odyssey_av.modules.__file__).parent


# --- ST-026: leitura não altera o arquivo -----------------------------------

# Operações de leitura cobertas. Ao criar analyze_file, incluí-la aqui.
READ_ONLY_OPERATIONS = {
    "hash calculate": calculate_sha256,
}


def _impressao_digital(caminho: Path) -> tuple[str, int, int]:
    """Conteúdo, tamanho e data de modificação. O atime não é comparado (limitação)."""
    conteudo = caminho.read_bytes()
    info = caminho.stat()
    return hashlib.sha256(conteudo).hexdigest(), info.st_size, info.st_mtime_ns


@pytest.fixture
def amostra(tmp_path: Path) -> Path:
    caminho = tmp_path / "amostra.bin"
    caminho.write_bytes(bytes(range(256)) * 512)
    return caminho


@pytest.mark.parametrize("operacao", list(READ_ONLY_OPERATIONS))
def test_st_026_operacao_de_leitura_nao_altera_o_arquivo(amostra: Path, operacao: str) -> None:
    antes = _impressao_digital(amostra)

    READ_ONLY_OPERATIONS[operacao](amostra)

    assert _impressao_digital(amostra) == antes


def test_st_026_canario_detecta_escrita_real(amostra: Path) -> None:
    """Prova que a impressão digital percebe uma alteração de verdade."""
    antes = _impressao_digital(amostra)

    with amostra.open("ab") as handle:
        handle.write(b"x")

    assert _impressao_digital(amostra) != antes


# --- ST-027: verificação estática do pacote de análise ----------------------

_REMOCAO_NOMES = {"unlink", "rmdir", "removedirs", "rmtree"}
_ESCRITA_ATRIBUTOS = {"write_text", "write_bytes", "truncate", "touch", "rename"}
_FLAGS_DE_ESCRITA = {"O_WRONLY", "O_RDWR", "O_CREAT", "O_TRUNC", "O_APPEND"}
_CARACTERES_DE_ESCRITA = set("wax+")


def find_violations(source: str, origem: str = "<trecho>") -> list[str]:
    """Localiza chamadas de exclusão e de escrita no código-fonte.

    Limitações: modos e flags são verificados quando literais. Modo não literal
    é reportado para revisão manual. Flags em variáveis não são analisadas.
    """
    violacoes: list[str] = []
    for no in ast.walk(ast.parse(source, filename=origem)):
        if not isinstance(no, ast.Call):
            continue
        local = f"{origem}:{no.lineno}"
        func = no.func

        if isinstance(func, ast.Name):
            if func.id in _REMOCAO_NOMES:
                violacoes.append(f"{local}: remoção ({func.id})")
            elif func.id == "open":
                _verificar_modo(no, 1, local, violacoes)
            continue

        if not isinstance(func, ast.Attribute):
            continue
        receptor = func.value.id if isinstance(func.value, ast.Name) else None
        atributo = func.attr

        if atributo in _REMOCAO_NOMES or (atributo == "remove" and receptor == "os"):
            violacoes.append(f"{local}: remoção ({atributo})")
        elif atributo in _ESCRITA_ATRIBUTOS:
            violacoes.append(f"{local}: escrita ({atributo})")
        elif atributo == "open" and receptor == "os":
            _verificar_flags(no, local, violacoes)
        elif atributo == "open" and receptor == "io":
            _verificar_modo(no, 1, local, violacoes)
        elif atributo == "open":
            _verificar_modo(no, 0, local, violacoes)  # Path.open(mode)
        elif atributo == "fdopen":
            _verificar_modo(no, 1, local, violacoes)
    return violacoes


def _verificar_modo(no: ast.Call, posicao: int, local: str, violacoes: list[str]) -> None:
    modo = next((k.value for k in no.keywords if k.arg == "mode"), None)
    if modo is None and len(no.args) > posicao:
        modo = no.args[posicao]
    if modo is None:
        return  # modo padrão "r"
    if not (isinstance(modo, ast.Constant) and isinstance(modo.value, str)):
        violacoes.append(f"{local}: modo não literal, requer revisão")
    elif _CARACTERES_DE_ESCRITA & set(modo.value):
        violacoes.append(f"{local}: modo de escrita '{modo.value}'")


def _verificar_flags(no: ast.Call, local: str, violacoes: list[str]) -> None:
    flags = next((k.value for k in no.keywords if k.arg == "flags"), None)
    if flags is None and len(no.args) > 1:
        flags = no.args[1]
    if flags is None:
        return
    proibidas = sorted(_nomes_em(flags) & _FLAGS_DE_ESCRITA)
    if proibidas:
        violacoes.append(f"{local}: flags de escrita {', '.join(proibidas)}")


def _nomes_em(no: ast.AST) -> set[str]:
    nomes: set[str] = set()
    for sub in ast.walk(no):
        if isinstance(sub, ast.Name):
            nomes.add(sub.id)
        elif isinstance(sub, ast.Attribute):
            nomes.add(sub.attr)
    return nomes


_DETECTA = [
    "import os\nos.remove('a.bin')",
    "import shutil\nshutil.rmtree('pasta')",
    "from pathlib import Path\nPath('a.bin').unlink()",
    "open('a.bin', 'w')",
    "open('a.bin', mode='ab')",
    "open('a.bin', variavel)",
    "from pathlib import Path\nPath('a.bin').open('w')",
    "from pathlib import Path\nPath('a.bin').write_bytes(b'x')",
    "import os\nos.open('a.bin', os.O_WRONLY | os.O_CREAT)",
    "import os\nos.fdopen(fd, 'r+b')",
]

_NAO_DETECTA = [
    "open('a.bin', 'rb')",
    "open('a.bin')",
    "import os\nos.open('a.bin', os.O_RDONLY | os.O_NOFOLLOW)",
    "import os\nos.fdopen(fd, 'rb')",
    "lista.remove(1)",
    "texto.replace('a', 'b')",
]


@pytest.mark.parametrize("trecho", _DETECTA)
def test_st_027_verificador_detecta_operacoes_proibidas(trecho: str) -> None:
    assert find_violations(trecho), "O verificador deveria ter encontrado a operação."


@pytest.mark.parametrize("trecho", _NAO_DETECTA)
def test_st_027_verificador_aceita_operacoes_de_leitura(trecho: str) -> None:
    assert find_violations(trecho) == []


def test_st_027_pacote_de_analise_sem_escrita_ou_exclusao() -> None:
    violacoes: list[str] = []
    for arquivo in sorted(MODULES_DIR.rglob("*.py")):
        violacoes.extend(find_violations(arquivo.read_text(encoding="utf-8"), str(arquivo)))
    assert violacoes == [], "\n".join(violacoes)


# --- ST-028: caminhos do diretório de dados são recusados -------------------

@pytest.fixture
def diretorio_de_dados(tmp_path: Path) -> Path:
    diretorio = tmp_path / "odyssey-av"
    diretorio.mkdir()
    (diretorio / "history.db").write_bytes(b"SQLite format 3\x00")
    (diretorio / "instance.lock").write_bytes(b"")
    return diretorio


def test_st_028_banco_de_historico_e_recusado(diretorio_de_dados: Path) -> None:
    with pytest.raises(InvalidInputError):
        ensure_outside_protected_dirs(diretorio_de_dados / "history.db", [diretorio_de_dados])


def test_st_028_arquivo_de_bloqueio_e_recusado(diretorio_de_dados: Path) -> None:
    with pytest.raises(InvalidInputError):
        ensure_outside_protected_dirs(diretorio_de_dados / "instance.lock", [diretorio_de_dados])


def test_st_028_proprio_diretorio_de_dados_e_recusado(diretorio_de_dados: Path) -> None:
    with pytest.raises(InvalidInputError):
        ensure_outside_protected_dirs(diretorio_de_dados, [diretorio_de_dados])


def test_st_028_arquivo_fora_do_diretorio_e_permitido(
    tmp_path: Path, diretorio_de_dados: Path
) -> None:
    arquivo = tmp_path / "amostra.bin"
    arquivo.write_bytes(b"conteudo")

    ensure_outside_protected_dirs(arquivo, [diretorio_de_dados])


def test_st_028_prefixo_parecido_nao_e_confundido(
    tmp_path: Path, diretorio_de_dados: Path
) -> None:
    irmao = tmp_path / "odyssey-av-backup"
    irmao.mkdir()
    arquivo = irmao / "amostra.bin"
    arquivo.write_bytes(b"conteudo")

    ensure_outside_protected_dirs(arquivo, [diretorio_de_dados])


@pytest.mark.skipif(sys.platform == "win32", reason="criar links simbólicos exige privilégio no Windows")
def test_st_028_link_para_o_banco_e_recusado(tmp_path: Path, diretorio_de_dados: Path) -> None:
    atalho = tmp_path / "atalho.db"
    atalho.symlink_to(diretorio_de_dados / "history.db")

    with pytest.raises(InvalidInputError):
        ensure_outside_protected_dirs(atalho, [diretorio_de_dados])