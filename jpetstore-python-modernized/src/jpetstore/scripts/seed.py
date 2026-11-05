"""CLI entry point for development seeding."""

from jpetstore.config import get_settings
from jpetstore.core.database import init_database, session_scope
from jpetstore.logging_setup import configure_logging, get_logger
from jpetstore.seed.runner import seed_development_data


def main() -> None:
    settings = get_settings()
    configure_logging(settings)
    logger = get_logger("seed.cli")
    init_database(settings)
    with session_scope() as session:
        seed_development_data(session, settings)
    logger.info("Seed command finished", extra={"event": "seed.cli.done"})


if __name__ == "__main__":
    main()
