"""Build TIL database from markdown files."""

import logging
import sys

from .config import TILConfig
from .exceptions import ConfigurationError, FileProcessingError, TILError
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

    Raises:
        TILError: If database build fails

    """
    try:
        processor = TILProcessor(config)
        processor.build_database()
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        raise
    except FileProcessingError as e:
        logger.error(f"Processing error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error building database: {e}")
        raise TILError(f"Failed to build database: {e}")


def main() -> None:
    """Main entry point."""
    try:
        config = TILConfig.from_environment()
        build_database(config)
        logger.info("Database build completed successfully")
    except TILError as e:
        logger.error(f"TIL error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Build interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
