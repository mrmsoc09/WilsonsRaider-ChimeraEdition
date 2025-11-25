"""Shuffle Integration Client - Production-Grade SOAR Platform

Comprehensive Shuffle REST API client for workflow orchestration,
playbook execution, and security automation (SOAR).
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


class WorkflowStatus(Enum):
    """Shuffle workflow execution status."""
    WAITING = "WAITING"
    EXECUTING = "EXECUTING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ABORTED = "ABORTED"
    SKIPPED = "SKIPPED"


class ShuffleNotConfigured(Exception):
    """Raised when Shuffle is not properly configured."""
    pass


class ShuffleClient:
    """Production-grade Shuffle SOAR integration client."""

    def __init__(self,
                 base_url: Optional[str] = None,
                 api_key: Optional[str] = None,
                 timeout: int = 60,
                 verify_ssl: bool = True):
        """
        Initialize Shuffle client.

        Args:
            base_url: Shuffle instance URL (e.g., https://shuffle:3001)
            api_key: API key for authentication
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
        """

        if httpx is None:
            raise ShuffleNotConfigured("httpx not installed. Install with: pip install httpx")

        self.base_url = (base_url or os.getenv("SHUFFLE_URL", "https://localhost:3001")).rstrip("/")
        self.api_key = api_key or os.getenv("SHUFFLE_API_KEY")

        if not self.api_key:
            raise ShuffleNotConfigured(
                "SHUFFLE_API_KEY not configured. Set via environment or constructor."
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

        logger.info(f"ShuffleClient initialized: base_url={self.base_url}")

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def health_check(self) -> bool:
        """Check Shuffle server health."""
        try:
            response = self.client.get("/api/v1/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    # Workflow Management

    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows."""
        try:
            response = self.client.get("/api/v1/workflows")
            response.raise_for_status()

            workflows = response.json()
            if isinstance(workflows, list):
                logger.info(f"Retrieved {len(workflows)} workflows")
                return workflows
            else:
                return workflows.get("data", [])

        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return []

    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow details."""
        try:
            response = self.client.get(f"/api/v1/workflows/{workflow_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get workflow {workflow_id}: {e}")
            return None

    def create_workflow(self,
                        name: str,
                        description: str = "",
                        tags: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Create a new workflow."""
        try:
            workflow_data = {
                "name": name,
                "description": description,
                "tags": tags or []
            }

            response = self.client.post("/api/v1/workflows", json=workflow_data)
            response.raise_for_status()

            workflow = response.json()
            logger.info(f"Workflow created: {workflow.get('id')} - {name}")
            return workflow

        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            return None

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        try:
            response = self.client.delete(f"/api/v1/workflows/{workflow_id}")
            response.raise_for_status()
            logger.info(f"Workflow {workflow_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to delete workflow {workflow_id}: {e}")
            return False

    # Workflow Execution

    def execute_workflow(self,
                         workflow_id: str,
                         execution_argument: Optional[Dict[str, Any]] = None,
                         start_node: Optional[str] = None) -> Optional[str]:
        """
        Execute a workflow (run playbook).

        Args:
            workflow_id: Target workflow ID
            execution_argument: Input data for workflow execution
            start_node: Optional specific node to start from

        Returns:
            Execution ID if successful
        """
        try:
            payload = {
                "execution_argument": execution_argument or {},
                "start": start_node or ""
            }

            response = self.client.post(
                f"/api/v1/workflows/{workflow_id}/execute",
                json=payload
            )
            response.raise_for_status()

            result = response.json()
            execution_id = result.get("execution_id") or result.get("id")
            logger.info(f"Workflow {workflow_id} executed: execution_id={execution_id}")
            return execution_id

        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            return None

    def get_execution_result(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow execution result."""
        try:
            response = self.client.get(f"/api/v1/workflows/executions/{execution_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get execution {execution_id}: {e}")
            return None

    def list_executions(self,
                        workflow_id: Optional[str] = None,
                        limit: int = 50) -> List[Dict[str, Any]]:
        """List workflow executions."""
        try:
            params = {"top": limit}
            endpoint = f"/api/v1/workflows/{workflow_id}/executions" if workflow_id else "/api/v1/workflows/executions"

            response = self.client.get(endpoint, params=params)
            response.raise_for_status()

            executions = response.json()
            if isinstance(executions, list):
                logger.info(f"Retrieved {len(executions)} executions")
                return executions
            else:
                return executions.get("data", [])

        except Exception as e:
            logger.error(f"Failed to list executions: {e}")
            return []

    def abort_execution(self, execution_id: str) -> bool:
        """Abort a running workflow execution."""
        try:
            response = self.client.post(f"/api/v1/workflows/executions/{execution_id}/abort")
            response.raise_for_status()
            logger.info(f"Execution {execution_id} aborted")
            return True
        except Exception as e:
            logger.error(f"Failed to abort execution {execution_id}: {e}")
            return False

    def wait_for_execution(self,
                           execution_id: str,
                           timeout: int = 300,
                           poll_interval: int = 5) -> Dict[str, Any]:
        """
        Wait for workflow execution to complete.

        Args:
            execution_id: Execution ID to monitor
            timeout: Maximum wait time in seconds
            poll_interval: Polling interval in seconds

        Returns:
            Execution result with status
        """
        import time
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            result = self.get_execution_result(execution_id)

            if not result:
                return {"error": "Execution not found", "status": "unknown"}

            status = result.get("status", "").upper()

            if status in [WorkflowStatus.SUCCESS.value, WorkflowStatus.FAILURE.value,
                          WorkflowStatus.ABORTED.value, WorkflowStatus.SKIPPED.value]:
                logger.info(f"Execution {execution_id} completed: {status}")
                return result

            logger.debug(f"Execution {execution_id} still running: {status}")
            time.sleep(poll_interval)

        logger.warning(f"Execution {execution_id} wait timeout")
        return {"error": "Timeout waiting for execution", "status": "timeout"}

    # App Management

    def list_apps(self) -> List[Dict[str, Any]]:
        """List available Shuffle apps (integrations)."""
        try:
            response = self.client.get("/api/v1/apps")
            response.raise_for_status()

            apps = response.json()
            if isinstance(apps, list):
                logger.info(f"Retrieved {len(apps)} apps")
                return apps
            else:
                return apps.get("data", [])

        except Exception as e:
            logger.error(f"Failed to list apps: {e}")
            return []

    def get_app(self, app_name: str, app_version: str = "1.0.0") -> Optional[Dict[str, Any]]:
        """Get app details."""
        try:
            response = self.client.get(f"/api/v1/apps/{app_name}/{app_version}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get app {app_name}: {e}")
            return None

    # Integration Helpers

    def trigger_incident_response_playbook(self,
                                           finding: Dict[str, Any],
                                           playbook_id: Optional[str] = None) -> Optional[str]:
        """
        Trigger incident response playbook for a finding.

        Args:
            finding: WilsonsRaider finding dict
            playbook_id: Specific playbook to trigger (auto-detect if not provided)

        Returns:
            Execution ID if successful
        """
        # Map severity to playbook
        if not playbook_id:
            severity = finding.get("severity", "MEDIUM")
            # Playbook naming convention: incident-response-{severity}
            playbook_name = f"incident-response-{severity.lower()}"
            workflows = self.list_workflows()
            for wf in workflows:
                if wf.get("name", "").lower() == playbook_name:
                    playbook_id = wf.get("id")
                    break

        if not playbook_id:
            logger.warning("No suitable playbook found for incident response")
            return None

        # Prepare execution data
        execution_data = {
            "finding": {
                "name": finding.get("name"),
                "severity": finding.get("severity"),
                "target": finding.get("target"),
                "confidence": finding.get("confidence"),
                "tool": finding.get("tool"),
                "description": finding.get("description"),
                "cwe": finding.get("cwe"),
                "cvss": finding.get("cvss")
            },
            "timestamp": datetime.utcnow().isoformat(),
            "source": "wilsons-raider"
        }

        return self.execute_workflow(playbook_id, execution_argument=execution_data)

    def trigger_vulnerability_triage_workflow(self, findings: List[Dict[str, Any]]) -> Optional[str]:
        """Trigger vulnerability triage workflow with multiple findings."""
        workflows = self.list_workflows()
        triage_workflow_id = None

        for wf in workflows:
            if "vulnerability-triage" in wf.get("name", "").lower():
                triage_workflow_id = wf.get("id")
                break

        if not triage_workflow_id:
            logger.warning("Vulnerability triage workflow not found")
            return None

        execution_data = {
            "findings": findings,
            "count": len(findings),
            "timestamp": datetime.utcnow().isoformat(),
            "source": "wilsons-raider"
        }

        return self.execute_workflow(triage_workflow_id, execution_argument=execution_data)

    def trigger_threat_hunting_workflow(self,
                                        indicators: List[str],
                                        ioc_type: str = "mixed") -> Optional[str]:
        """Trigger threat hunting workflow with IOCs."""
        workflows = self.list_workflows()
        hunt_workflow_id = None

        for wf in workflows:
            if "threat-hunt" in wf.get("name", "").lower():
                hunt_workflow_id = wf.get("id")
                break

        if not hunt_workflow_id:
            logger.warning("Threat hunting workflow not found")
            return None

        execution_data = {
            "indicators": indicators,
            "ioc_type": ioc_type,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "wilsons-raider"
        }

        return self.execute_workflow(hunt_workflow_id, execution_argument=execution_data)

    def send_notification(self,
                          message: str,
                          title: str = "WilsonsRaider Alert",
                          channels: Optional[List[str]] = None) -> Optional[str]:
        """
        Send notification via Shuffle notification workflow.

        Args:
            message: Notification message
            title: Notification title
            channels: Target channels (slack, email, pagerduty, etc.)

        Returns:
            Execution ID if successful
        """
        workflows = self.list_workflows()
        notify_workflow_id = None

        for wf in workflows:
            if "notification" in wf.get("name", "").lower():
                notify_workflow_id = wf.get("id")
                break

        if not notify_workflow_id:
            logger.warning("Notification workflow not found")
            return None

        execution_data = {
            "title": title,
            "message": message,
            "channels": channels or ["slack"],
            "timestamp": datetime.utcnow().isoformat(),
            "source": "wilsons-raider"
        }

        return self.execute_workflow(notify_workflow_id, execution_argument=execution_data)

    async def execute_workflow_async(self,
                                     workflow_id: str,
                                     execution_argument: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Async version of execute_workflow."""
        try:
            payload = {
                "execution_argument": execution_argument or {},
                "start": ""
            }

            response = await self.async_client.post(
                f"/api/v1/workflows/{workflow_id}/execute",
                json=payload
            )
            response.raise_for_status()

            result = response.json()
            execution_id = result.get("execution_id") or result.get("id")
            logger.info(f"Workflow {workflow_id} executed async: execution_id={execution_id}")
            return execution_id

        except Exception as e:
            logger.error(f"Failed to execute workflow async {workflow_id}: {e}")
            return None

    async def execute_workflows_batch(self,
                                      executions: List[Dict[str, Any]]) -> List[Optional[str]]:
        """
        Execute multiple workflows concurrently.

        Args:
            executions: List of dicts with 'workflow_id' and 'execution_argument'

        Returns:
            List of execution IDs
        """
        tasks = [
            self.execute_workflow_async(
                execution["workflow_id"],
                execution.get("execution_argument")
            )
            for execution in executions
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [
            result if not isinstance(result, Exception) else None
            for result in results
        ]

    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get workflow execution statistics."""
        try:
            executions = self.list_executions(limit=500)

            stats = {
                "total_executions": len(executions),
                "success": 0,
                "failure": 0,
                "running": 0,
                "aborted": 0
            }

            for execution in executions:
                status = execution.get("status", "").upper()
                if status == WorkflowStatus.SUCCESS.value:
                    stats["success"] += 1
                elif status == WorkflowStatus.FAILURE.value:
                    stats["failure"] += 1
                elif status in [WorkflowStatus.EXECUTING.value, WorkflowStatus.WAITING.value]:
                    stats["running"] += 1
                elif status == WorkflowStatus.ABORTED.value:
                    stats["aborted"] += 1

            return stats

        except Exception as e:
            logger.error(f"Failed to get workflow statistics: {e}")
            return {"error": str(e)}

    def close(self) -> None:
        """Cleanup HTTP clients."""
        self.client.close()
        logger.info("ShuffleClient closed")

    async def aclose(self) -> None:
        """Cleanup async HTTP client."""
        await self.async_client.aclose()
        logger.info("ShuffleClient async client closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()
