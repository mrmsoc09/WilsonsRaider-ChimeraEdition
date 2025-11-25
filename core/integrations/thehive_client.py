"""TheHive Integration Client - Production-Grade Incident Response

Comprehensive TheHive REST API client for case management,
observables, tasks, and incident response workflows.
Version: 1.0.0
"""

import os
import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)


class CaseSeverity(Enum):
    """TheHive case severity levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class CaseStatus(Enum):
    """TheHive case status."""
    NEW = "New"
    IN_PROGRESS = "InProgress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class TLP(Enum):
    """Traffic Light Protocol levels."""
    WHITE = 0  # Unlimited disclosure
    GREEN = 1  # Community disclosure
    AMBER = 2  # Limited disclosure
    RED = 3    # Personal disclosure only


class TheHiveNotConfigured(Exception):
    """Raised when TheHive is not properly configured."""
    pass


class TheHiveClient:
    """Production-grade TheHive incident response client."""

    def __init__(self,
                 base_url: Optional[str] = None,
                 api_key: Optional[str] = None,
                 organization: str = "WilsonsRaider",
                 timeout: int = 30,
                 verify_ssl: bool = True):
        """
        Initialize TheHive client.

        Args:
            base_url: TheHive instance URL (e.g., http://thehive:9000)
            api_key: API key for authentication
            organization: Organization name
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
        """

        if httpx is None:
            raise TheHiveNotConfigured("httpx not installed. Install with: pip install httpx")

        self.base_url = (base_url or os.getenv("THEHIVE_URL", "http://localhost:9000")).rstrip("/")
        self.api_key = api_key or os.getenv("THEHIVE_API_KEY")
        self.organization = organization

        if not self.api_key:
            raise TheHiveNotConfigured(
                "THEHIVE_API_KEY not configured. Set via environment or constructor."
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

        logger.info(f"TheHiveClient initialized: base_url={self.base_url}, org={self.organization}")

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def health_check(self) -> bool:
        """Check TheHive server health."""
        try:
            response = self.client.get("/api/status")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    # Case Management

    def create_case(self,
                    title: str,
                    description: str,
                    severity: CaseSeverity = CaseSeverity.MEDIUM,
                    tlp: TLP = TLP.AMBER,
                    tags: Optional[List[str]] = None,
                    pap: int = 2,
                    flag: bool = False,
                    custom_fields: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new case in TheHive.

        Args:
            title: Case title
            description: Detailed description
            severity: Case severity (LOW/MEDIUM/HIGH/CRITICAL)
            tlp: Traffic Light Protocol level
            tags: List of tags (e.g., ['vulnerability', 'sqli'])
            pap: Permissible Actions Protocol (2 = default)
            flag: Flag case for attention
            custom_fields: Additional custom fields

        Returns:
            Created case object with case ID
        """
        try:
            case_data = {
                "title": title,
                "description": description,
                "severity": severity.value,
                "tlp": tlp.value,
                "pap": pap,
                "flag": flag,
                "tags": tags or [],
                "status": CaseStatus.NEW.value
            }

            if custom_fields:
                case_data["customFields"] = custom_fields

            response = self.client.post("/api/v1/case", json=case_data)
            response.raise_for_status()

            case = response.json()
            logger.info(f"Case created: {case.get('_id')} - {title}")
            return case

        except Exception as e:
            logger.error(f"Failed to create case: {e}")
            return None

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get case details."""
        try:
            response = self.client.get(f"/api/v1/case/{case_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get case {case_id}: {e}")
            return None

    def update_case(self, case_id: str, updates: Dict[str, Any]) -> bool:
        """Update case fields."""
        try:
            response = self.client.patch(f"/api/v1/case/{case_id}", json=updates)
            response.raise_for_status()
            logger.info(f"Case {case_id} updated")
            return True
        except Exception as e:
            logger.error(f"Failed to update case {case_id}: {e}")
            return False

    def close_case(self, case_id: str, resolution_status: str = "TruePositive",
                   summary: Optional[str] = None) -> bool:
        """Close a case with resolution."""
        try:
            updates = {
                "status": CaseStatus.CLOSED.value,
                "resolutionStatus": resolution_status,
                "endDate": int(datetime.utcnow().timestamp() * 1000)
            }

            if summary:
                updates["summary"] = summary

            return self.update_case(case_id, updates)
        except Exception as e:
            logger.error(f"Failed to close case {case_id}: {e}")
            return False

    def list_cases(self,
                   status: Optional[CaseStatus] = None,
                   severity: Optional[CaseSeverity] = None,
                   limit: int = 50) -> List[Dict[str, Any]]:
        """List cases with optional filters."""
        try:
            query = {
                "query": [{"_name": "listCase"}],
                "range": f"0-{limit}"
            }

            # Add filters
            filters = []
            if status:
                filters.append({"_field": "status", "_value": status.value})
            if severity:
                filters.append({"_field": "severity", "_value": severity.value})

            if filters:
                query["query"][0]["filters"] = filters

            response = self.client.post("/api/v1/query", json=query)
            response.raise_for_status()

            cases = response.json()
            logger.info(f"Retrieved {len(cases)} cases")
            return cases

        except Exception as e:
            logger.error(f"Failed to list cases: {e}")
            return []

    # Observable Management

    def add_observable(self,
                       case_id: str,
                       data: str,
                       dataType: str,
                       message: Optional[str] = None,
                       tlp: TLP = TLP.AMBER,
                       ioc: bool = False,
                       sighted: bool = False,
                       tags: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Add observable to case.

        Args:
            case_id: Target case ID
            data: Observable value (IP, domain, hash, etc.)
            dataType: Type (ip, domain, url, hash, filename, etc.)
            message: Description
            tlp: Traffic Light Protocol
            ioc: Mark as Indicator of Compromise
            sighted: Mark as sighted in environment
            tags: Additional tags

        Returns:
            Created observable object
        """
        try:
            observable_data = {
                "data": data,
                "dataType": dataType,
                "tlp": tlp.value,
                "ioc": ioc,
                "sighted": sighted,
                "tags": tags or []
            }

            if message:
                observable_data["message"] = message

            response = self.client.post(
                f"/api/v1/case/{case_id}/artifact",
                json=observable_data
            )
            response.raise_for_status()

            observable = response.json()
            logger.info(f"Observable added to case {case_id}: {dataType}={data}")
            return observable

        except Exception as e:
            logger.error(f"Failed to add observable: {e}")
            return None

    def get_observables(self, case_id: str) -> List[Dict[str, Any]]:
        """Get all observables for a case."""
        try:
            response = self.client.get(f"/api/v1/case/{case_id}/artifact")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get observables: {e}")
            return []

    # Task Management

    def create_task(self,
                    case_id: str,
                    title: str,
                    description: Optional[str] = None,
                    owner: Optional[str] = None,
                    status: str = "Waiting") -> Optional[Dict[str, Any]]:
        """Create a task in a case."""
        try:
            task_data = {
                "title": title,
                "status": status
            }

            if description:
                task_data["description"] = description
            if owner:
                task_data["owner"] = owner

            response = self.client.post(
                f"/api/v1/case/{case_id}/task",
                json=task_data
            )
            response.raise_for_status()

            task = response.json()
            logger.info(f"Task created in case {case_id}: {title}")
            return task

        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return None

    def update_task_status(self, task_id: str, status: str) -> bool:
        """Update task status (Waiting, InProgress, Completed, Cancel)."""
        try:
            response = self.client.patch(
                f"/api/v1/case/task/{task_id}",
                json={"status": status}
            )
            response.raise_for_status()
            logger.info(f"Task {task_id} status updated to {status}")
            return True
        except Exception as e:
            logger.error(f"Failed to update task: {e}")
            return False

    # Integration Helpers

    def create_case_from_finding(self, finding: Dict[str, Any]) -> Optional[str]:
        """
        Create TheHive case from WilsonsRaider finding.

        Args:
            finding: Finding dict with keys: name, description, severity,
                    target, confidence, tool, cvss, cwe, etc.

        Returns:
            Case ID if successful
        """
        severity_map = {
            "CRITICAL": CaseSeverity.CRITICAL,
            "HIGH": CaseSeverity.HIGH,
            "MEDIUM": CaseSeverity.MEDIUM,
            "LOW": CaseSeverity.LOW,
            "INFO": CaseSeverity.LOW
        }

        severity = severity_map.get(finding.get("severity", "MEDIUM"), CaseSeverity.MEDIUM)

        title = f"[WilsonsRaider] {finding.get('name', 'Security Finding')}"
        description = f"""
**Vulnerability**: {finding.get('name')}
**Target**: {finding.get('target', 'N/A')}
**Severity**: {finding.get('severity', 'N/A')}
**Confidence**: {finding.get('confidence', 'N/A')}
**Tool**: {finding.get('tool', 'N/A')}

**Description**:
{finding.get('description', 'No description available')}

**CVSS**: {finding.get('cvss', 'N/A')}
**CWE**: {finding.get('cwe', 'N/A')}

**Raw Evidence**:
```
{finding.get('raw_output', '')[:500]}
```
"""

        tags = ["wilsons-raider", "automated-scan"]
        if finding.get("tool"):
            tags.append(finding["tool"])
        if finding.get("category"):
            tags.append(finding["category"])

        custom_fields = {
            "confidence": {"float": finding.get("confidence", 0.0)},
            "scan_id": {"string": finding.get("scan_id", "")},
            "tool": {"string": finding.get("tool", "")}
        }

        case = self.create_case(
            title=title,
            description=description,
            severity=severity,
            tlp=TLP.AMBER,
            tags=tags,
            flag=(severity in [CaseSeverity.CRITICAL, CaseSeverity.HIGH]),
            custom_fields=custom_fields
        )

        if case:
            case_id = case.get("_id")

            # Add target as observable
            if finding.get("target"):
                self.add_observable(
                    case_id=case_id,
                    data=finding["target"],
                    dataType="url" if "http" in finding["target"] else "domain",
                    message="Vulnerable target",
                    ioc=True
                )

            # Create remediation task
            self.create_task(
                case_id=case_id,
                title="Verify and Remediate Vulnerability",
                description="1. Manually verify the finding\n2. Develop fix\n3. Deploy patch\n4. Re-scan to confirm"
            )

            return case_id

        return None

    async def create_case_async(self, title: str, description: str,
                                severity: CaseSeverity, **kwargs) -> Optional[Dict[str, Any]]:
        """Async version of create_case."""
        try:
            case_data = {
                "title": title,
                "description": description,
                "severity": severity.value,
                "tlp": kwargs.get("tlp", TLP.AMBER).value,
                "pap": kwargs.get("pap", 2),
                "flag": kwargs.get("flag", False),
                "tags": kwargs.get("tags", []),
                "status": CaseStatus.NEW.value
            }

            response = await self.async_client.post("/api/v1/case", json=case_data)
            response.raise_for_status()

            case = response.json()
            logger.info(f"Case created async: {case.get('_id')}")
            return case

        except Exception as e:
            logger.error(f"Failed to create case async: {e}")
            return None

    def close(self) -> None:
        """Cleanup HTTP clients."""
        self.client.close()
        logger.info("TheHiveClient closed")

    async def aclose(self) -> None:
        """Cleanup async HTTP client."""
        await self.async_client.aclose()
        logger.info("TheHiveClient async client closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()
