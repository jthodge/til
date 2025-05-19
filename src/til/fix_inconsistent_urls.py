#!/usr/bin/env python
"""Fix inconsistent URLs in the TIL database.

Some entries have old paths (without content/) but their files
are actually in the content/ directory. This script rebuilds the
database to ensure consistency.
"""

import logging
import sys

from .config_loader import ConfigLoader
from .processor import TILProcessor


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Rebuild database to fix inconsistent URLs."""
    try:
        # Load configuration
        config_loader = ConfigLoader()
        config = config_loader.load_config()

        # Create processor and rebuild database
        processor = TILProcessor(config)
        logger.info("Rebuilding database to fix inconsistent URLs...")
        processor.build_database()

        logger.info("Database rebuild complete!")

    except Exception as e:
        logger.error(f"Error rebuilding database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
