"""Enhanced Dashboard API - Unified Security Operations Center

Comprehensive dashboard API aggregating data from all integrated platforms:
- TheHive (Incident Response)
- Wazuh (SIEM)
- Shuffle (SOAR)
- Cortex (Threat Intelligence)
- WilsonsRaider Core (Scanning)

Version: 1.0.0
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import integration clients
from core.integrations.thehive_client import TheHiveClient, CaseSeverity, CaseStatus
from core.integrations.wazuh_client import WazuhClient, AlertLevel
from core.integrations.shuffle_client import ShuffleClient
from core.integrations.cortex_client import CortexClient, ObservableDataType
from core.integrations.n8n_client import N8nClient

# Import core managers
from core.managers.scanning_manager import ScanningManager
from core.managers.validation_manager import ValidationManager
from core.managers.reporting_manager import ReportingManager
from core.managers.job_manager import JobManager

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="WilsonsRaider Command Center",
    description="Unified Security Operations Dashboard",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections for real-time updates
active_connections: List[WebSocket] = []


# Pydantic Models
class ScanRequest(BaseModel):
    target: str
    scan_type: str
    opsec_level: str = "medium"


class FindingEnrichmentRequest(BaseModel):
    finding_id: str
    enrich_with: List[str] = ["cortex", "thehive"]


# Helper Functions
def get_integration_clients() -> Dict[str, Any]:
    """Get all integration clients with error handling."""
    clients = {}

    try:
        clients["thehive"] = TheHiveClient()
    except Exception as e:
        logger.warning(f"TheHive not configured: {e}")
        clients["thehive"] = None

    try:
        clients["wazuh"] = WazuhClient()
    except Exception as e:
        logger.warning(f"Wazuh not configured: {e}")
        clients["wazuh"] = None

    try:
        clients["shuffle"] = ShuffleClient()
    except Exception as e:
        logger.warning(f"Shuffle not configured: {e}")
        clients["shuffle"] = None

    try:
        clients["cortex"] = CortexClient()
    except Exception as e:
        logger.warning(f"Cortex not configured: {e}")
        clients["cortex"] = None

    try:
        clients["n8n"] = N8nClient()
    except Exception as e:
        logger.warning(f"n8n not configured: {e}")
        clients["n8n"] = None

    return clients


async def broadcast_update(message: Dict[str, Any]):
    """Broadcast update to all connected WebSocket clients."""
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            disconnected.append(connection)

    # Remove disconnected clients
    for conn in disconnected:
        active_connections.remove(conn)


# Health & Status Endpoints

@app.get("/api/health")
async def health_check():
    """Overall platform health check."""
    clients = get_integration_clients()

    health_status = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "integrations": {
            "thehive": clients["thehive"].health_check() if clients["thehive"] else False,
            "wazuh": clients["wazuh"].health_check() if clients["wazuh"] else False,
            "shuffle": clients["shuffle"].health_check() if clients["shuffle"] else False,
            "cortex": clients["cortex"].health_check() if clients["cortex"] else False,
            "n8n": clients["n8n"].health_check() if clients["n8n"] else False
        }
    }

    # Determine overall status
    if all(health_status["integrations"].values()):
        health_status["status"] = "healthy"
    elif any(health_status["integrations"].values()):
        health_status["status"] = "degraded"
    else:
        health_status["status"] = "unavailable"

    return health_status


@app.get("/api/dashboard/overview")
async def get_dashboard_overview():
    """Get comprehensive dashboard overview with all metrics."""
    clients = get_integration_clients()

    overview = {
        "timestamp": datetime.utcnow().isoformat(),
        "active_scans": 0,
        "findings_today": 0,
        "critical_cases": 0,
        "wazuh_alerts": 0,
        "shuffle_workflows_running": 0,
        "integrations_status": {}
    }

    # Get active scans (from job manager or state)
    try:
        job_manager = JobManager()
        overview["active_scans"] = len([j for j in job_manager.queue if j.get("status") == "running"])
    except Exception as e:
        logger.error(f"Failed to get active scans: {e}")

    # Get TheHive critical cases
    if clients["thehive"]:
        try:
            critical_cases = clients["thehive"].list_cases(
                status=CaseStatus.NEW,
                severity=CaseSeverity.CRITICAL,
                limit=100
            )
            overview["critical_cases"] = len(critical_cases)
            overview["integrations_status"]["thehive"] = "connected"
        except Exception as e:
            logger.error(f"Failed to get TheHive cases: {e}")
            overview["integrations_status"]["thehive"] = "error"

    # Get Wazuh alerts
    if clients["wazuh"]:
        try:
            alert_summary = clients["wazuh"].get_alert_summary()
            overview["wazuh_alerts"] = alert_summary.get("total", 0)
            overview["integrations_status"]["wazuh"] = "connected"
        except Exception as e:
            logger.error(f"Failed to get Wazuh alerts: {e}")
            overview["integrations_status"]["wazuh"] = "error"

    # Get Shuffle workflow status
    if clients["shuffle"]:
        try:
            stats = clients["shuffle"].get_workflow_statistics()
            overview["shuffle_workflows_running"] = stats.get("running", 0)
            overview["integrations_status"]["shuffle"] = "connected"
        except Exception as e:
            logger.error(f"Failed to get Shuffle stats: {e}")
            overview["integrations_status"]["shuffle"] = "error"

    return overview


# TheHive Endpoints

@app.get("/api/thehive/cases")
async def list_thehive_cases(status: Optional[str] = None, limit: int = 50):
    """List TheHive cases."""
    clients = get_integration_clients()
    if not clients["thehive"]:
        raise HTTPException(status_code=503, detail="TheHive not configured")

    try:
        case_status = CaseStatus[status.upper()] if status else None
        cases = clients["thehive"].list_cases(status=case_status, limit=limit)
        return {"cases": cases, "count": len(cases)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/thehive/cases/{case_id}")
async def get_thehive_case(case_id: str):
    """Get specific TheHive case."""
    clients = get_integration_clients()
    if not clients["thehive"]:
        raise HTTPException(status_code=503, detail="TheHive not configured")

    case = clients["thehive"].get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Get observables
    observables = clients["thehive"].get_observables(case_id)

    return {
        "case": case,
        "observables": observables
    }


@app.post("/api/thehive/cases")
async def create_thehive_case(finding: Dict[str, Any]):
    """Create TheHive case from finding."""
    clients = get_integration_clients()
    if not clients["thehive"]:
        raise HTTPException(status_code=503, detail="TheHive not configured")

    case_id = clients["thehive"].create_case_from_finding(finding)
    if not case_id:
        raise HTTPException(status_code=500, detail="Failed to create case")

    # Broadcast update
    await broadcast_update({
        "type": "case_created",
        "case_id": case_id,
        "severity": finding.get("severity")
    })

    return {"case_id": case_id, "status": "created"}


# Wazuh Endpoints

@app.get("/api/wazuh/alerts")
async def get_wazuh_alerts(limit: int = 100, rule_level: Optional[int] = None):
    """Get Wazuh alerts."""
    clients = get_integration_clients()
    if not clients["wazuh"]:
        raise HTTPException(status_code=503, detail="Wazuh not configured")

    try:
        alerts = clients["wazuh"].get_alerts(limit=limit, rule_level=rule_level)
        return {"alerts": alerts, "count": len(alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wazuh/summary")
async def get_wazuh_summary():
    """Get Wazuh security events summary."""
    clients = get_integration_clients()
    if not clients["wazuh"]:
        raise HTTPException(status_code=503, detail="Wazuh not configured")

    try:
        summary = clients["wazuh"].get_security_events_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wazuh/agents")
async def list_wazuh_agents(status: Optional[str] = None):
    """List Wazuh agents."""
    clients = get_integration_clients()
    if not clients["wazuh"]:
        raise HTTPException(status_code=503, detail="Wazuh not configured")

    try:
        agents = clients["wazuh"].list_agents(status=status, limit=500)
        return {"agents": agents, "count": len(agents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Shuffle Endpoints

@app.get("/api/shuffle/workflows")
async def list_shuffle_workflows():
    """List Shuffle workflows."""
    clients = get_integration_clients()
    if not clients["shuffle"]:
        raise HTTPException(status_code=503, detail="Shuffle not configured")

    try:
        workflows = clients["shuffle"].list_workflows()
        return {"workflows": workflows, "count": len(workflows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/shuffle/workflows/{workflow_id}/execute")
async def execute_shuffle_workflow(workflow_id: str, payload: Optional[Dict[str, Any]] = None):
    """Execute Shuffle workflow."""
    clients = get_integration_clients()
    if not clients["shuffle"]:
        raise HTTPException(status_code=503, detail="Shuffle not configured")

    try:
        execution_id = clients["shuffle"].execute_workflow(workflow_id, payload)
        if not execution_id:
            raise HTTPException(status_code=500, detail="Failed to execute workflow")

        await broadcast_update({
            "type": "workflow_started",
            "workflow_id": workflow_id,
            "execution_id": execution_id
        })

        return {"execution_id": execution_id, "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/shuffle/executions")
async def list_shuffle_executions(limit: int = 50):
    """List Shuffle workflow executions."""
    clients = get_integration_clients()
    if not clients["shuffle"]:
        raise HTTPException(status_code=503, detail="Shuffle not configured")

    try:
        executions = clients["shuffle"].list_executions(limit=limit)
        return {"executions": executions, "count": len(executions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Cortex Endpoints

@app.post("/api/cortex/enrich")
async def enrich_observable(data: str, data_type: str):
    """Enrich observable with Cortex threat intelligence."""
    clients = get_integration_clients()
    if not clients["cortex"]:
        raise HTTPException(status_code=503, detail="Cortex not configured")

    try:
        observable_type = ObservableDataType(data_type.lower())

        if observable_type == ObservableDataType.IP:
            result = clients["cortex"].enrich_ip(data)
        elif observable_type == ObservableDataType.DOMAIN:
            result = clients["cortex"].enrich_domain(data)
        elif observable_type == ObservableDataType.HASH:
            result = clients["cortex"].enrich_hash(data)
        elif observable_type == ObservableDataType.URL:
            result = clients["cortex"].enrich_url(data)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported data type: {data_type}")

        # Extract taxonomy/reputation
        taxonomy = clients["cortex"].extract_taxonomy(result) if result else {}

        return {
            "observable": data,
            "data_type": data_type,
            "enrichment": result,
            "reputation": taxonomy
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cortex/analyzers")
async def list_cortex_analyzers():
    """List available Cortex analyzers."""
    clients = get_integration_clients()
    if not clients["cortex"]:
        raise HTTPException(status_code=503, detail="Cortex not configured")

    try:
        analyzers = clients["cortex"].list_analyzers()
        return {"analyzers": analyzers, "count": len(analyzers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Scanning & Findings Endpoints

@app.post("/api/scans/start")
async def start_scan(scan_request: ScanRequest):
    """Start a new security scan."""
    clients = get_integration_clients()

    # Send scan start event to Wazuh
    if clients["wazuh"]:
        scan_id = f"scan-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        clients["wazuh"].send_scan_start_event(
            scan_id=scan_id,
            target=scan_request.target,
            scan_type=scan_request.scan_type
        )

    # Start scan (integrate with existing scanning manager)
    await broadcast_update({
        "type": "scan_started",
        "target": scan_request.target,
        "scan_type": scan_request.scan_type
    })

    return {
        "scan_id": scan_id,
        "status": "started",
        "target": scan_request.target
    }


@app.get("/api/findings/recent")
async def get_recent_findings(limit: int = 50):
    """Get recent security findings."""
    # Integrate with reporting manager or database
    # For now, return placeholder
    return {
        "findings": [],
        "count": 0
    }


# WebSocket for Real-Time Updates

@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates."""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Send periodic updates
            data = await websocket.receive_text()

            # Handle client messages if needed
            if data == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("WebSocket client disconnected")


