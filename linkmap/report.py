from jinja2 import Environment, FileSystemLoader
import os
from .database import Page

def generate_report(db_session, output_dir='report'):
    """
    Generates a static HTML report from the crawl data in the database.
    """
    print("Generating report...")

    # Query data from the database
    all_pages = db_session.query(Page).order_by(Page.url).all()
    broken_links = [p for p in all_pages if p.status_code < 0 or p.status_code >= 400]

    # Set up Jinja2 environment. We assume a 'templates' directory in the root.
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('report.html.j2')

    # Render the template with data
    html_content = template.render(
        all_pages=all_pages,
        broken_links=broken_links,
        total_pages=len(all_pages),
        total_broken=len(broken_links)
    )

    # Write the report file
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    report_path = os.path.join(output_dir, 'index.html')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Report generated successfully at {os.path.abspath(report_path)}")
