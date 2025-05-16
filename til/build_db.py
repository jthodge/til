"""Build TIL database from markdown files."""

import logging

from .config import TILConfig
from .processor import TILProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def build_database(config: TILConfig) -> None:
    """Build SQLite database from markdown files in repository.

    Args:
        config: TIL configuration
    """
    processor = TILProcessor(config)
    processor.build_database()


def main() -> None:
    """Main entry point."""
    config = TILConfig.from_environment()
    build_database(config)


if __name__ == "__main__":
    main()
