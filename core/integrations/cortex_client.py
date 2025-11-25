"""Cortex Integration Client - Production-Grade Threat Intelligence

Comprehensive Cortex REST API client for observable analysis,
threat intelligence enrichment, and IOC processing.
Version: 1.0.0
"""

import os
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)


class ObservableDataType(Enum):
    """Cortex observable data types."""
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    FQDN = "fqdn"
    MAIL = "mail"
    HASH = "hash"
    FILENAME = "filename"
    REGISTRY = "registry"
    USER_AGENT = "user-agent"
    URI_PATH = "uri_path"


class AnalyzerType(Enum):
    """Common Cortex analyzers."""
    VIRUSTOTAL = "VirusTotal_GetReport_3_0"
    ABUSEIPDB = "AbuseIPDB_1_0"
    SHODAN = "Shodan_Info_1_0"
    OTXQUERY = "OTXQuery_2_0"
    MAXMIND = "MaxMind_GeoIP_3_0"
    MISP = "MISP_2_1"
    PASSIVETOTAL = "PassiveTotal_Enrichment_2_0"
    THREATCROWD = "ThreatCrowd_1_0"
    URLHAUS = "URLhaus_2_0"
    HYBRID_ANALYSIS = "HybridAnalysis_GetReport_1_0"


class JobStatus(Enum):
    """Cortex job status."""
    WAITING = "Waiting"
    IN_PROGRESS = "InProgress"
    SUCCESS = "Success"
    FAILURE = "Failure"
    DELETED = "Deleted"


class TaxonomyLevel(Enum):
    """Cortex taxonomy levels (threat scoring)."""
    SAFE = "safe"
    INFO = "info"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"


class CortexNotConfigured(Exception):
    """Raised when Cortex is not properly configured."""
    pass


