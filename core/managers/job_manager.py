<<<<<<< HEAD
=======
"""Job Manager - Distributed Task Orchestration and Cloud Fleet Management

Manages job queuing, distribution, and cloud node orchestration.
Version: 2.0.0
"""

import time
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4
import asyncio
import logging
from collections import deque
<<<<<<< HEAD
from core import ui

class JobManager:
    """Manages a queue of jobs and distributes them to a heterogeneous fleet of nodes."""

    def __init__(self, node_managers: list):
        self.ui = ui
        self.node_managers = node_managers
        self.job_queue = deque()
        self.active_jobs = {}
        ui.print_info(f"JobManager initialized with {len(node_managers)} node manager(s).")

    def add_job(self, job_details: dict):
        """Adds a new job to the queue."""
        job = {**job_details, 'status': 'queued'}
        self.job_queue.append(job)
        self.ui.print_info(f"Job added for target: {job.get('target')}. Queue size: {len(self.job_queue)}")

    async def process_queue(self):
        """The main loop to process jobs and distribute them to available nodes."""
        self.ui.print_subheader("Job Manager starting... Processing queue.")
        while self.job_queue:
            idle_nodes = []
            # Gather all available nodes from all managers
            for manager in self.node_managers:
                available_nodes = await manager.get_available_nodes()
                for node in available_nodes:
                    if node['id'] not in self.active_jobs:
                        node['manager'] = manager  # Tag node with its manager
                        idle_nodes.append(node)

            if not idle_nodes:
                await asyncio.sleep(10)
                continue

            # Assign jobs to idle nodes
            while self.job_queue and idle_nodes:
                job_to_run = self.job_queue.popleft()
                node_to_use = idle_nodes.pop(0)
                
                node_id = node_to_use['id']
                manager = node_to_use['manager']

                self.active_jobs[node_id] = job_to_run
                self.ui.print_success(f"Assigning job for '{job_to_run.get('target')}' to node '{node_id}'")
                
                # Run the job in the background
                asyncio.create_task(self._run_job_and_handle_completion(manager, node_id, job_to_run))

            await asyncio.sleep(5)
        
        self.ui.print_info("Job queue is empty. Active jobs will complete in the background.")

    async def _run_job_and_handle_completion(self, manager, node_id, job):
        """A wrapper to execute a job and manage its lifecycle."""
        result = await manager.execute_job_on_node(node_id, job)
        
        if result.get('status') == 'success':
            self.ui.print_success(f"Job for '{job.get('target')}' on node '{node_id}' completed.")
            # TODO: Add logic to process successful job results (result['stdout'])
        else:
            self.ui.print_error(f"Job for '{job.get('target')}' on node '{node_id}' failed: {result.get('stderr')}")
            # TODO: Add logic to handle failed jobs (e.g., re-queue)
            
        # Mark node as idle by removing the job
        if node_id in self.active_jobs:
            del self.active_jobs[node_id]

=======
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class Job:
    """Represents a single scanning/testing job."""
    def __init__(self, target: str, job_type: str = "scan", priority: JobPriority = JobPriority.NORMAL):
        self.id = f"{job_type}_{target}_{int(time.time())}"
        self.target = target
        self.job_type = job_type
        self.priority = priority
        self.status = JobStatus.QUEUED
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.retry_count = 0
        self.max_retries = 3
        self.result = None
        self.error = None

