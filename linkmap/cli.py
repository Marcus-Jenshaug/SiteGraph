import click
from .crawler import Crawler
from . import database
from .database import Page, Edge
from . import report as report_generator

@click.group()
def cli():
    """A tool to crawl a website and generate an interactive link map report."""
    pass

@cli.command()
@click.option('--start-url', required=True, help='The URL to start crawling from.')
@click.option('--max-pages', default=100, help='The maximum number of pages to crawl.')
@click.option('--max-depth', default=5, help='The maximum crawl depth.')
@click.option('--db', default='crawl.db', help='Path to the SQLite database file.')
def crawl(start_url, max_pages, max_depth, db):
    """Crawl a website to collect link data."""
    click.echo(f"Output will be saved to '{db}'")
    engine = database.get_engine(db)
    database.create_db_and_tables(engine)
    session = database.get_session(engine)

    try:
        crawler = Crawler(
            start_url=start_url,
            db_session=session,
            max_pages=max_pages,
            max_depth=max_depth
        )
        crawler.crawl()

        page_count = session.query(Page).count()
        edge_count = session.query(Edge).count()
        click.echo(f"Crawl complete. Stored {page_count} pages and {edge_count} links in '{db}'.")

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
        report_generator.generate_report(session, output_dir=out)
    finally:
        session.close()


if __name__ == '__main__':
    cli()
