import time
import asyncio
from collections import deque
from ..ui import UIManager
from ..cloud.cloud_manager import CloudManager

class JobManager:
    """Manages a queue of scanning jobs and distributes them to cloud nodes."""

    def __init__(self, config: dict, ui_manager: UIManager, cloud_manager: CloudManager):
        self.ui = ui_manager
        self.config = config
        self.cloud_manager = cloud_manager
        self.job_queue = deque()
        self.active_nodes = {}
        self.max_nodes = config.get('cloud', {}).get('max_concurrent_jobs', 6)

    def add_job(self, target: str):
        """Adds a new target to the job queue."""
        job = {'target': target, 'status': 'queued'}
        self.job_queue.append(job)
        self.ui.print(f"[+] Job added for target: {target}. Queue size: {len(self.job_queue)}")

    async def process_queue(self):
        """The main loop to process jobs and manage the node fleet."""
        self.ui.run_subheading("Job Manager Initialized - Processing Queue")
        while self.job_queue:
            self._update_node_status()

            # Provision new nodes if we are below capacity and there are jobs
            if len(self.active_nodes) < self.max_nodes and self.job_queue:
                self.ui.print(f"  -> Fleet below capacity ({len(self.active_nodes)}/{self.max_nodes}). Provisioning new node...")
                new_node = self.cloud_manager.provision_node()
                if new_node:
                    self.active_nodes[new_node['id']] = {'node_info': new_node, 'status': 'idle', 'job': None}
            
            # Assign jobs to idle nodes
            for node_id, node_data in self.active_nodes.items():
                if node_data['status'] == 'idle' and self.job_queue:
                    job_to_run = self.job_queue.popleft()
                    job_to_run['status'] = 'running'
                    node_data['status'] = 'busy'
                    node_data['job'] = job_to_run
                    self.ui.print(f"[green]  -> Assigning job for '{job_to_run['target']}' to node {node_id} ({node_data['node_info']['ip_address']})[/green]")
                    # In a real system, this would trigger the scan on the remote node
                    asyncio.create_task(self._simulate_scan(node_id, job_to_run))

            await asyncio.sleep(5) # Wait before checking the queue again
        
        self.ui.print("[bold green]Job queue is empty. Shutting down nodes...[/bold green]")
        await self._cleanup_nodes()

    def _update_node_status(self):
        """(Placeholder) Checks the status of running jobs on nodes."""
        # In a real system, this would poll nodes for job completion.
        pass

    async def _simulate_scan(self, node_id: str, job: dict):
        """(Placeholder) Simulates a scan running on a remote node."""
        self.ui.print(f"    -> Scan for {job['target']} started on node {node_id}.")
        await asyncio.sleep(15) # Simulate scan time
        self.ui.print(f"    -> Scan for {job['target']} finished on node {node_id}.")
        # Mark the node as idle so it can pick up a new job
        if node_id in self.active_nodes:
            self.active_nodes[node_id]['status'] = 'idle'
            self.active_nodes[node_id]['job'] = None

    async def _cleanup_nodes(self):
        """Destroys all active cloud nodes."""
        for node_id in list(self.active_nodes.keys()):
            self.cloud_manager.destroy_node(node_id)
            del self.active_nodes[node_id]

