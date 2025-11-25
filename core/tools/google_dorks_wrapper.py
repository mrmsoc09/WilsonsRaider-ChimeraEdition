"""Google Dorks Wrapper - Automated OSINT via Google Search

Comprehensive Google dorking automation with pre-built queries,
rate limiting, and result parsing.
Version: 1.0.0
"""

import os
import time
import logging
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class GoogleDorksWrapper:
    """
    Production-grade Google dorking automation.

    Uses Google Custom Search API (100 free queries/day)
    or falls back to web scraping (use responsibly).
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 cse_id: Optional[str] = None,
                 use_api: bool = True):
        """
        Initialize Google Dorks wrapper.

        Args:
            api_key: Google API key
            cse_id: Custom Search Engine ID
            use_api: Use official API (recommended) vs scraping
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.cse_id = cse_id or os.getenv("GOOGLE_CSE_ID")
        self.use_api = use_api and self.api_key and self.cse_id

        # Rate limiting
        self.last_request_time = 0
        self.min_delay = 2  # seconds between requests

        # Pre-built dork categories
        self.dork_categories = self._load_dork_templates()

        if self.use_api:
            logger.info("Google Dorks using official API (100 queries/day)")
        else:
            logger.warning("Google Dorks using scraping mode (use responsibly)")

    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Execute a single Google search query.

        Args:
            query: Search query (can include dork operators)
            num_results: Number of results to retrieve

        Returns:
            List of search results with URL, title, snippet
        """
        logger.info(f"Searching: {query}")

        # Rate limiting
        self._rate_limit()

        if self.use_api:
            return self._search_api(query, num_results)
        else:
            return self._search_scrape(query, num_results)

    def _search_api(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API."""
        results = []

        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.api_key,
                "cx": self.cse_id,
                "q": query,
                "num": min(num_results, 10)  # API max is 10 per request
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            for item in data.get("items", []):
                results.append({
                    "title": item.get("title"),
                    "url": item.get("link"),
                    "snippet": item.get("snippet"),
                    "displayLink": item.get("displayLink")
                })

            logger.info(f"Found {len(results)} results")

        except Exception as e:
            logger.error(f"Google API search failed: {e}")

        return results

    def _search_scrape(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """
        Fallback: Parse Google search results (use responsibly).

        Note: This should only be used for testing. For production,
        use the official API or tools like googlesearch-python.
        """
        results = []

        try:
            # Use googlesearch library if available
            from googlesearch import search

            urls = search(query, num=num_results, stop=num_results, pause=2)

            for url in urls:
                results.append({
                    "title": "",  # Scraping doesn't provide titles easily
                    "url": url,
                    "snippet": "",
                    "displayLink": url.split('/')[2] if '/' in url else url
                })

        except ImportError:
            logger.error("googlesearch-python not installed. Install: pip install googlesearch-python")
        except Exception as e:
            logger.error(f"Google scraping failed: {e}")

        return results

    def dork_site(self, target_domain: str, category: str = "all") -> Dict[str, Any]:
        """
        Run pre-built dorks against a target domain.

        Args:
            target_domain: Target domain (e.g., example.com)
            category: Dork category (exposed_files, login_pages, admin_panels, etc.)

        Returns:
            Dict with categorized results
        """
        logger.info(f"Running {category} dorks on {target_domain}")

        categories_to_run = (
            [category] if category != "all"
            else list(self.dork_categories.keys())
        )

        all_results = {}

        for cat in categories_to_run:
            dorks = self.dork_categories.get(cat, [])
            category_results = []

            for dork_template in dorks[:5]:  # Limit to 5 per category to save quota
                query = dork_template.format(domain=target_domain)
                results = self.search(query, num_results=10)

                if results:
                    category_results.extend(results)

            all_results[cat] = {
                "count": len(category_results),
                "results": category_results
            }

        return {
            "target": target_domain,
            "categories": all_results,
            "total_results": sum(r["count"] for r in all_results.values())
        }

    def find_subdomains(self, domain: str) -> List[str]:
        """Find subdomains using Google."""
        query = f"site:*.{domain} -site:www.{domain}"
        results = self.search(query, num_results=50)

        subdomains = set()
        for result in results:
            url = result.get("url", "")
            if domain in url:
                # Extract subdomain
                try:
                    parts = url.split("//")[1].split("/")[0]
                    if domain in parts:
                        subdomains.add(parts)
                except:
                    pass

        return list(subdomains)

    def find_exposed_files(self, domain: str, file_types: List[str] = None) -> Dict[str, List[Dict]]:
        """
        Find exposed files of specific types.

        Args:
            domain: Target domain
            file_types: List of file extensions (default: common sensitive files)
        """
        if not file_types:
            file_types = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'sql', 'env', 'config', 'log']

        results_by_type = {}

        for file_type in file_types[:10]:  # Limit to save quota
            query = f'site:{domain} filetype:{file_type}'
            results = self.search(query, num_results=10)

            if results:
                results_by_type[file_type] = results

        return results_by_type

    def find_login_pages(self, domain: str) -> List[Dict[str, Any]]:
        """Find login pages."""
        queries = [
            f'site:{domain} inurl:login',
            f'site:{domain} inurl:signin',
            f'site:{domain} inurl:admin',
            f'site:{domain} intitle:"login"',
        ]

        all_results = []
        for query in queries:
            results = self.search(query, num_results=10)
            all_results.extend(results)

        # Deduplicate by URL
        unique_results = {r['url']: r for r in all_results}.values()

        return list(unique_results)

    def find_exposed_credentials(self, domain: str) -> List[Dict[str, Any]]:
        """
        Find potential credential exposures (VERY SENSITIVE - use ethically).
        """
        queries = [
            f'site:{domain} intext:"password"',
            f'site:{domain} filetype:env',
            f'site:{domain} filetype:config intext:password',
            f'site:{domain} ext:sql intext:password',
        ]

        all_results = []
        for query in queries[:3]:  # Limit for safety
            results = self.search(query, num_results=5)
            all_results.extend(results)

        return all_results

    def find_error_messages(self, domain: str) -> List[Dict[str, Any]]:
        """Find pages with error messages (info disclosure)."""
        queries = [
            f'site:{domain} intext:"error" intext:"stack trace"',
            f'site:{domain} intext:"Exception"',
            f'site:{domain} intext:"Warning: mysql"',
            f'site:{domain} intext:"Fatal error"',
        ]

        all_results = []
        for query in queries:
            results = self.search(query, num_results=10)
            all_results.extend(results)

        return all_results

    def _rate_limit(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_request_time = time.time()

    def _load_dork_templates(self) -> Dict[str, List[str]]:
        """Load pre-built Google dork templates."""
        return {
            "exposed_files": [
                'site:{domain} filetype:pdf',
                'site:{domain} filetype:doc OR filetype:docx',
                'site:{domain} filetype:xls OR filetype:xlsx',
                'site:{domain} filetype:sql',
                'site:{domain} filetype:env',
                'site:{domain} filetype:config',
                'site:{domain} filetype:log',
                'site:{domain} filetype:bak',
                'site:{domain} ext:txt intext:password',
            ],
            "login_pages": [
                'site:{domain} inurl:login',
                'site:{domain} inurl:signin',
                'site:{domain} inurl:auth',
                'site:{domain} intitle:"login"',
                'site:{domain} intitle:"sign in"',
            ],
            "admin_panels": [
                'site:{domain} inurl:admin',
                'site:{domain} inurl:administrator',
                'site:{domain} inurl:cpanel',
                'site:{domain} intitle:"admin panel"',
                'site:{domain} inurl:dashboard',
            ],
            "error_messages": [
                'site:{domain} intext:"error" intext:"warning"',
                'site:{domain} intext:"Exception"',
                'site:{domain} intext:"stack trace"',
                'site:{domain} intext:"Fatal error"',
            ],
            "directory_listings": [
                'site:{domain} intitle:"index of"',
                'site:{domain} intitle:"directory listing"',
            ],
            "subdomains": [
                'site:*.{domain}',
                'site:*.{domain} -www',
            ],
            "exposed_databases": [
                'site:{domain} filetype:sql',
                'site:{domain} inurl:phpmyadmin',
                'site:{domain} intext:"MySQL" intext:"dump"',
            ],
            "api_endpoints": [
                'site:{domain} inurl:api',
                'site:{domain} inurl:/v1/',
                'site:{domain} inurl:/v2/',
                'site:{domain} intitle:"API documentation"',
            ],
            "git_exposure": [
                'site:{domain} inurl:.git',
                'site:{domain} filetype:git',
            ],
            "aws_keys": [
                'site:{domain} "AKIA"',  # AWS access key pattern
                'site:{domain} filetype:env "AWS"',
            ]
        }

    def get_available_categories(self) -> List[str]:
        """Get list of available dork categories."""
        return list(self.dork_categories.keys())
