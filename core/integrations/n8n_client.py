"""n8n Workflow Automation Client - Production-Grade Integration

Comprehensive n8n REST API client for workflow orchestration,
execution monitoring, and webhook management.
Version: 2.0.0
"""

import os
import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)

class N8nNotConfigured(Exception):
    """Raised when n8n is not properly configured."""
    pass

class N8nClient:
    """Production-grade n8n workflow automation client."""
    
    def __init__(self,
                 base_url: Optional[str] = None,
                 api_key: Optional[str] = None,
                 timeout: int = 30,
                 max_retries: int = 3):
        
        if httpx is None:
            raise N8nNotConfigured("httpx not installed. Install with: pip install httpx")
        
        self.base_url = (base_url or os.getenv("N8N_BASE_URL", "http://localhost:5678")).rstrip("/")
        self.api_key = api_key or os.getenv("N8N_API_KEY")
        
        if not self.api_key:
            logger.warning("N8N_API_KEY not configured, some operations may fail")
        
        # HTTP client configuration
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize clients
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers=self._get_headers()
        )
        
        self.async_client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers=self._get_headers()
        )
        
        logger.info(f"N8nClient initialized: base_url={self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["X-N8N-API-KEY"] = self.api_key
        
        return headers
    
    def health_check(self) -> bool:
        """Check n8n server health."""
        try:
            response = self.client.get("/healthz")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    # Workflow Management
    
    def list_workflows(self, active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """List all workflows."""
        try:
            params = {}
            if active is not None:
                params["active"] = str(active).lower()
            
            response = self.client.get("/workflows", params=params)
            response.raise_for_status()
            
            workflows = response.json().get("data", [])
            logger.info(f"Retrieved {len(workflows)} workflows")
            return workflows
        
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return []
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow details."""
        try:
            response = self.client.get(f"/workflows/{workflow_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get workflow {workflow_id}: {e}")
            return None
    
    def activate_workflow(self, workflow_id: str) -> bool:
        """Activate a workflow."""
        try:
            response = self.client.patch(
                f"/workflows/{workflow_id}",
                json={"active": True}
            )
            response.raise_for_status()
            logger.info(f"Workflow {workflow_id} activated")
            return True
        except Exception as e:
            logger.error(f"Failed to activate workflow {workflow_id}: {e}")
            return False
    
    def deactivate_workflow(self, workflow_id: str) -> bool:
        """Deactivate a workflow."""
        try:
            response = self.client.patch(
                f"/workflows/{workflow_id}",
                json={"active": False}
            )
            response.raise_for_status()
            logger.info(f"Workflow {workflow_id} deactivated")
            return True
        except Exception as e:
            logger.error(f"Failed to deactivate workflow {workflow_id}: {e}")
            return False
    
    # Execution Management
    
    def trigger_workflow(self, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger workflow execution via webhook."""
        try:
            response = self.client.post(
                f"/webhook/{workflow_id}",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"status": response.status_code}
            logger.info(f"Workflow {workflow_id} triggered successfully")
            return result
        
        except Exception as e:
            logger.error(f"Failed to trigger workflow {workflow_id}: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def trigger_workflow_async(self, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger workflow execution asynchronously."""
        try:
            response = await self.async_client.post(
                f"/webhook/{workflow_id}",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"status": response.status_code}
            logger.info(f"Workflow {workflow_id} triggered async")
            return result
        
        except Exception as e:
            logger.error(f"Failed to trigger workflow {workflow_id}: {e}")
            return {"error": str(e), "status": "failed"}
    
    def list_executions(self, workflow_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """List workflow executions."""
        try:
            params = {"limit": limit}
            if workflow_id:
                params["workflowId"] = workflow_id
            
            response = self.client.get("/executions", params=params)
            response.raise_for_status()
            
            executions = response.json().get("data", [])
            logger.info(f"Retrieved {len(executions)} executions")
            return executions
        
        except Exception as e:
            logger.error(f"Failed to list executions: {e}")
            return []
    
    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution details."""
        try:
            response = self.client.get(f"/executions/{execution_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get execution {execution_id}: {e}")
            return None
    
    def get_execution_status(self, execution_id: str) -> Optional[str]:
        """Get execution status."""
        execution = self.get_execution(execution_id)
        if execution:
            return execution.get("status")
        return None
    
    def wait_for_execution(self, execution_id: str, timeout: int = 300, poll_interval: int = 5) -> Dict[str, Any]:
        """Wait for execution to complete."""
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).total_seconds() < timeout:
            execution = self.get_execution(execution_id)
            
            if not execution:
                return {"error": "Execution not found", "status": "unknown"}
            
            status = execution.get("status")
            
            if status in ["success", "error", "canceled"]:
                logger.info(f"Execution {execution_id} completed: {status}")
                return execution
            
            logger.debug(f"Execution {execution_id} still running: {status}")
            asyncio.sleep(poll_interval)
        
        logger.warning(f"Execution {execution_id} wait timeout")
        return {"error": "Timeout waiting for execution", "status": "timeout"}
    
    # Webhook Management
    
    def test_webhook(self, workflow_id: str, test_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Test webhook with payload."""
        try:
            response = self.client.post(
                f"/webhook-test/{workflow_id}",
                json=test_payload
            )
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"status": response.status_code}
            logger.info(f"Webhook test for {workflow_id} successful")
            return result
        
        except Exception as e:
            logger.error(f"Webhook test failed for {workflow_id}: {e}")
            return {"error": str(e), "status": "failed"}
    
    # Batch Operations
    
    async def trigger_workflows_batch(self, triggers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Trigger multiple workflows concurrently."""
        tasks = [
            self.trigger_workflow_async(trigger["workflow_id"], trigger.get("payload", {}))
            for trigger in triggers
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) else {"error": str(result), "status": "failed"}
            for result in results
        ]
    
    def close(self) -> None:
        """Cleanup HTTP clients."""
        self.client.close()
        logger.info("N8nClient closed")
    
    async def aclose(self) -> None:
        """Cleanup async HTTP client."""
        await self.async_client.aclose()
        logger.info("N8nClient async client closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()
