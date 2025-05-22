"""Command line interface for TIL."""

import sys
from pathlib import Path
from typing import Optional

import click

from .config_loader import ConfigLoader
from .database import TILDatabase
from .exceptions import ConfigurationError, DatabaseError, TILError
from .fix_creation_dates import fix_creation_dates
from .logging_config import LogLevel, setup_logging
from .processor import TILProcessor
from .readme_generator import ReadmeGenerator


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress all output except errors")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """TIL - Today I Learned static site generator.

    A tool for building a static website from markdown files containing
    today-I-learned entries. Automatically extracts metadata from git
    history and renders markdown to HTML.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet


@cli.command()
@click.option(
    "--github-token",
    envvar="MARKDOWN_GITHUB_TOKEN",
    help="GitHub token for markdown API",
)
@click.option(
    "--repo",
    envvar="TIL_GITHUB_REPO",
    default="jthodge/til",
    help="GitHub repository (owner/name)",
)
@click.option("--db", default="til.db", help="Database file name")
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.pass_context
def build(
    ctx: click.Context,
    github_token: Optional[str],
    repo: str,
    db: str,
    config: Optional[Path],
) -> None:
    """Build TIL database from markdown files.

    Scans the repository for markdown files organized by topic directories,
    extracts metadata from git history, renders markdown to HTML using the
    GitHub API, and creates a SQLite database for serving with Datasette.
    """
    verbose = ctx.obj.get("verbose", False)
    quiet = ctx.obj.get("quiet", False)

    try:
        til_config = ConfigLoader.load_config(
            config_file=config,
            github_token=github_token,
            github_repo=repo,
            database_name=db,
        )

        # Configure logging based on flags and config
        log_config = til_config.log_config
        if quiet:
            log_config.level = LogLevel.ERROR
        elif verbose:
            log_config.level = LogLevel.DEBUG

        setup_logging(log_config)

        import logging

        logger = logging.getLogger(__name__)

        if verbose:
            click.echo(f"Building database: {til_config.database_path}")
            click.echo(f"Repository: {til_config.github_repo}")

        processor = TILProcessor(til_config)
        processor.build_database()

        if not quiet:
            click.echo(click.style("✨ Database built successfully!", fg="green"))

    except ConfigurationError as e:
        click.echo(click.style(f"Configuration error: {e}", fg="red"), err=True)
        sys.exit(1)
    except TILError as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nBuild interrupted by user")
        sys.exit(130)
    except Exception as e:
        import logging

        try:
            logger = logging.getLogger(__name__)
            logger.exception("Unexpected error")
        except Exception:
            pass
        click.echo(click.style(f"Unexpected error: {e}", fg="red"), err=True)
        sys.exit(1)


