"""Update README with latest TIL entries."""

import logging
import sys

from .config import TILConfig
from .database import TILDatabase
from .readme_generator import ReadmeGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point."""
    config = TILConfig.from_environment()
    til_db = TILDatabase(config.database_path)
    generator = ReadmeGenerator(til_db)

    # Build index
    index_lines = generator.generate_index()
    total_count = til_db.count()

    logger.info(f"Found {total_count} TIL entries")

    # Update README if --rewrite flag is present
    if "--rewrite" in sys.argv:
        readme_path = config.root_path / "README.md"
        logger.info(f"Updating {readme_path}")
        generator.update_readme(readme_path)
    else:
        # Just print the index
        print("\n".join(index_lines))


if __name__ == "__main__":
    main()
