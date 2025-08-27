import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import collections
import time
from playwright.sync_api import sync_playwright, Error as PlaywrightError
from .database import Page, Edge

class Crawler:
    """
    A web crawler that can use either a simple HTTP client or a headless browser
    to gather links and metadata from a website.
    """
    def __init__(self, config: dict, db_session):
        self.config = config
        self.db_session = db_session

        self.start_url = self.config['start_url']
        self.max_pages = self.config['max_pages']
        self.max_depth = self.config['max_depth']

        self.domain = urlparse(self.start_url).netloc
        self.queue = collections.deque([(self.start_url, 0)])
        self.visited_urls = {self.start_url}

        # Playwright instance, will be initialized in __enter__
        self.playwright = None
        self.browser = None

    def __enter__(self):
        """Initializes resources, like the Playwright browser."""
        if self.config.get('render_js', False):
            print("Initializing headless browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleans up resources."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
            print("Headless browser shut down.")

    def crawl(self):
        """
        Starts the crawling process from the start_url.
        """
        print(f"Starting crawl at {self.start_url} (domain: {self.domain})")

        crawled_count = 0
        while self.queue and crawled_count < self.max_pages:
            url, depth = self.queue.popleft()

            if depth > self.max_depth:
                continue

            crawled_count += 1
            page_data = {'url': url, 'depth': depth}

            try:
                if self.config.get('render_js', False):
                    fetch_data = self._fetch_with_playwright(url)
                else:
                    fetch_data = self._fetch_with_requests(url)

                page_data.update(fetch_data)
                print(f"Crawled: {url} (Status: {page_data['status_code']})")

                if 'text/html' in page_data.get('content_type', ''):
                    soup = BeautifulSoup(page_data['content'], 'lxml')

                    metadata = self._extract_page_metadata(soup, url)
                    page_data.update(metadata)

                    links = self._extract_links(soup, url)
                    for link_data in links:
                        self.db_session.add(Edge(
                            source_url=url,
                            target_url=link_data['target_url'],
                            anchor_text=link_data['anchor_text'],
                            rel=link_data['rel']
                        ))
                        if link_data['target_url'] not in self.visited_urls:
                            self.visited_urls.add(link_data['target_url'])
                            self.queue.append((link_data['target_url'], depth + 1))

            except (requests.RequestException, PlaywrightError) as e:
                print(f"Error fetching {url}: {e}")
                page_data['status_code'] = -1

            finally:
                # Remove content from page_data before saving to DB
                page_data.pop('content', None)
                page = Page(**page_data)
                self.db_session.add(page)
                self.db_session.commit()

        print(f"Crawl finished. Processed {crawled_count} pages.")

    def _fetch_with_requests(self, url: str) -> dict:
        """Fetches a URL using the Requests library."""
        data = {}
        response = requests.get(url, timeout=10)
        data['status_code'] = response.status_code
        data['content_type'] = response.headers.get('Content-Type', '')
        data['load_ms'] = int(response.elapsed.total_seconds() * 1000)
        data['size_bytes'] = len(response.content)
        data['content'] = response.content
        return data

    def _fetch_with_playwright(self, url: str) -> dict:
        """Fetches a URL using Playwright to render JavaScript."""
        if not self.browser:
            raise Exception("Playwright browser not initialized. Did you use a 'with' statement?")

        data = {}
        page = self.browser.new_page()
        try:
            start_time = time.time()
            response = page.goto(url, wait_until='domcontentloaded', timeout=15000)
            end_time = time.time()

            content = page.content()

            data['status_code'] = response.status
            data['content_type'] = response.headers.get('content-type', '')
            data['load_ms'] = int((end_time - start_time) * 1000)
            data['size_bytes'] = len(content.encode('utf-8'))
            data['content'] = content
        finally:
            page.close()
        return data

    def _extract_page_metadata(self, soup: BeautifulSoup, base_url: str) -> dict:
        """Extracts metadata from a BeautifulSoup object."""
        metadata = {}
        # Title
        metadata['title'] = soup.title.string.strip() if soup.title else ''
        # H1
        h1 = soup.find('h1')
        metadata['h1'] = h1.string.strip() if h1 else ''
        # Canonical
        canonical_tag = soup.find('link', rel='canonical')
        if canonical_tag and canonical_tag.get('href'):
            metadata['canonical'] = self._normalize_url(canonical_tag['href'], base_url)
        # Language
        metadata['language'] = soup.html.get('lang', '') if soup.html else ''
        # Meta robots
        robots_tag = soup.find('meta', attrs={'name': 'robots'})
        metadata['meta_robots'] = robots_tag.get('content', '') if robots_tag else ''

        return metadata

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list[dict]:
        """
        Parses HTML to extract all valid, internal links with their attributes.
        """
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                continue

            url = self._normalize_url(href, base_url)
            if self._is_internal(url):
                links.append({
                    'target_url': url,
                    'anchor_text': a_tag.get_text(strip=True),
                    'rel': a_tag.get('rel', [None])[0] or 'dofollow'
                })
        return links

    def _normalize_url(self, href, base_url):
        """
        Resolves a URL fragment to an absolute URL and cleans it.
        """
        url = urljoin(base_url, href)
        # Remove fragment for consistency
        parsed = urlparse(url)._replace(fragment="")
        return parsed.geturl().rstrip('/')

    def _is_internal(self, url):
        """
        Checks if a URL belongs to the same domain as the start_url.
        """
        return urlparse(url).netloc == self.domain
