"""Padrões visuais da CLI: cores, símbolos e formatação dos exemplos.

Toda cor e símbolo da ajuda vem deste arquivo. Para mudar a aparência de toda a
CLI, altere somente os valores aqui.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Symbols:
    bullet: str
    square: str
    diamond: str
    circle: str
    triangle: str
    ok: str
    fail: str


def _supports_unicode() -> bool:
    encoding = (getattr(sys.stdout, "encoding", None) or "").lower()
    return encoding.startswith("utf")


if _supports_unicode():
    SYMBOLS = Symbols(
        bullet="▸", square="■", diamond="◆", circle="●", triangle="▲", ok="✔", fail="✖"
    )
else:
    # Terminais sem UTF-8 (por exemplo, cmd com página de código antiga) usam ASCII.
    SYMBOLS = Symbols(
        bullet=">", square="#", diamond="*", circle="o", triangle="^", ok="+", fail="x"
    )

# Estilos Rich. Use sempre estes nomes em [estilo]texto[/].
PRIMARY = "bold bright_cyan"
SUCCESS = "bold bright_green"
WARNING = "bold bright_yellow"
DANGER = "bold bright_red"
ACCENT = "bold bright_magenta"
MUTED = "dim"


def example(command: str, note: str = "") -> str:
    """Formata uma linha de exemplo para o epílogo da ajuda."""
    line = f"  [{PRIMARY}]{SYMBOLS.bullet}[/] [{SUCCESS}]{command}[/]"
    if note:
        line += f"  [{MUTED}]{SYMBOLS.circle} {note}[/]"
    return line