class CortexClient:
    """Production-grade Cortex threat intelligence client."""

    def __init__(self,
                 base_url: Optional[str] = None,
                 api_key: Optional[str] = None,
                 timeout: int = 60,
                 verify_ssl: bool = True):
        """
        Initialize Cortex client.

        Args:
            base_url: Cortex instance URL (e.g., http://cortex:9001)
            api_key: API key for authentication
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
        """

        if httpx is None:
            raise CortexNotConfigured("httpx not installed. Install with: pip install httpx")

        self.base_url = (base_url or os.getenv("CORTEX_URL", "http://localhost:9001")).rstrip("/")
        self.api_key = api_key or os.getenv("CORTEX_API_KEY")

        if not self.api_key:
            raise CortexNotConfigured(
                "CORTEX_API_KEY not configured. Set via environment or constructor."
            )

        # HTTP client configuration
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Initialize clients
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            verify=verify_ssl,
            headers=self._get_headers()
        )

        self.async_client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            verify=verify_ssl,
            headers=self._get_headers()
        )

        logger.info(f"CortexClient initialized: base_url={self.base_url}")

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def health_check(self) -> bool:
        """Check Cortex server health."""
        try:
            response = self.client.get("/api/status")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    # Analyzer Management

    def list_analyzers(self, data_type: Optional[ObservableDataType] = None) -> List[Dict[str, Any]]:
        """
        List available analyzers.

        Args:
            data_type: Filter by observable data type

        Returns:
            List of analyzer configurations
        """
        try:
            endpoint = "/api/analyzer"
            if data_type:
                endpoint += f"/{data_type.value}"

            response = self.client.get(endpoint)
            response.raise_for_status()

            analyzers = response.json()
            logger.info(f"Retrieved {len(analyzers)} analyzers")
            return analyzers

        except Exception as e:
            logger.error(f"Failed to list analyzers: {e}")
            return []

    def get_analyzer(self, analyzer_id: str) -> Optional[Dict[str, Any]]:
        """Get analyzer details."""
        try:
            response = self.client.get(f"/api/analyzer/{analyzer_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get analyzer {analyzer_id}: {e}")
            return None

    # Observable Analysis

    def analyze_observable(self,
                           data: str,
                           data_type: ObservableDataType,
                           analyzers: Optional[List[str]] = None,
                           tlp: int = 2,
                           pap: int = 2,
                           message: Optional[str] = None) -> Optional[str]:
        """
        Submit observable for analysis.

        Args:
            data: Observable value (IP, domain, hash, etc.)
            data_type: Type of observable
            analyzers: List of analyzer IDs to run (all if None)
            tlp: Traffic Light Protocol (0=WHITE, 1=GREEN, 2=AMBER, 3=RED)
            pap: Permissible Actions Protocol
            message: Optional description

        Returns:
            Job ID for tracking analysis
        """
        try:
            payload = {
                "data": data,
                "dataType": data_type.value,
                "tlp": tlp,
                "pap": pap
            }

            if analyzers:
                payload["analyzers"] = analyzers
            if message:
                payload["message"] = message

            response = self.client.post("/api/analyzer/_search", json=payload)
            response.raise_for_status()

            jobs = response.json()
            if jobs:
                job_id = jobs[0].get("id")
                logger.info(f"Observable analysis submitted: {data} ({data_type.value}) - job_id={job_id}")
                return job_id
            else:
                logger.warning(f"No suitable analyzers found for {data_type.value}")
                return None

        except Exception as e:
            logger.error(f"Failed to analyze observable: {e}")
            return None

    def run_analyzer(self,
                     analyzer_id: str,
                     data: str,
                     data_type: ObservableDataType,
                     tlp: int = 2) -> Optional[str]:
        """
        Run specific analyzer on observable.

        Args:
            analyzer_id: Analyzer ID to execute
            data: Observable value
            data_type: Observable data type
            tlp: Traffic Light Protocol

        Returns:
            Job ID
        """
        try:
            payload = {
                "data": data,
                "dataType": data_type.value,
                "tlp": tlp
            }

            response = self.client.post(f"/api/analyzer/{analyzer_id}/run", json=payload)
            response.raise_for_status()

            job = response.json()
            job_id = job.get("id")
            logger.info(f"Analyzer {analyzer_id} running: job_id={job_id}")
            return job_id

        except Exception as e:
            logger.error(f"Failed to run analyzer {analyzer_id}: {e}")
            return None

    # Job Management

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job details and status."""
        try:
            response = self.client.get(f"/api/job/{job_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None

    def get_job_report(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job analysis report."""
        try:
            response = self.client.get(f"/api/job/{job_id}/report")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get job report {job_id}: {e}")
            return None

    def wait_for_job(self,
                     job_id: str,
                     timeout: int = 300,
                     poll_interval: int = 5) -> Dict[str, Any]:
        """
        Wait for job completion and return report.

        Args:
            job_id: Job ID to monitor
            timeout: Maximum wait time in seconds
            poll_interval: Polling interval in seconds

        Returns:
            Job report with analysis results
        """
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            job = self.get_job(job_id)

            if not job:
                return {"error": "Job not found", "status": "unknown"}

            status = job.get("status")

            if status in [JobStatus.SUCCESS.value, JobStatus.FAILURE.value]:
                logger.info(f"Job {job_id} completed: {status}")
                if status == JobStatus.SUCCESS.value:
                    return self.get_job_report(job_id) or job
                return job

            logger.debug(f"Job {job_id} still running: {status}")
            time.sleep(poll_interval)

        logger.warning(f"Job {job_id} wait timeout")
        return {"error": "Timeout waiting for job", "status": "timeout"}

    def delete_job(self, job_id: str) -> bool:
        """Delete a job."""
        try:
            response = self.client.delete(f"/api/job/{job_id}")
            response.raise_for_status()
            logger.info(f"Job {job_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False

    def list_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List recent jobs."""
        try:
            query = {
                "query": {},
                "range": f"0-{limit}",
                "sort": ["-createdAt"]
            }

            response = self.client.post("/api/job/_search", json=query)
            response.raise_for_status()

            jobs = response.json()
            logger.info(f"Retrieved {len(jobs)} jobs")
            return jobs

        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            return []

    # High-Level Analysis Functions

    def enrich_ip(self, ip_address: str,
                  analyzers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enrich IP address with threat intelligence.

        Args:
            ip_address: IP address to analyze
            analyzers: Specific analyzers (defaults to common IP analyzers)

        Returns:
            Enrichment results with reputation, geolocation, threat intel
        """
        if not analyzers:
            # Default IP analyzers
            analyzers = [
                "AbuseIPDB_1_0",
                "Shodan_Info_1_0",
                "MaxMind_GeoIP_3_0",
                "OTXQuery_2_0"
            ]

        job_id = self.analyze_observable(
            data=ip_address,
            data_type=ObservableDataType.IP,
            analyzers=analyzers
        )

        if not job_id:
            return {"error": "Failed to submit analysis"}

        return self.wait_for_job(job_id)

    def enrich_domain(self, domain: str,
                      analyzers: Optional[List[str]] = None) -> Dict[str, Any]:
        """Enrich domain with threat intelligence."""
        if not analyzers:
            analyzers = [
                "VirusTotal_GetReport_3_0",
                "OTXQuery_2_0",
                "PassiveTotal_Enrichment_2_0",
                "URLhaus_2_0"
            ]

        job_id = self.analyze_observable(
            data=domain,
            data_type=ObservableDataType.DOMAIN,
            analyzers=analyzers
        )

        if not job_id:
            return {"error": "Failed to submit analysis"}

        return self.wait_for_job(job_id)

    def enrich_hash(self, file_hash: str,
                    analyzers: Optional[List[str]] = None) -> Dict[str, Any]:
        """Enrich file hash with threat intelligence."""
        if not analyzers:
            analyzers = [
                "VirusTotal_GetReport_3_0",
                "OTXQuery_2_0",
                "HybridAnalysis_GetReport_1_0"
            ]

        job_id = self.analyze_observable(
            data=file_hash,
            data_type=ObservableDataType.HASH,
            analyzers=analyzers
        )

        if not job_id:
            return {"error": "Failed to submit analysis"}

        return self.wait_for_job(job_id)

    def enrich_url(self, url: str,
                   analyzers: Optional[List[str]] = None) -> Dict[str, Any]:
        """Enrich URL with threat intelligence."""
        if not analyzers:
            analyzers = [
                "VirusTotal_GetReport_3_0",
                "URLhaus_2_0",
                "OTXQuery_2_0"
            ]

        job_id = self.analyze_observable(
            data=url,
            data_type=ObservableDataType.URL,
            analyzers=analyzers
        )

        if not job_id:
            return {"error": "Failed to submit analysis"}

        return self.wait_for_job(job_id)

    async def enrich_observable_async(self,
                                      data: str,
                                      data_type: ObservableDataType,
                                      analyzers: Optional[List[str]] = None) -> Dict[str, Any]:
        """Async version of observable enrichment."""
        try:
            payload = {
                "data": data,
                "dataType": data_type.value,
                "tlp": 2
            }

            if analyzers:
                payload["analyzers"] = analyzers

            response = await self.async_client.post("/api/analyzer/_search", json=payload)
            response.raise_for_status()

            jobs = response.json()
            if jobs:
                job_id = jobs[0].get("id")
                logger.info(f"Observable analysis submitted async: {data} - job_id={job_id}")
                # Note: Caller needs to wait for job separately
                return {"job_id": job_id, "status": "submitted"}
            else:
                return {"error": "No suitable analyzers found"}

        except Exception as e:
            logger.error(f"Failed to analyze observable async: {e}")
            return {"error": str(e)}

    async def batch_enrich_observables(self,
                                       observables: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Batch enrich multiple observables concurrently.

        Args:
            observables: List of dicts with 'data' and 'data_type' keys

        Returns:
            List of enrichment results
        """
        tasks = [
            self.enrich_observable_async(
                data=obs["data"],
                data_type=ObservableDataType(obs["data_type"])
            )
            for obs in observables
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [
            result if not isinstance(result, Exception) else {"error": str(result)}
            for result in results
        ]

    # Integration Helpers

    def enrich_finding(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich WilsonsRaider finding with threat intelligence.

        Args:
            finding: Finding dict with target, IP, domain, hashes, etc.

        Returns:
            Enriched finding with Cortex intelligence
        """
        enrichment = {
            "target": None,
            "ips": [],
            "domains": [],
            "hashes": []
        }

        # Extract and enrich target
        target = finding.get("target", "")
        if target:
            # Determine if target is IP, domain, or URL
            import re
            ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'

            if re.match(ip_pattern, target.split(":")[0]):  # IP address
                enrichment["target"] = self.enrich_ip(target.split(":")[0])
            elif "http" in target:  # URL
                enrichment["target"] = self.enrich_url(target)
            else:  # Domain
                enrichment["target"] = self.enrich_domain(target.split(":")[0])

        # Enrich additional observables if present
        if finding.get("ips"):
            for ip in finding["ips"][:5]:  # Limit to 5
                enrichment["ips"].append(self.enrich_ip(ip))

        if finding.get("domains"):
            for domain in finding["domains"][:5]:
                enrichment["domains"].append(self.enrich_domain(domain))

        if finding.get("hashes"):
            for file_hash in finding["hashes"][:5]:
                enrichment["hashes"].append(self.enrich_hash(file_hash))

        return enrichment

    def extract_taxonomy(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract taxonomy (reputation) from Cortex report.

        Returns:
            Dict with level (safe/suspicious/malicious) and score
        """
        taxonomies = report.get("taxonomies", [])

        if not taxonomies:
            return {"level": "unknown", "score": 0, "details": []}

        # Aggregate taxonomies
        malicious_count = 0
        suspicious_count = 0
        safe_count = 0

        for taxonomy in taxonomies:
            level = taxonomy.get("level", "").lower()
            if level == TaxonomyLevel.MALICIOUS.value:
                malicious_count += 1
            elif level == TaxonomyLevel.SUSPICIOUS.value:
                suspicious_count += 1
            elif level == TaxonomyLevel.SAFE.value:
                safe_count += 1

        # Determine overall reputation
        if malicious_count > 0:
            overall_level = TaxonomyLevel.MALICIOUS.value
            score = 0.9 + (malicious_count * 0.01)  # 0.9-1.0
        elif suspicious_count > 0:
            overall_level = TaxonomyLevel.SUSPICIOUS.value
            score = 0.6 + (suspicious_count * 0.05)  # 0.6-0.85
        elif safe_count > 0:
            overall_level = TaxonomyLevel.SAFE.value
            score = 0.1 + (safe_count * 0.01)  # 0.1-0.3
        else:
            overall_level = "info"
            score = 0.5

        return {
            "level": overall_level,
            "score": min(score, 1.0),
            "malicious": malicious_count,
            "suspicious": suspicious_count,
            "safe": safe_count,
            "details": taxonomies
        }

    def close(self) -> None:
        """Cleanup HTTP clients."""
        self.client.close()
        logger.info("CortexClient closed")

    async def aclose(self) -> None:
        """Cleanup async HTTP client."""
        await self.async_client.aclose()
        logger.info("CortexClient async client closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()
