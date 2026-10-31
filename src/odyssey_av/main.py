"""Ponto de entrada do Odyssey AV."""

from odyssey_av.application.services.instance_service import InstanceService
from odyssey_av.application.services.recovery_service import Session, start_session
from odyssey_av.cli.app import app
from odyssey_av.shared.errors.handlers import report_error


def main() -> None:
    """Mantém o bloqueio e a sessão durante toda a execução e os libera ao sair."""
    instance = InstanceService()
    session: Session | None = None

    try:
        instance.start()
        session = start_session(instance.instance_id)
        app(obj=session)
    except Exception as error:
        raise SystemExit(report_error(error)) from None
    finally:
        if session is not None:
            session.close()
        instance.stop()


if __name__ == "__main__":
    main()