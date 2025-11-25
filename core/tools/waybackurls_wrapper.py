"""Waybackurls/GAU Wrapper - URL Discovery from Archives

Fetch URLs from Wayback Machine and other web archives.
Version: 1.0.0
"""

import subprocess
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ArchiveURLWrapper:
    """Wrapper for waybackurls and gau (GetAllUrls)."""

    def __init__(self, output_dir: str = "/tmp/archive_urls"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Check which tools are available
        self.has_waybackurls = self._check_tool('waybackurls')
        self.has_gau = self._check_tool('gau')

    def _check_tool(self, tool: str) -> bool:
        """Check if a tool is installed."""
        try:
            subprocess.run([tool, '-h'], capture_output=True)
            return True
        except FileNotFoundError:
            return False

    def fetch_urls(self, domain: str, include_subs: bool = True) -> Dict[str, Any]:
        """Fetch URLs from web archives."""
        logger.info(f"Fetching archived URLs for {domain}")

        all_urls = set()

        # Try waybackurls first
        if self.has_waybackurls:
            urls = self._fetch_waybackurls(domain, include_subs)
            all_urls.update(urls)
            logger.info(f"waybackurls found {len(urls)} URLs")

        # Also try gau
        if self.has_gau:
            urls = self._fetch_gau(domain, include_subs)
            all_urls.update(urls)
            logger.info(f"gau found {len(urls)} additional URLs")

        # Categorize URLs
        categorized = self._categorize_urls(list(all_urls))

        return {
            "domain": domain,
            "total_urls": len(all_urls),
            "urls": list(all_urls),
            "categorized": categorized
        }

    def _fetch_waybackurls(self, domain: str, include_subs: bool) -> List[str]:
        """Fetch URLs using waybackurls."""
        try:
            command = ['waybackurls', domain]
            result = subprocess.run(command, capture_output=True, text=True, timeout=300)
            return [url.strip() for url in result.stdout.split('\n') if url.strip()]
        except Exception as e:
            logger.error(f"waybackurls failed: {e}")
            return []

    def _fetch_gau(self, domain: str, include_subs: bool) -> List[str]:
        """Fetch URLs using gau."""
        try:
            command = ['gau', domain]
            if include_subs:
                command.append('--subs')
            result = subprocess.run(command, capture_output=True, text=True, timeout=300)
            return [url.strip() for url in result.stdout.split('\n') if url.strip()]
        except Exception as e:
            logger.error(f"gau failed: {e}")
            return []

    def _categorize_urls(self, urls: List[str]) -> Dict[str, List[str]]:
        """Categorize URLs by type (API endpoints, files, parameters, etc.)."""
        categories = {
            "api_endpoints": [],
            "with_parameters": [],
            "files": {"js": [], "json": [], "xml": [], "pdf": [], "other": []},
            "admin_panels": [],
            "other": []
        }

        for url in urls:
            if '/api/' in url or '/v1/' in url or '/v2/' in url:
                categories["api_endpoints"].append(url)
            elif '?' in url:
                categories["with_parameters"].append(url)
            elif '/admin' in url or '/login' in url or '/dashboard' in url:
                categories["admin_panels"].append(url)
            elif url.endswith('.js'):
                categories["files"]["js"].append(url)
            elif url.endswith('.json'):
                categories["files"]["json"].append(url)
            elif url.endswith(('.xml', '.config')):
                categories["files"]["xml"].append(url)
            elif url.endswith('.pdf'):
                categories["files"]["pdf"].append(url)
            else:
                categories["other"].append(url)

        return categories