@cli.command(name="update-readme")
@click.option("--rewrite", is_flag=True, help="Update README file in place")
@click.option("--db", default="til.db", help="Database file name")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file (default: stdout or README.md with --rewrite)",
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.pass_context
def update_readme(
    ctx: click.Context,
    rewrite: bool,
    db: str,
    output: Optional[str],
    config: Optional[Path],
) -> None:
    """Update README with latest TIL entries.

    Generates an index of all TIL entries organized by topic. By default,
    prints the index to stdout. Use --rewrite to update README.md in place.
    """
    verbose = ctx.obj.get("verbose", False)
    quiet = ctx.obj.get("quiet", False)

    try:
        til_config = ConfigLoader.load_config(
            config_file=config,
            database_name=db,
        )

        # Configure logging based on flags and config
        log_config = til_config.log_config
        if quiet:
            log_config.level = LogLevel.ERROR
        elif verbose:
            log_config.level = LogLevel.DEBUG

        setup_logging(log_config)

        import logging

        logger = logging.getLogger(__name__)

        # Check if database exists
        if not til_config.database_path.exists():
            click.echo(
                click.style(
                    f"Database not found at {til_config.database_path}\n"
                    + "Run 'til build' to create the database first",
                    fg="red",
                ),
                err=True,
            )
            sys.exit(1)

        til_db = TILDatabase(til_config.database_path)
        generator = ReadmeGenerator(til_db)

        # Build index
        try:
            index_lines = generator.generate_index()
            total_count = til_db.count()

            if verbose:
                click.echo(f"Found {total_count} TIL entries")

        except DatabaseError as e:
            click.echo(
                click.style(f"Failed to read from database: {e}", fg="red"), err=True
            )
            sys.exit(1)

        # Handle output
        if rewrite:
            readme_path = til_config.root_path / "README.md"
            if not readme_path.exists():
                click.echo(
                    click.style(f"README.md not found at {readme_path}", fg="red"),
                    err=True,
                )
                sys.exit(1)

            try:
                if verbose:
                    click.echo(f"Updating {readme_path}")

                generator.update_readme(readme_path)

                if not quiet:
                    click.echo(
                        click.style("✨ README updated successfully!", fg="green")
                    )

            except OSError as e:
                click.echo(
                    click.style(f"Failed to update README: {e}", fg="red"), err=True
                )
                sys.exit(1)

        elif output:
            # Write to specified output file
            output_path = Path(output)
            try:
                with open(output_path, "w") as f:
                    f.write("\n".join(index_lines))

                if not quiet:
                    click.echo(
                        click.style(f"✨ Index written to {output_path}", fg="green")
                    )

            except OSError as e:
                click.echo(
                    click.style(f"Failed to write output: {e}", fg="red"), err=True
                )
                sys.exit(1)

        else:
            # Print to stdout
            click.echo("\n".join(index_lines))

    except ConfigurationError as e:
        click.echo(click.style(f"Configuration error: {e}", fg="red"), err=True)
        sys.exit(1)
    except TILError as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nUpdate interrupted by user")
        sys.exit(130)
    except Exception as e:
        import logging

        try:
            logger = logging.getLogger(__name__)
            logger.exception("Unexpected error")
        except Exception:
            pass
        click.echo(click.style(f"Unexpected error: {e}", fg="red"), err=True)
        sys.exit(1)


@cli.command(name="fix-creation-dates")
@click.option("--db", default="til.db", help="Database file name")
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what changes would be made without applying them",
)
@click.pass_context
def fix_creation_dates_cmd(
    ctx: click.Context,
    db: str,
    config: Optional[Path],
    dry_run: bool,
) -> None:
    """Fix creation dates in database by re-extracting from git history.

    This command addresses the issue where TIL entries have incorrect creation
    dates due to database rebuilds. It re-extracts the correct creation dates
    from git history and updates the database.

    Only entries with creation dates from 2025-05-18 or 2025-05-19 will be
    updated, preserving existing update timestamps where appropriate.
    """
    verbose = ctx.obj.get("verbose", False)
    quiet = ctx.obj.get("quiet", False)

    try:
        til_config = ConfigLoader.load_config(
            config_file=config,
            database_name=db,
        )

        # Configure logging based on flags and config
        log_config = til_config.log_config
        if quiet:
            log_config.level = LogLevel.ERROR
        elif verbose:
            log_config.level = LogLevel.DEBUG

        setup_logging(log_config)

        import logging

        logger = logging.getLogger(__name__)

        # Check if database exists
        if not til_config.database_path.exists():
            click.echo(
                click.style(
                    f"Database not found at {til_config.database_path}\n"
                    + "Run 'til build' to create the database first",
                    fg="red",
                ),
                err=True,
            )
            sys.exit(1)

        if verbose:
            click.echo(f"Fixing creation dates in: {til_config.database_path}")
            click.echo(f"Repository: {til_config.root_path}")

        if dry_run:
            click.echo(
                click.style("DRY RUN MODE - No changes will be made", fg="yellow")
            )

        # Import the function that does the actual work
        from .fix_creation_dates import fix_creation_dates

        # Call the fix function
        fix_creation_dates(
            til_config.database_path, til_config.root_path, dry_run=dry_run
        )

        if not quiet:
            if dry_run:
                click.echo(
                    click.style("✨ Dry run completed - no changes made", fg="green")
                )
            else:
                click.echo(
                    click.style("✨ Creation dates fixed successfully!", fg="green")
                )

    except ConfigurationError as e:
        click.echo(click.style(f"Configuration error: {e}", fg="red"), err=True)
        sys.exit(1)
    except TILError as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nFix interrupted by user")
        sys.exit(130)
    except Exception as e:
        import logging

        try:
            logger = logging.getLogger(__name__)
            logger.exception("Unexpected error")
        except Exception:
            pass
        click.echo(click.style(f"Unexpected error: {e}", fg="red"), err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
