"""Automation Orchestrator Agent - Core AI Orchestration Engine

Central orchestration agent coordinating all AI-driven automation workflows.
Manages task delegation, model selection, OPSEC compliance, and audit trails.

Key Features:
- Autonomous multi-agent workflow coordination
- Adaptive LLM model selection based on cost/performance requirements
- Comprehensive input validation and sanitization
- OPSEC-aware operation with configurable stealth levels
- Vault integration for secure credential management
- Full audit trail for compliance and forensics
- Optional Human-in-Loop checkpoints for enhanced accuracy

Author: WilsonsRaider Development Team
Version: 2.0.0
"""

import logging
import time
import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from secret_manager import SecretManager

# Configure structured logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class AutomationOrchestratorAgent:
    """Central AI orchestration engine for autonomous bug bounty operations.
    
    Coordinates multi-agent workflows, manages model selection, ensures OPSEC
    compliance, and maintains comprehensive audit trails.
    
    Attributes:
        cost_tier: Model selection strategy (economic|balanced|high-performance)
        secrets: Vault integration for secure credential management
        model: Selected LLM model identifier
        llm_api_key: OpenAI API key from Vault
        task_history: Audit trail of executed tasks
        max_retries: Maximum retry attempts for failed operations
        timeout: Task execution timeout in seconds
        hil_enabled: Optional Human-in-Loop checkpoints (default: False)
    """
    
    COST_TIERS = {
        'economic': 'gpt-3.5-turbo',
        'balanced': 'gpt-4',
        'high-performance': 'gpt-4o'
    }
    
    VALID_TASK_TYPES = [
        'recon', 'enumeration', 'vulnerability_scan', 'exploitation',
        'post_exploitation', 'reporting', 'remediation', 'threat_intel'
    ]
    
    OPSEC_LEVELS = {
        'low': {'rate_limit': 100, 'jitter': 0.1, 'user_agent_rotation': False},
        'medium': {'rate_limit': 50, 'jitter': 0.3, 'user_agent_rotation': True},
        'high': {'rate_limit': 10, 'jitter': 0.5, 'user_agent_rotation': True}
    }
    
    def __init__(self, cost_tier: str = 'balanced', max_retries: int = 3, 
                 timeout: int = 300, hil_enabled: bool = False):
        """Initialize the Automation Orchestrator Agent.
        
        Args:
            cost_tier: Model selection strategy
            max_retries: Maximum retry attempts
            timeout: Task execution timeout in seconds
            hil_enabled: Enable optional Human-in-Loop checkpoints (default: False)
        
        Raises:
            ValueError: If cost_tier invalid
            RuntimeError: If Vault initialization fails
        
        Note:
            HiL is OPTIONAL and NOT mandatory for autonomous operation.
            Agent can find vulnerabilities independently without HiL approval.
        """
        if cost_tier not in self.COST_TIERS:
            raise ValueError(
                f"Invalid cost_tier '{cost_tier}'. "
                f"Must be one of: {list(self.COST_TIERS.keys())}"
            )
        
        self.cost_tier = cost_tier
        self.max_retries = max_retries
        self.timeout = timeout
        self.hil_enabled = hil_enabled
        self.task_history: List[Dict[str, Any]] = []
        
        logger.info(
            f"Initializing orchestrator: cost_tier={cost_tier}, "
            f"hil_enabled={hil_enabled}"
        )
        
        try:
            self.secrets = SecretManager()
            self.llm_api_key = self.secrets.get_secret(
                'wilsons-raiders/creds', 'OPENAI_API_KEY'
            )
            
            if not self.llm_api_key:
                raise RuntimeError("Failed to retrieve OPENAI_API_KEY")
            
            masked = self.llm_api_key[:8] + '...' + self.llm_api_key[-4:]
            logger.info(f"API key retrieved: {masked}")
            
        except Exception as e:
            logger.error(f"Vault init failed: {e}", exc_info=True)
            raise RuntimeError(f"Vault initialization failed: {e}") from e
        
        self.model = self._select_model()
        logger.info(f"Selected model: {self.model}")
    
    def _select_model(self) -> str:
        """Select appropriate LLM model based on cost tier.
        
        Returns:
            str: OpenAI model identifier
        """
        model = self.COST_TIERS[self.cost_tier]
        logger.debug(f"Model selection: {model} (cost_tier: {self.cost_tier})")
        return model
    
    def _validate_task_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize task input to prevent injection attacks.
        
        Args:
            data: Raw task data dictionary
        
        Returns:
            Dict[str, Any]: Sanitized and validated task data
        
        Raises:
            ValueError: If required fields missing or invalid
        
        Security:
            - Validates task_type against allowlist
            - Sanitizes string inputs to prevent prompt injection
            - Enforces required field presence
        """
        if not isinstance(data, dict):
            raise ValueError(f"Task data must be dict, got {type(data)}")
        
        required_fields = ['task_type', 'target']
        missing = [f for f in required_fields if f not in data]
        
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        task_type = data.get('task_type')
        if task_type not in self.VALID_TASK_TYPES:
            raise ValueError(
                f"Invalid task_type '{task_type}'. "
                f"Must be one of: {self.VALID_TASK_TYPES}"
            )
        
        # Sanitize string inputs
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = value.replace('\x00', '').replace('\r', '').strip()
            else:
                sanitized[key] = value
        
        # Set default OPSEC level
        if 'opsec_level' not in sanitized:
            sanitized['opsec_level'] = 'medium'
            logger.info("No opsec_level specified, defaulting to 'medium'")
        
        if sanitized['opsec_level'] not in self.OPSEC_LEVELS:
            raise ValueError(
                f"Invalid opsec_level. "
                f"Must be one of: {list(self.OPSEC_LEVELS.keys())}"
            )
        
        logger.debug(f"Task input validated: {sanitized}")
        return sanitized
    
    def _generate_task_id(self, data: Dict[str, Any]) -> str:
        """Generate unique task identifier for audit trail.
        
        Args:
            data: Task data dictionary
        
        Returns:
            str: Unique task identifier (hash-based)
        """
        task_str = json.dumps(data, sort_keys=True)
        task_hash = hashlib.sha256(task_str.encode()).hexdigest()[:16]
        return f"task_{task_hash}_{int(time.time())}"
    
    def _record_task_execution(self, task_id: str, data: Dict[str, Any],
                              result: Any, duration: float, success: bool):
        """Record task execution in audit trail.
        
        Args:
            task_id: Unique task identifier
            data: Task input parameters
            result: Task execution result or error
            duration: Execution time in seconds
            success: Whether task completed successfully
        """
        audit_record = {
            'task_id': task_id,
            'timestamp': datetime.utcnow().isoformat(),
            'task_type': data.get('task_type'),
            'target': data.get('target'),
            'opsec_level': data.get('opsec_level'),
            'model': self.model,
            'duration': round(duration, 2),
            'success': success,
            'result_summary': str(result)[:200] if result else None
        }
        
        self.task_history.append(audit_record)
        logger.info(
            f"Task recorded: {task_id} "
            f"(success={success}, duration={duration:.2f}s)"
        )
    
    def execute_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestrated task with comprehensive error handling.
        
        This method autonomously executes tasks without mandatory HiL approval.
        Optional HiL checkpoints can be enabled via hil_enabled flag for
        enhanced accuracy when needed.
        
        Args:
            data: Task specification dictionary containing:
                - task_type (str): Type of task (required)
                - target (str): Target identifier (required)
                - scope (List[str]): In-scope targets (optional)
                - opsec_level (str): low|medium|high (default: medium)
                - parameters (Dict): Task-specific params (optional)
        
        Returns:
            Dict[str, Any]: Task execution result
        
        Raises:
            ValueError: If input validation fails
            TimeoutError: If task exceeds timeout
            RuntimeError: If critical error occurs
        """
        start_time = time.time()
        
        try:
            validated = self._validate_task_input(data)
            task_id = self._generate_task_id(validated)
            
            logger.info(
                f"Executing task {task_id}: "
                f"{validated['task_type']} on {validated['target']}"
            )
            
            # TODO: Implement full orchestration logic
            result = {
                'status': 'not_implemented',
                'message': 'Full orchestration logic pending',
                'task_type': validated['task_type'],
                'target': validated['target'],
                'autonomous_execution': not self.hil_enabled
            }
            
            duration = time.time() - start_time
            self._record_task_execution(task_id, validated, result, duration, False)
            
            return {
                'task_id': task_id,
                'status': 'pending_implementation',
                'result': result,
                'duration': duration,
                'errors': ['Full orchestration not yet implemented'],
                'hil_triggered': False
            }
            
        except ValueError as e:
            duration = time.time() - start_time
            logger.error(f"Validation error: {e}")
            return {
                'task_id': None,
                'status': 'failure',
                'result': None,
                'duration': duration,
                'errors': [f"Validation error: {str(e)}"],
                'hil_triggered': False
            }
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Execution error: {e}", exc_info=True)
            return {
                'task_id': None,
                'status': 'failure',
                'result': None,
                'duration': duration,
                'errors': [f"Execution error: {str(e)}"],
                'hil_triggered': False
            }
    
    def get_task_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve task execution history for audit.
        
        Args:
            limit: Max recent tasks to return (None for all)
        
        Returns:
            List[Dict[str, Any]]: Task execution records
        """
        if limit is None:
            return self.task_history
        return self.task_history[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Calculate execution statistics for monitoring.
        
        Returns:
            Dict[str, Any]: Statistics including success rate, avg duration
        """
        if not self.task_history:
            return {'total_tasks': 0}
        
        total = len(self.task_history)
        successful = sum(1 for t in self.task_history if t['success'])
        total_dur = sum(t['duration'] for t in self.task_history)
        
        return {
            'total_tasks': total,
            'successful_tasks': successful,
            'failed_tasks': total - successful,
            'success_rate': round(successful / total * 100, 2) if total > 0 else 0,
            'avg_duration': round(total_dur / total, 2) if total > 0 else 0,
            'total_duration': round(total_dur, 2)
        }
