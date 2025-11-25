"""ffuf Wrapper - Production-Grade Web Fuzzing

Comprehensive wrapper for ffuf (Fuzz Faster U Fool) with directory/file
discovery, parameter fuzzing, and virtual host discovery.
Version: 1.0.0
"""

import subprocess
import json
import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class FfufWrapper:
    """Production-grade ffuf web fuzzing wrapper."""

    def __init__(self,
                 output_dir: str = "/tmp/ffuf",
                 wordlist_dir: str = "/usr/share/wordlists",
                 rate_limit: int = 100,
                 timeout: int = 1800):
        """
        Initialize ffuf wrapper.

        Args:
            output_dir: Output directory for results
            wordlist_dir: Directory containing wordlists
            rate_limit: Max requests per second
            timeout: Maximum execution time in seconds
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.wordlist_dir = Path(wordlist_dir)
        self.rate_limit = rate_limit
        self.timeout = timeout

        # Common wordlists
        self.wordlists = {
            "directories": str(self.wordlist_dir / "dirb/common.txt"),
            "files": str(self.wordlist_dir / "dirb/common.txt"),
            "parameters": str(self.wordlist_dir / "SecLists/Discovery/Web-Content/burp-parameter-names.txt"),
            "subdomains": str(self.wordlist_dir / "SecLists/Discovery/DNS/subdomains-top1million-20000.txt"),
            "large": str(self.wordlist_dir / "SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt")
        }

        # Check if ffuf is installed
        try:
            subprocess.run(['ffuf', '-V'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            raise RuntimeError("ffuf not installed. Install from: https://github.com/ffuf/ffuf")

    def fuzz_directories(self,
                         url: str,
                         wordlist: Optional[str] = None,
                         extensions: Optional[List[str]] = None,
                         recursion: bool = False,
                         recursion_depth: int = 2,
                         match_codes: List[int] = [200, 204, 301, 302, 307, 401, 403],
                         threads: int = 40) -> Dict[str, Any]:
        """
        Fuzz directories and files.

        Args:
            url: Target URL with FUZZ keyword (e.g., https://example.com/FUZZ)
            wordlist: Custom wordlist path
            extensions: File extensions to append (e.g., ['.php', '.html'])
            recursion: Enable recursive fuzzing
            recursion_depth: Maximum recursion depth
            match_codes: HTTP status codes to match
            threads: Number of concurrent threads

        Returns:
            Dict with discovered paths and metadata
        """
        logger.info(f"Starting ffuf directory fuzzing on {url}")

        if "FUZZ" not in url:
            url = url.rstrip('/') + '/FUZZ'

        output_file = self.output_dir / f"ffuf_dir_{int(time.time())}.json"
        wordlist = wordlist or self.wordlists.get("directories")

        command = [
            'ffuf',
            '-u', url,
            '-w', wordlist,
            '-mc', ','.join(map(str, match_codes)),
            '-t', str(threads),
            '-rate', str(self.rate_limit),
            '-timeout', str(min(30, self.timeout)),
            '-o', str(output_file),
            '-of', 'json',
            '-se',  # Stop on spurious errors
            '-sa',  # Stop on all errors
        ]

        if extensions:
            command.extend(['-e', ','.join(extensions)])

        if recursion:
            command.extend(['-recursion', '-recursion-depth', str(recursion_depth)])

        # Auto-calibration for false positives
        command.extend(['-ac'])

        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            duration = time.time() - start_time

            # Parse JSON output
            findings = self._parse_json_output(output_file)

            logger.info(f"ffuf directory fuzzing found {len(findings)} paths in {duration:.2f}s")

            return {
                "url": url,
                "type": "directory_fuzzing",
                "findings": findings,
                "count": len(findings),
                "duration": duration,
                "output_file": str(output_file)
            }

        except subprocess.TimeoutExpired:
            logger.error(f"ffuf directory fuzzing timed out after {self.timeout}s")
            return {"error": "timeout", "url": url, "findings": []}
        except Exception as e:
            logger.error(f"ffuf directory fuzzing failed: {e}")
            return {"error": str(e), "url": url, "findings": []}

    def fuzz_parameters(self,
                        url: str,
                        method: str = "GET",
                        wordlist: Optional[str] = None,
                        data: Optional[str] = None,
                        headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Fuzz URL/POST parameters.

        Args:
            url: Target URL with FUZZ keyword (e.g., https://example.com/api?FUZZ=value)
            method: HTTP method (GET, POST, PUT, etc.)
            wordlist: Custom parameter wordlist
            data: POST data with FUZZ keyword
            headers: Custom headers

        Returns:
            Dict with discovered parameters
        """
        logger.info(f"Starting ffuf parameter fuzzing on {url}")

        output_file = self.output_dir / f"ffuf_params_{int(time.time())}.json"
        wordlist = wordlist or self.wordlists.get("parameters")

        command = [
            'ffuf',
            '-u', url,
            '-w', wordlist,
            '-X', method.upper(),
            '-mc', '200,302,401,403',
            '-t', '40',
            '-rate', str(self.rate_limit),
            '-o', str(output_file),
            '-of', 'json',
            '-ac',
        ]

        if data:
            command.extend(['-d', data])

        if headers:
            for key, value in headers.items():
                command.extend(['-H', f"{key}: {value}"])

        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            duration = time.time() - start_time
            findings = self._parse_json_output(output_file)

            logger.info(f"ffuf parameter fuzzing found {len(findings)} parameters in {duration:.2f}s")

            return {
                "url": url,
                "type": "parameter_fuzzing",
                "method": method,
                "findings": findings,
                "count": len(findings),
                "duration": duration,
                "output_file": str(output_file)
            }

        except subprocess.TimeoutExpired:
            logger.error(f"ffuf parameter fuzzing timed out")
            return {"error": "timeout", "url": url, "findings": []}
        except Exception as e:
            logger.error(f"ffuf parameter fuzzing failed: {e}")
            return {"error": str(e), "url": url, "findings": []}

    def fuzz_vhosts(self,
                    url: str,
                    wordlist: Optional[str] = None,
                    filter_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Fuzz virtual hosts.

        Args:
            url: Target URL with FUZZ in Host header placeholder
            wordlist: Subdomain wordlist
            filter_size: Filter responses by size

        Returns:
            Dict with discovered virtual hosts
        """
        logger.info(f"Starting ffuf vhost fuzzing on {url}")

        output_file = self.output_dir / f"ffuf_vhosts_{int(time.time())}.json"
        wordlist = wordlist or self.wordlists.get("subdomains")

        # Extract domain from URL
        from urllib.parse import urlparse
        parsed = urlparse(url)
        base_domain = parsed.netloc

        command = [
            'ffuf',
            '-u', url,
            '-w', wordlist,
            '-H', f'Host: FUZZ.{base_domain}',
            '-mc', '200,302,401,403',
            '-t', '40',
            '-rate', str(self.rate_limit),
            '-o', str(output_file),
            '-of', 'json',
            '-ac',
        ]

        if filter_size:
            command.extend(['-fs', str(filter_size)])

        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            duration = time.time() - start_time
            findings = self._parse_json_output(output_file)

            logger.info(f"ffuf vhost fuzzing found {len(findings)} virtual hosts in {duration:.2f}s")

            return {
                "url": url,
                "type": "vhost_fuzzing",
                "findings": findings,
                "count": len(findings),
                "duration": duration,
                "output_file": str(output_file)
            }

        except subprocess.TimeoutExpired:
            logger.error(f"ffuf vhost fuzzing timed out")
            return {"error": "timeout", "url": url, "findings": []}
        except Exception as e:
            logger.error(f"ffuf vhost fuzzing failed: {e}")
            return {"error": str(e), "url": url, "findings": []}

    def _parse_json_output(self, json_file: Path) -> List[Dict[str, Any]]:
        """Parse ffuf JSON output file."""
        findings = []

        if not json_file.exists():
            logger.warning(f"Output file not found: {json_file}")
            return findings

        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            results = data.get("results", [])

            for result in results:
                finding = {
                    "url": result.get("url"),
                    "input": result.get("input", {}),
                    "position": result.get("position"),
                    "status_code": result.get("status"),
                    "length": result.get("length"),
                    "words": result.get("words"),
                    "lines": result.get("lines"),
                    "content_type": result.get("content-type"),
                    "redirect_location": result.get("redirectlocation"),
                    "duration": result.get("duration")
                }
                findings.append(finding)

        except Exception as e:
            logger.error(f"Failed to parse JSON output: {e}")

        return findings

    def api_fuzz(self,
                 base_url: str,
                 endpoints: List[str],
                 methods: List[str] = ["GET", "POST", "PUT", "DELETE"],
                 wordlist: Optional[str] = None) -> Dict[str, Any]:
        """
        Fuzz API endpoints and parameters.

        Args:
            base_url: Base API URL
            endpoints: List of endpoint paths to fuzz
            methods: HTTP methods to test
            wordlist: Parameter wordlist

        Returns:
            Dict with API fuzzing results
        """
        logger.info(f"Starting API fuzzing on {base_url}")

        all_findings = []

        for endpoint in endpoints:
            for method in methods:
                url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

                if method == "GET":
                    fuzz_url = f"{url}?FUZZ=test"
                    results = self.fuzz_parameters(fuzz_url, method=method, wordlist=wordlist)
                else:
                    results = self.fuzz_parameters(url, method=method, data="FUZZ=test", wordlist=wordlist)

                all_findings.extend(results.get("findings", []))

        return {
            "base_url": base_url,
            "type": "api_fuzzing",
            "endpoints_tested": len(endpoints),
            "methods_tested": methods,
            "findings": all_findings,
            "count": len(all_findings)
        }
