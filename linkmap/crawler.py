import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import collections
from .database import Page, Edge

class Crawler:
    """
    A simple web crawler to gather links from a website and store them in a database.
    """
    def __init__(self, start_url, db_session, max_pages=1000, max_depth=10):
        self.start_url = start_url
        self.db_session = db_session
        self.max_pages = max_pages
        self.max_depth = max_depth

        self.domain = urlparse(start_url).netloc
        self.queue = collections.deque([(start_url, 0)])

        # Keep track of visited URLs in memory to avoid re-queuing
        # For very large crawls, a Bloom filter or disk-based set would be better.
        self.visited_urls = {start_url}

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
            page_data = {'url': url, 'status_code': -1, 'content_type': '', 'depth': depth}

            try:
                response = requests.get(url, timeout=10)
                page_data.update({
                    'status_code': response.status_code,
                    'content_type': response.headers.get('Content-Type', ''),
                })
                print(f"Crawled: {url} (Status: {response.status_code})")

                if 'text/html' in page_data['content_type']:
                    links = self._extract_links(response.content, url)
                    for link in links:
                        self.db_session.add(Edge(source_url=url, target_url=link))
                        if link not in self.visited_urls:
                            self.visited_urls.add(link)
                            self.queue.append((link, depth + 1))

            except requests.RequestException as e:
                print(f"Error fetching {url}: {e}")

            finally:
                # Save page info regardless of success or failure
                page = Page(**page_data)
                self.db_session.add(page)
                self.db_session.commit() # Commit after each page to save incrementally

        print(f"Crawl finished. Processed {crawled_count} pages.")

    def _extract_links(self, html_content, base_url):
        """
        Parses HTML to extract all valid, internal links.
        """
        soup = BeautifulSoup(html_content, 'lxml')
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                continue

            url = self._normalize_url(href, base_url)
            if self._is_internal(url):
                links.add(url)
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
