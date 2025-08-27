# LinkMap

LinkMap is a command-line tool to crawl a website, analyze its internal link structure, and generate reports. This tool is designed to help SEO specialists, UX designers, and developers understand the architecture of a website.

## Features (MVP)

*   **Website Crawler**: A simple, non-JavaScript-rendering crawler that can explore a website from a starting URL.
    *   Respects page and depth limits.
    *   Follows internal links.
*   **Data Storage**: Crawl data is stored in a local SQLite database (`crawl.db`).
    *   Saves page information (URL, status code, etc.).
    *   Saves all discovered links (edges).
*   **Static HTML Reports**: Generates a simple HTML report that includes:
    *   A summary of the crawl.
    *   A list of broken links (4xx/5xx status codes).
    *   A table of all pages discovered.

## Installation

To get started, clone the repository and install the required dependencies.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd linkmap-project
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install the tool:**
    Install the package in editable mode. This will make the `linkmap` command available in your shell.
    ```bash
    pip install -e .
    ```

## Usage

Using LinkMap involves two main steps: crawling the site and then generating a report.

### 1. Crawl a Website

Use the `linkmap crawl` command to start crawling. You must provide a starting URL.

```bash
linkmap crawl --start-url https://example.com --max-pages 50
```

**Options:**
*   `--start-url`: (Required) The URL to begin crawling from.
*   `--max-pages`: The maximum number of pages to crawl. (Default: 100)
*   `--max-depth`: The maximum depth to crawl from the start page. (Default: 5)
*   `--db`: The path to the SQLite database file. (Default: `crawl.db`)

### 2. Generate a Report

Once the crawl is complete, use the `linkmap report` command to generate an HTML report from the database.

```bash
linkmap report --db crawl.db --out ./my-report
```

This will generate an `index.html` file inside the `./my-report` directory.

**Options:**
*   `--db`: The database file to generate the report from. (Default: `crawl.db`)
*   `--out`: The directory where the report will be saved. (Default: `report`)

### Combined Usage

To run a crawl and immediately generate a report, you can chain the commands:

```bash
linkmap crawl --start-url https://books.toscrape.com/ --max-pages 20 && linkmap report
```
