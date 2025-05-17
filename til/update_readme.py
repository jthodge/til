"""Update README with latest TIL entries."""

import logging
import sys

from .config import TILConfig
from .database import TILDatabase
from .exceptions import ConfigurationError, DatabaseError, TILError
from .readme_generator import ReadmeGenerator


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point."""
    try:
        config = TILConfig.from_environment()

        # Check if database exists
        if not config.database_path.exists():
            logger.error(f"Database not found at {config.database_path}")
            logger.info("Run 'til-build' to create the database first")
            sys.exit(1)

        til_db = TILDatabase(config.database_path)
        generator = ReadmeGenerator(til_db)

        # Build index
        try:
            index_lines = generator.generate_index()
            total_count = til_db.count()
            logger.info(f"Found {total_count} TIL entries")
        except DatabaseError as e:
            logger.error(f"Failed to read from database: {e}")
            sys.exit(1)

        # Update README if --rewrite flag is present
        if "--rewrite" in sys.argv:
            readme_path = config.root_path / "README.md"
            if not readme_path.exists():
                logger.error(f"README.md not found at {readme_path}")
                sys.exit(1)

            try:
                logger.info(f"Updating {readme_path}")
                generator.update_readme(readme_path)
                logger.info("README updated successfully")
            except OSError as e:
                logger.error(f"Failed to update README: {e}")
                sys.exit(1)
            except Exception as e:
                logger.error(f"Unexpected error updating README: {e}")
                sys.exit(1)
        else:
            # Just print the index
            print("\n".join(index_lines))

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except TILError as e:
        logger.error(f"TIL error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Update interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
