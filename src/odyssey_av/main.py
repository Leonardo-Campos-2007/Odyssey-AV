"""Ponto de entrada do Odyssey AV."""

from odyssey_av.cli.app import app
from odyssey_av.shared.errors.handlers import OdysseyError, report_error


def main() -> None:
    """Executa a CLI e converte erros em mensagens seguras e códigos de saída."""
    try:
        app()
    except OdysseyError as error:
        raise SystemExit(report_error(error)) from None
    except Exception as error:
        raise SystemExit(report_error(error)) from None


if __name__ == "__main__":
    main()