# Integrated Workflow Endpoints

@app.post("/api/workflow/finding-to-case")
async def finding_to_case_workflow(finding: Dict[str, Any]):
    """
    Complete workflow: Finding → Cortex Enrichment → TheHive Case → Shuffle Playbook
    """
    clients = get_integration_clients()
    workflow_result = {
        "finding": finding,
        "enrichment": None,
        "case_id": None,
        "playbook_execution_id": None
    }

    # Step 1: Enrich with Cortex
    if clients["cortex"]:
        try:
            enrichment = clients["cortex"].enrich_finding(finding)
            workflow_result["enrichment"] = enrichment
        except Exception as e:
            logger.error(f"Cortex enrichment failed: {e}")

    # Step 2: Create TheHive case
    if clients["thehive"]:
        try:
            case_id = clients["thehive"].create_case_from_finding(finding)
            workflow_result["case_id"] = case_id
        except Exception as e:
            logger.error(f"TheHive case creation failed: {e}")

    # Step 3: Trigger Shuffle incident response playbook
    if clients["shuffle"] and finding.get("severity") in ["CRITICAL", "HIGH"]:
        try:
            execution_id = clients["shuffle"].trigger_incident_response_playbook(finding)
            workflow_result["playbook_execution_id"] = execution_id
        except Exception as e:
            logger.error(f"Shuffle playbook trigger failed: {e}")

    # Step 4: Send to Wazuh
    if clients["wazuh"]:
        try:
            clients["wazuh"].send_finding_event(finding)
        except Exception as e:
            logger.error(f"Wazuh event failed: {e}")

    # Broadcast update
    await broadcast_update({
        "type": "finding_processed",
        "finding": finding.get("name"),
        "case_id": workflow_result["case_id"]
    })

    return workflow_result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