class JobManager:
    """Manages distributed job execution across cloud nodes."""
    
    def __init__(self, config: dict, ui_manager=None, cloud_manager=None, state_manager=None):
        self.ui = ui_manager
        self.config = config
        self.cloud_manager = cloud_manager
        self.state_manager = state_manager
        self.job_queue = deque()
        self.active_jobs = {}
        self.completed_jobs = []
        self.active_nodes = {}
        self.max_nodes = config.get('cloud', {}).get('max_concurrent_jobs', 6)
        self.job_timeout = config.get('cloud', {}).get('job_timeout', 300)
        logger.info(f"JobManager initialized: max_nodes={self.max_nodes}, timeout={self.job_timeout}s")
    
    def add_job(self, target: str, job_type: str = "scan", priority: JobPriority = JobPriority.NORMAL) -> Job:
        """Add new job to queue."""
        job = Job(target, job_type, priority)
        self.job_queue.append(job)
        logger.info(f"Job added: {job.id} (priority={priority.name}, queue_size={len(self.job_queue)})")
        if self.ui:
            self.ui.print(f"[+] Job queued: {target} (priority: {priority.name})")
        return job
    
    def _sort_queue_by_priority(self):
        """Sort job queue by priority."""
        self.job_queue = deque(sorted(self.job_queue, key=lambda j: j.priority.value, reverse=True))
    
    async def process_queue(self):
        """Main loop to process jobs and manage node fleet."""
        logger.info("Starting job queue processing")
        if self.ui:
            self.ui.run_subheading("Job Manager - Processing Queue")
        
        try:
            while self.job_queue or self.active_jobs:
                await self._update_node_status()
                self._sort_queue_by_priority()
                
                # Provision nodes if below capacity and jobs waiting
                if len(self.active_nodes) < self.max_nodes and self.job_queue:
                    await self._provision_node()
                
                # Assign jobs to idle nodes
                await self._assign_jobs_to_nodes()
                
                # Check for timeouts
                await self._check_job_timeouts()
                
                await asyncio.sleep(2)
            
            logger.info("Queue empty, shutting down nodes")
            if self.ui:
                self.ui.print("[bold green]All jobs completed. Cleaning up...[/bold green]")
            await self._cleanup_nodes()
        
        except Exception as e:
            logger.error(f"Queue processing error: {e}")
            await self._cleanup_nodes()
            raise
    
    async def _provision_node(self):
        """Provision new cloud node."""
        try:
            if self.ui:
                self.ui.print(f"  -> Provisioning node ({len(self.active_nodes)}/{self.max_nodes})...")
            
            if self.cloud_manager:
                new_node = self.cloud_manager.provision_node()
                if new_node:
                    self.active_nodes[new_node['id']] = {
                        'node_info': new_node,
                        'status': 'idle',
                        'job': None,
                        'provisioned_at': datetime.utcnow()
                    }
                    logger.info(f"Node provisioned: {new_node['id']}")
        except Exception as e:
            logger.error(f"Node provisioning failed: {e}")
    
    async def _assign_jobs_to_nodes(self):
        """Assign queued jobs to idle nodes."""
        for node_id, node_data in list(self.active_nodes.items()):
            if node_data['status'] == 'idle' and self.job_queue:
                job = self.job_queue.popleft()
                job.status = JobStatus.RUNNING
                job.started_at = datetime.utcnow()
                
                node_data['status'] = 'busy'
                node_data['job'] = job
                self.active_jobs[job.id] = {'job': job, 'node_id': node_id}
                
                if self.ui:
                    self.ui.print(f"[green]  -> Assigned {job.target} to node {node_id}[/green]")
                
                asyncio.create_task(self._execute_job(node_id, job))
    
    async def _execute_job(self, node_id: str, job: Job):
        """Execute job on remote node."""
        try:
            logger.info(f"Executing job {job.id} on node {node_id}")
            if self.ui:
                self.ui.print(f"    -> Starting {job.job_type} for {job.target} on {node_id}")
            
            # Simulate job execution (replace with actual remote execution)
            await asyncio.sleep(15)
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.result = {'status': 'success', 'node': node_id}
            
            logger.info(f"Job completed: {job.id}")
            if self.ui:
                self.ui.print(f"    -> Completed {job.target} on {node_id}")
        
        except Exception as e:
            logger.error(f"Job execution failed: {job.id} - {e}")
            job.status = JobStatus.FAILED
            job.error = str(e)
            
            # Retry logic
            if job.retry_count < job.max_retries:
                job.retry_count += 1
                job.status = JobStatus.QUEUED
                self.job_queue.append(job)
                logger.info(f"Job requeued for retry {job.retry_count}/{job.max_retries}")
        
        finally:
            # Mark node as idle
            if node_id in self.active_nodes:
                self.active_nodes[node_id]['status'] = 'idle'
                self.active_nodes[node_id]['job'] = None
            
            # Move to completed
            if job.id in self.active_jobs:
                del self.active_jobs[job.id]
            self.completed_jobs.append(job)
    
    async def _check_job_timeouts(self):
        """Check for and handle timed-out jobs."""
        now = datetime.utcnow()
        for job_id, job_data in list(self.active_jobs.items()):
            job = job_data['job']
            if job.started_at:
                elapsed = (now - job.started_at).total_seconds()
                if elapsed > self.job_timeout:
                    logger.warning(f"Job timeout: {job_id} ({elapsed}s)")
                    job.status = JobStatus.FAILED
                    job.error = f"Timeout after {elapsed}s"
                    
                    # Release node
                    node_id = job_data['node_id']
                    if node_id in self.active_nodes:
                        self.active_nodes[node_id]['status'] = 'idle'
                        self.active_nodes[node_id]['job'] = None
                    
                    del self.active_jobs[job_id]
                    self.completed_jobs.append(job)
    
    async def _update_node_status(self):
        """Check status of active nodes."""
        # Placeholder for actual node health checks
        pass
    
    async def _cleanup_nodes(self):
        """Destroy all active cloud nodes."""
        logger.info(f"Cleaning up {len(self.active_nodes)} nodes")
        for node_id in list(self.active_nodes.keys()):
            try:
                if self.cloud_manager:
                    self.cloud_manager.destroy_node(node_id)
                del self.active_nodes[node_id]
                logger.info(f"Node destroyed: {node_id}")
            except Exception as e:
                logger.error(f"Failed to destroy node {node_id}: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get job execution metrics."""
        completed = [j for j in self.completed_jobs if j.status == JobStatus.COMPLETED]
        failed = [j for j in self.completed_jobs if j.status == JobStatus.FAILED]
        
        return {
            'total_jobs': len(self.completed_jobs),
            'completed': len(completed),
            'failed': len(failed),
            'active': len(self.active_jobs),
            'queued': len(self.job_queue),
            'active_nodes': len(self.active_nodes)
        }
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4
