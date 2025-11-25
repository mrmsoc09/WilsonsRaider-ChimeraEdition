"""httpx Wrapper - Production-Grade HTTP Probing

Fast HTTP probing tool for validating live hosts, extracting titles,
status codes, and technology fingerprinting.
Version: 1.0.0
"""

import subprocess
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class HttpxWrapper:
    """Production-grade httpx HTTP probing wrapper."""

    def __init__(self, output_dir: str = "/tmp/httpx", rate_limit: int = 150, threads: int = 50):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit = rate_limit
        self.threads = threads

        try:
            subprocess.run(['httpx', '-version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            raise RuntimeError("httpx not installed. Install: go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest")

    def probe_urls(self, urls: List[str], tech_detect: bool = True, screenshot: bool = False,
                   follow_redirects: bool = True, match_codes: Optional[List[int]] = None) -> Dict[str, Any]:
        """Probe URLs to check if they're alive and extract metadata."""
        logger.info(f"Probing {len(urls)} URLs with httpx")

        input_file = self.output_dir / "urls_input.txt"
        output_file = self.output_dir / "httpx_output.json"

        with open(input_file, 'w') as f:
            f.write('\n'.join(urls))

        command = [
            'httpx', '-l', str(input_file), '-json', '-o', str(output_file),
            '-threads', str(self.threads), '-rate-limit', str(self.rate_limit),
            '-title', '-status-code', '-content-length', '-server', '-method'
        ]

        if tech_detect:
            command.append('-tech-detect')
        if screenshot:
            command.extend(['-screenshot', '-screenshot-path', str(self.output_dir / "screenshots")])
        if follow_redirects:
            command.append('-follow-redirects')
        if match_codes:
            command.extend(['-mc', ','.join(map(str, match_codes))])

        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=600)
            probed_hosts = self._parse_json_output(output_file)
            logger.info(f"httpx found {len(probed_hosts)} live hosts")

            return {
                "total_urls": len(urls),
                "live_hosts": probed_hosts,
                "live_count": len(probed_hosts),
                "output_file": str(output_file)
            }
        except Exception as e:
            logger.error(f"httpx probing failed: {e}")
            return {"error": str(e), "live_hosts": []}

    def _parse_json_output(self, json_file: Path) -> List[Dict[str, Any]]:
        """Parse httpx JSON output."""
        hosts = []
        if not json_file.exists():
            return hosts

        try:
            with open(json_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        hosts.append({
                            "url": data.get("url"),
                            "host": data.get("host"),
                            "status_code": data.get("status_code"),
                            "title": data.get("title"),
                            "content_length": data.get("content_length"),
                            "server": data.get("server"),
                            "technologies": data.get("tech", []),
                            "method": data.get("method"),
                            "final_url": data.get("final_url")
                        })
        except Exception as e:
            logger.error(f"Failed to parse httpx output: {e}")

        return hosts
