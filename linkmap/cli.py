import click
from .crawler import Crawler
from . import database
from .database import Page, Edge
from . import report as report_generator
from .config import load_config
import sys

def merge_config_with_cli_params(config, params):
    """Overrides config file values with CLI parameters."""
    cli_args = {key: value for key, value in params.items() if value is not None}
    config.update(cli_args)
    return config

@click.group()
def cli():
    """A tool to crawl a website and generate an interactive link map report."""
    pass

@cli.command()
@click.option('--config', 'config_path', default='config.yml', help='Path to the configuration file.')
@click.option('--start-url', help='The URL to start crawling from (overrides config).')
@click.option('--max-pages', type=int, help='The maximum number of pages to crawl (overrides config).')
@click.option('--max-depth', type=int, help='The maximum crawl depth (overrides config).')
@click.option('--db', help='Path to the SQLite database file (overrides config).')
def crawl(config_path, start_url, max_pages, max_depth, db):
    """Crawl a website to collect link data."""
    try:
        config = load_config(config_path)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    # Override config with CLI parameters
    cli_params = {'start_url': start_url, 'max_pages': max_pages, 'max_depth': max_depth, 'db': db}
    config = merge_config_with_cli_params(config, cli_params)

    db_path = config['db']
    click.echo(f"Output will be saved to '{db_path}'")
    engine = database.get_engine(db_path)
    database.create_db_and_tables(engine)
    session = database.get_session(engine)

    try:
        with Crawler(config=config, db_session=session) as crawler:
            crawler.crawl()

        page_count = session.query(Page).count()
        edge_count = session.query(Edge).count()
        click.echo(f"Crawl complete. Stored {page_count} pages and {edge_count} links in '{db_path}'.")

    finally:
        session.close()


@cli.command()
@click.option('--db', default='crawl.db', help='Path to the SQLite database file to read from.')
@click.option('--out', default='report', help='The directory to save the report to.')
def report(db, out):
    """Generate an interactive report from crawl data."""
    engine = database.get_engine(db)
    session = database.get_session(engine)

    try:
        click.echo(f"Generating report from '{db}' into '{out}' directory...")
        report_generator.generate_report(session, output_dir=out)
        click.echo("Report generation complete.")
    finally:
        session.close()


if __name__ == '__main__':
    cli()
